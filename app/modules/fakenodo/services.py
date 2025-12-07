
from __future__ import annotations

import json
import os
import random
import threading
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4
from venv import logger

from flask import Response, jsonify

from app.modules.dataset.models import DatasetVersion
from app.modules.fakenodo.models import Fakenodo
from app.modules.fakenodo.repositories import FakenodoRepository
from core.services.BaseService import BaseService


class FakenodoService(BaseService):
    def __init__(self):
        super().__init__(None)
        self.repository = FakenodoRepository()

    def list_depositions(self) -> List[Dict]:
        """Return all depositions from DB as dicts."""
        depositions = Fakenodo.query.all()
        result: List[Dict] = []
        for d in depositions:
            result.append({
                "id": d.id,
                "metadata": d.meta_data or {},
                "status": d.status,
                "doi": d.doi,
            })
        return result

    def get_deposition(self, deposition_id: int) -> Optional[Dict]:
        """Get a single deposition from DB as dict."""
        try:
            d = self.repository.get_deposition(deposition_id)
            return {
                "id": d.id,
                "metadata": d.meta_data or {},
                "status": d.status,
                "doi": d.doi,
            }
        except Exception:
            logger.exception("FakenodoService: deposition not found: %s", deposition_id)
            return None

    def upload_file(self, dataset, deposition_id: int, fits_model) -> dict:
        """Persist a file record into deposition meta_data.files in DB."""
        file_name = None
        file_path = None
        try:
            if hasattr(fits_model, "files") and fits_model.files:
                hf = fits_model.files[0]
                file_name = getattr(hf, "name", None)
                file_path = getattr(hf, "path", None)
            if not file_name and hasattr(fits_model, "fm_meta_data") and getattr(fits_model.fm_meta_data, "csv_filename", None):
                file_name = fits_model.fm_meta_data.csv_filename
                file_path = getattr(getattr(dataset, "working_path", None), "path", None)
        except Exception:
            logger.exception("FakenodoService: error extracting file info from model")

        file_name = file_name or "unknown.csv"
        file_path = file_path or ""

        logger.info(f"FakenodoService: attaching file '{file_name}' to deposition '{deposition_id}'")
        meta = self.repository.add_csv_file(deposition_id=deposition_id, file_name=file_name, file_path=file_path)
        return {"status": "completed", "meta_data": meta}

    def publish_deposition(self, deposition_id: int) -> dict:
        """Mark deposition as published and assign DOI in DB."""
        dep = self.repository.get_deposition(deposition_id)
        if not dep:
            raise Exception("Deposition not found")
        dep.status = "published"
        dep.doi = f"10.5281/fakenodo.{random.randint(1000000, 9999999)}"
        from app import db
        db.session.add(dep)
        db.session.commit()
        logger.info("FakenodoService: published deposition %s with DOI %s", deposition_id, dep.doi)
        try:
            meta = dep.meta_data or {}
            label = meta.get("dataset_version") or "1.0"
            self.repository.add_version(
                deposition_id=deposition_id,
                version_label=label,
                doi=dep.doi,
                changes={
                    "metadata_changed": False,
                    "file_changed": True,
                    "comment": "Published deposition",
                },
            )
        except Exception:
            logger.exception("FakenodoService: could not append version on publish for deposition %s", deposition_id)
        return {"state": "done", "submitted": True, "doi": dep.doi}

    def list_versions(self, deposition_id: int) -> Optional[List[Dict]]:
        """Return version history for a deposition, preferring DatasetVersion records.

        Fallback to versions stored in meta_data if no dataset link exists.
        """
        try:
            dep = self.repository.get_deposition(deposition_id)
        except Exception:
            logger.warning("FakenodoService: deposition not found for list_versions: %s", deposition_id)
            return []
        
        if not dep:
            return []
        meta = dep.meta_data or {}

        dataset_id = meta.get("dataset_id")
        out: List[Dict] = []
        try:
            if dataset_id:
                qs = (
                    DatasetVersion.query
                    .filter_by(dataset_id=dataset_id)
                    .order_by(DatasetVersion.version_major.asc(), DatasetVersion.version_minor.asc())
                    .all()
                )
                for dv in qs:
                    label = f"{dv.version_major}.{dv.version_minor}"
                    created = getattr(dv, 'created_at', None)
                    out.append({
                        "version": label,
                        "doi": dep.doi,
                        "created_at": created.isoformat() + 'Z' if created else None,
                        "changes": None,
                    })
        except Exception:
            logger.exception("FakenodoService: error listing dataset versions for dataset_id=%s", dataset_id)

        if not out:
            versions = meta.get("versions", [])
            if isinstance(versions, list):
                return versions
            return []

        return out

    def create_new_deposition(self, dataset) -> dict:
        """Create a new deposition row in DB and return an API-like dict."""
        title = getattr(getattr(dataset, "ds_meta_data", None), "title", None)
        description = getattr(getattr(dataset, "ds_meta_data", None), "description", None)
        tags = getattr(getattr(dataset, "ds_meta_data", None), "tags", None)
        current_version_label = None
        try:
            dv = (
                DatasetVersion.query.filter_by(dataset_id=dataset.id)
                .order_by(DatasetVersion.version_major.desc(), DatasetVersion.version_minor.desc())
                .first()
            )
            if dv:
                current_version_label = f"{dv.version_major}.{dv.version_minor}"
        except Exception:
            current_version_label = None
        meta = {
            "title": title,
            "description": description,
            "tags": tags,
            "dataset_version": current_version_label,
            "dataset_id": getattr(dataset, "id", None),
        }

        dep = self.repository.create_new_deposition(meta_data=meta)
        logger.info("FakenodoService: created deposition in DB id=%s", dep.id)
        return {
            "id": dep.id,
            "metadata": {},
            "links": {"bucket": f"/api/files/{dep.id}"},
        }

    def get_doi(self, deposition_id: int) -> str:
        """Return stored DOI from DB."""
        dep = self.repository.get_deposition(deposition_id)
        if not dep:
            raise Exception("Deposition not found")
        return dep.doi or ""

    def get_by_doi(self, doi: str) -> Optional[Dict]:
        """Return a deposition dict looked up by DOI."""
        dep = self.repository.get_by_doi(doi)
        if not dep:
            return None
        return {
            "id": dep.id,
            "metadata": dep.meta_data or {},
            "status": dep.status,
            "doi": dep.doi,
        }

    def append_version(self, deposition_id: int, version_major: int, version_minor: int, doi: Optional[str] = None) -> dict:
        """Append a version entry to the deposition meta_data in DB."""
        label = f"{version_major}.{version_minor}"
        return self.repository.add_version(deposition_id=deposition_id, version_label=label, doi=doi)

    def set_dataset_version(self, deposition_id: int, version_major: int, version_minor: int, append_to_versions: bool = True) -> dict:
        """Update the deposition's dataset_version.
        
        If append_to_versions is True (default), also adds an entry to the versions list
        with the previous DOI (since no new DOI is generated for metadata-only changes).
        """
        label = f"{version_major}.{version_minor}"
        result = self.repository.update_dataset_version(deposition_id=deposition_id, version_label=label)
        
        if append_to_versions:
            dep = self.repository.get_deposition(deposition_id)
            current_doi = dep.doi if dep else None
            self.repository.add_version(deposition_id=deposition_id, version_label=label, doi=current_doi)
            logger.info("FakenodoService: appended version %s to deposition %s (metadata-only, DOI unchanged)", label, deposition_id)
        
        return result
    
    def create_deposition(self, metadata: Optional[Dict] = None) -> Dict:
        """Create a new deposition from raw metadata dict (API-style).

        This is used by the HTTP endpoint POST /fakenodo/deposit/depositions.
        Unlike create_new_deposition which takes a dataset object, this one
        accepts a plain metadata dict.
        """
        meta = metadata or {}
        dep = self.repository.create_new_deposition(meta_data=meta)
        logger.info("FakenodoService: created deposition via API, id=%s", dep.id)
        return {
            "id": dep.id,
            "metadata": dep.meta_data or {},
            "status": dep.status,
            "doi": dep.doi,
            "links": {"bucket": f"/api/files/{dep.id}"},
        }

    def update_metadata(self, deposition_id: int, metadata: Dict) -> Optional[Dict]:
        """Update only metadata of a deposition without generating a new DOI.

        This respects the basic Zenodo logic:
        - Edit metadata only → no new DOI (dirty flag set to True).
        - Files must be changed and published to get a new DOI/version.
        """
        try:
            updated = self.repository.update_metadata(deposition_id, metadata)
            return updated
        except Exception:
            logger.exception("FakenodoService: error updating metadata for deposition %s", deposition_id)
            return None

    def delete_deposition(self, deposition_id: int) -> bool:
        """Delete a deposition from the database."""
        return self.repository.delete_deposition(deposition_id)

    def test_full_connection(self) -> Response:
        """
        Simulate testing connection with FakeNodo.
        """
        logger.info("Simulating connection to FakeNodo...")
        return jsonify({"success": True, "message": "FakeNodo connection test successful."})
