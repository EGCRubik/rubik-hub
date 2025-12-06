
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

from app.modules.fakenodo.models import Fakenodo
from app.modules.fakenodo.repositories import FakenodoRepository
from core.services.BaseService import BaseService


class FakenodoService(BaseService):
    def __init__(self):
        super().__init__(None)
        self.repository = FakenodoRepository()

    def list_depositions(self) -> List[Dict]:
        """Return all depositions from DB as dicts."""
        # Simple list conversion; for larger models add schema/serialiser
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
        # Determine file info: for feature_models or file_models
        file_name = None
        file_path = None
        try:
            # file_models: fits_model.files[0].path/name
            if hasattr(fits_model, "files") and fits_model.files:
                hf = fits_model.files[0]
                file_name = getattr(hf, "name", None)
                file_path = getattr(hf, "path", None)
            # feature_models: fm_meta_data.csv_filename or similar
            if not file_name and hasattr(fits_model, "fm_meta_data") and getattr(fits_model.fm_meta_data, "csv_filename", None):
                file_name = fits_model.fm_meta_data.csv_filename
                # best-effort path under uploads
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
        # Assign a fresh fake DOI on every publish to reflect a new version
        # Keep a history inside meta_data.versions; the current dep.doi is the latest
        dep.status = "published"
        dep.doi = f"10.5281/fakenodo.{random.randint(1000000, 9999999)}"
        from app import db
        db.session.add(dep)
        db.session.commit()
        logger.info("FakenodoService: published deposition %s with DOI %s", deposition_id, dep.doi)
        return {"state": "done", "submitted": True, "doi": dep.doi}

    def list_versions(self, deposition_id: int) -> Optional[List[Dict]]:
        """Return versions stored in meta_data (if any)."""
        dep = self.repository.get_deposition(deposition_id)
        if not dep:
            return None
        meta = dep.meta_data or {}
        return meta.get("versions", [])

    def create_new_deposition(self, dataset) -> dict:
        """Create a new deposition row in DB and return an API-like dict."""
        # Build minimal metadata from dataset
        title = getattr(getattr(dataset, "ds_meta_data", None), "title", None)
        description = getattr(getattr(dataset, "ds_meta_data", None), "description", None)
        tags = getattr(getattr(dataset, "ds_meta_data", None), "tags", None)
        meta = {
            "title": title,
            "description": description,
            "tags": tags,
        }
        # Pre-reserve DOI style
        concept_rec_id = random.randint(100000, 999999)
        meta["prereserve_doi"] = {"doi": f"10.5072/fakenodo.{concept_rec_id}"}

        dep = self.repository.create_new_deposition(meta_data=meta)
        logger.info("FakenodoService: created deposition in DB id=%s", dep.id)
        return {
            "conceptrecid": concept_rec_id,
            "id": dep.id,
            "metadata": {"prereserve_doi": {"doi": meta["prereserve_doi"]["doi"]}},
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
    
    def test_full_connection(self) -> Response:
        """
        Simulate testing connection with FakeNodo.
        """
        logger.info("Simulating connection to FakeNodo...")
        return jsonify({"success": True, "message": "FakeNodo connection test successful."})
