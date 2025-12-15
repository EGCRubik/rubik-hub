
from __future__ import annotations

import random
from datetime import datetime
from typing import Dict, List, Optional

from flask import Response, jsonify
from sqlalchemy.orm.attributes import flag_modified

from app import db
from app.modules.dataset.models import DatasetVersion
from app.modules.fakenodo.models import Fakenodo
from core.services.BaseService import BaseService


class FakenodoService(BaseService):

    def __init__(self):
        super().__init__(None)

    def get_deposition_obj(self, deposition_id: int) -> Fakenodo | None:
        return Fakenodo.query.get(deposition_id)

    def list_depositions(self) -> List[Dict]:
        return [{"id": d.id, "metadata": d.meta_data or {}, "status": d.status, "doi": d.doi} for d in Fakenodo.query.all()]

    def get_deposition(self, deposition_id: int) -> Optional[Dict]:
        d = self.get_deposition_obj(deposition_id)
        return {"id": d.id, "metadata": d.meta_data or {}, "status": d.status, "doi": d.doi} if d else None

    def upload_file(self, dataset, deposition_id: int, fits_model) -> dict:
        file_name, file_path = None, None
        if hasattr(fits_model, "files") and fits_model.files:
            hf = fits_model.files[0]
            file_name, file_path = getattr(hf, "name", None), getattr(hf, "path", None)
        if not file_name and hasattr(fits_model, "fm_meta_data") and getattr(fits_model.fm_meta_data, "csv_filename", None):
            file_name = fits_model.fm_meta_data.csv_filename
            file_path = getattr(getattr(dataset, "working_path", None), "path", None)
        dep = self.get_deposition_obj(deposition_id)
        meta_data = dep.meta_data or {}
        files = meta_data.get("files", [])
        files.append({"file_name": file_name or "unknown.csv", "file_path": file_path or "", "file_type": "text/csv"})
        meta_data["files"] = files
        dep.meta_data = meta_data
        flag_modified(dep, "meta_data")
        db.session.commit()
        return {"status": "completed", "meta_data": meta_data}

    def publish_deposition(self, deposition_id: int) -> dict:
        dep = self.get_deposition_obj(deposition_id)
        dep.status = "published"
        dep.doi = f"10.5281/fakenodo.{random.randint(1000000, 9999999)}"
        db.session.commit()
        label = (dep.meta_data or {}).get("dataset_version") or "1.0"
        self.add_version(deposition_id, label, dep.doi, {"metadata_changed": False, "file_changed": True, "comment": "Published deposition"})
        return {"state": "done", "submitted": True, "doi": dep.doi}

    def add_version(self, deposition_id: int, version_label: str, doi: str = None, changes: dict = None) -> dict:
        dep = self.get_deposition_obj(deposition_id)
        meta_data = dep.meta_data or {}
        versions = meta_data.get("versions", [])
        entry = {"version": version_label, "doi": doi, "created_at": datetime.utcnow().isoformat() + "Z"}
        if isinstance(changes, dict):
            entry["changes"] = changes
            fields = changes.get("fields") if isinstance(changes.get("fields"), dict) else {}
            for key in ("title", "description", "tags"):
                if key in fields and fields[key] is not None:
                    meta_data[key] = fields[key]
        versions.append(entry)
        meta_data["versions"] = versions
        meta_data["dataset_version"] = version_label
        dep.meta_data = meta_data
        flag_modified(dep, "meta_data")
        db.session.commit()
        return meta_data

    def list_versions(self, deposition_id: int) -> List[Dict]:
        dep = self.get_deposition_obj(deposition_id)
        meta = dep.meta_data or {}
        dataset_id = meta.get("dataset_id")
        out = []
        if dataset_id:
            for dv in DatasetVersion.query.filter_by(dataset_id=dataset_id).order_by(DatasetVersion.version_major.asc(), DatasetVersion.version_minor.asc()):
                label = f"{dv.version_major}.{dv.version_minor}"
                created = getattr(dv, 'created_at', None)
                out.append({"version": label, "doi": dep.doi, "created_at": created.isoformat() + 'Z' if created else None, "changes": None})

        return out or (meta.get("versions", []) if isinstance(meta.get("versions"), list) else [])

    def create_new_deposition(self, dataset) -> dict:
        ds_meta = getattr(dataset, "ds_meta_data", None)
        title, description, tags = getattr(ds_meta, "title", None), getattr(ds_meta, "description", None), getattr(ds_meta, "tags", None)
        current_version_label = None
        dv = DatasetVersion.query.filter_by(dataset_id=dataset.id).order_by(DatasetVersion.version_major.desc(), DatasetVersion.version_minor.desc()).first()
        if dv:
            current_version_label = f"{dv.version_major}.{dv.version_minor}"
        meta = {"title": title, "description": description, "tags": tags, "dataset_version": current_version_label, "dataset_id": getattr(dataset, "id", None)}
        dep = Fakenodo(meta_data=meta, status="draft")
        db.session.add(dep)
        db.session.commit()
        return {"id": dep.id, "metadata": {}, "links": {"bucket": f"/api/files/{dep.id}"}}

    def get_doi(self, deposition_id: int) -> str:
        dep = self.get_deposition_obj(deposition_id)
        return dep.doi or "" if dep else ""

    def get_by_doi(self, doi: str) -> Optional[Dict]:
        dep = Fakenodo.query.filter_by(doi=doi).first()
        return {"id": dep.id, "metadata": dep.meta_data or {}, "status": dep.status, "doi": dep.doi} if dep else None

    def append_version(self, deposition_id: int, version_major: int, version_minor: int, doi: Optional[str] = None) -> dict:
        return self.add_version(deposition_id, f"{version_major}.{version_minor}", doi)

    def set_dataset_version(self, deposition_id: int, version_major: int, version_minor: int, append_to_versions: bool = True) -> dict:
        label = f"{version_major}.{version_minor}"
        dep = self.get_deposition_obj(deposition_id)
        if not dep:
            return {}
        meta_data = dep.meta_data or {}
        meta_data["dataset_version"] = label
        dep.meta_data = meta_data
        flag_modified(dep, "meta_data")
        db.session.commit()
        if append_to_versions:
            self.add_version(deposition_id, label, dep.doi)
        return meta_data

    def create_deposition(self, metadata: Optional[Dict] = None) -> Dict:
        dep = Fakenodo(meta_data=metadata or {}, status="draft")
        db.session.add(dep)
        db.session.commit()
        return {"id": dep.id, "metadata": dep.meta_data or {}, "status": dep.status, "doi": dep.doi, "links": {"bucket": f"/api/files/{dep.id}"}}

    def update_metadata(self, deposition_id: int, metadata: Dict) -> Optional[Dict]:
        dep = self.get_deposition_obj(deposition_id)
        meta_data = dep.meta_data or {}
        for key in ("title", "description", "tags", "publication_type", "publication_doi"):
            if key in metadata:
                meta_data[key] = metadata[key]
        meta_data["dirty"] = True
        dep.meta_data = meta_data
        flag_modified(dep, "meta_data")
        db.session.commit()
        return {"id": dep.id, "metadata": meta_data, "status": dep.status, "doi": dep.doi, "dirty": True, "versions": meta_data.get("versions", [])}

    def delete_deposition(self, deposition_id: int) -> bool:
        dep = self.get_deposition_obj(deposition_id)
        if dep:
            db.session.delete(dep)
            db.session.commit()
            return True
        return False

    def test_full_connection(self) -> Response:
        return jsonify({"success": True, "message": "FakeNodo connection test successful."})
    
    # He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código. 
    # La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.

