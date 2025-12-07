import logging
from datetime import datetime
from venv import logger

from sqlalchemy.orm.attributes import flag_modified

from app import db
from app.modules.fakenodo.models import Fakenodo
from core.repositories.BaseRepository import BaseRepository


class FakenodoRepository:
    """Repository for interacting with the Fakenodo depositions in the database."""

    def create_new_deposition(self, meta_data: dict = None, doi: str = None) -> Fakenodo:
        """
        Create a new deposition entry in the database.
        """
        if meta_data is None:
            meta_data = {}
        deposition = Fakenodo()
        deposition.meta_data = meta_data or {}
        deposition.doi = doi
        if not getattr(deposition, "status", None):
            deposition.status = "draft"
        db.session.add(deposition)
        db.session.commit()

        logger.info(f"FakenodoRepository: Created new deposition with ID {deposition.id}")
        return deposition

    def add_csv_file(self, deposition_id: int, file_name: str, file_path: str) -> dict:
        """
        Attach a CSV file to an existing deposition record.
        """
        deposition = Fakenodo.query.get(deposition_id)
        if not deposition:
            raise Exception(f"Deposition with ID {deposition_id} not found.")

        meta_data = deposition.meta_data or {}
        files = meta_data.get("files", [])
        files.append({
            "file_name": file_name,
            "file_path": file_path,
            "file_type": "text/csv",
        })
        meta_data["files"] = files
        deposition.meta_data = meta_data

        flag_modified(deposition, "meta_data")
        db.session.commit()
        logger.info(f"FakenodoRepository: Added CSV file '{file_name}' to deposition ID {deposition_id}")
        return meta_data

    def add_version(self, deposition_id: int, version_label: str, doi: str | None = None, changes: dict | None = None) -> dict:
        """Append a version entry to the deposition meta_data. Creates list if missing.
        """
        deposition = Fakenodo.query.get(deposition_id)
        if not deposition:
            raise Exception(f"Deposition with ID {deposition_id} not found.")

        meta_data = deposition.meta_data or {}
        versions = meta_data.get("versions", [])
        entry = {
            "version": version_label,
            "doi": doi,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        if isinstance(changes, dict):
            entry["changes"] = changes
            fields = changes.get("fields") if isinstance(changes.get("fields"), dict) else {}
            for key in ("title", "description", "tags"):
                if key in fields and fields[key] is not None:
                    meta_data[key] = fields[key]
        versions.append(entry)
        meta_data["versions"] = versions
        meta_data["dataset_version"] = version_label
        deposition.meta_data = meta_data

        flag_modified(deposition, "meta_data")
        db.session.commit()
        logger.info(f"FakenodoRepository: Added version '{version_label}' to deposition ID {deposition_id}")
        return meta_data

    def update_dataset_version(self, deposition_id: int, version_label: str) -> dict:
        """Update only the dataset_version field in meta_data without adding a new entry to versions."""
        deposition = Fakenodo.query.get(deposition_id)
        if not deposition:
            raise Exception(f"Deposition with ID {deposition_id} not found.")

        meta_data = deposition.meta_data or {}
        meta_data["dataset_version"] = version_label
        deposition.meta_data = meta_data

        flag_modified(deposition, "meta_data")
        db.session.commit()
        logger.info(f"FakenodoRepository: Updated dataset_version to '{version_label}' for deposition ID {deposition_id}")
        return meta_data

    def update_metadata(self, deposition_id: int, metadata: dict) -> dict:
        """Update metadata fields of a deposition without generating a new DOI.
        """
        deposition = Fakenodo.query.get(deposition_id)
        if not deposition:
            raise Exception(f"Deposition with ID {deposition_id} not found.")

        meta_data = deposition.meta_data or {}

        for key in ("title", "description", "tags", "publication_type", "publication_doi"):
            if key in metadata:
                meta_data[key] = metadata[key]

        meta_data["dirty"] = True
        deposition.meta_data = meta_data
        flag_modified(deposition, "meta_data")
        db.session.commit()

        logger.info(f"FakenodoRepository: Updated metadata for deposition ID {deposition_id} (dirty=True)")
        return {
            "id": deposition.id,
            "metadata": meta_data,
            "status": deposition.status,
            "doi": deposition.doi,
            "dirty": True,
            "versions": meta_data.get("versions", []),
        }

    def get_deposition(self, deposition_id: int) -> Fakenodo:
        """Retrieve a deposition entry by its ID."""
        deposition = Fakenodo.query.get(deposition_id)
        if not deposition:
            raise Exception(f"Deposition with ID {deposition_id} not found.")
        return deposition

    def get_by_doi(self, doi: str) -> Fakenodo | None:
        """Retrieve a deposition entry by its DOI."""
        try:
            return Fakenodo.query.filter_by(doi=doi).first()
        except Exception:
            logger.exception("FakenodoRepository: error fetching by DOI %s", doi)
            return None

    def delete_deposition(self, deposition_id: int) -> bool:
        """Delete a deposition entry from the database."""
        deposition = Fakenodo.query.get(deposition_id)
        if deposition:
            db.session.delete(deposition)
            db.session.commit()
            logger.info(f"FakenodoRepository: Deleted deposition with ID {deposition_id}")
            return True
        logger.warning(f"FakenodoRepository: Tried to delete non-existent deposition ID {deposition_id}")
        return False
