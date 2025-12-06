import logging
from datetime import datetime
from venv import logger

from app import db
from app.modules.fakenodo.models import Fakenodo
from core.repositories.BaseRepository import BaseRepository


class FakenodoRepository:
    """Repository for interacting with the Fakenodo depositions in the database."""

    def create_new_deposition(self, meta_data: dict = None, doi: str = None) -> Fakenodo:
        """
        Create a new deposition entry in the database.

        Args:
            meta_data (dict): Metadata for the deposition (title, description, etc.)
            doi (str): Optional DOI string.

        Returns:
            Fakenodo: The newly created database object.
        """
        if meta_data is None:

            meta_data = {}
        # Testing hooks here dont mind this message
        deposition = Fakenodo()
        deposition.meta_data = meta_data or {}
        deposition.doi = doi
        # default status
        if not getattr(deposition, "status", None):
            deposition.status = "draft"
        db.session.add(deposition)
        db.session.commit()

        logger.info(f"FakenodoRepository: Created new deposition with ID {deposition.id}")
        return deposition

    def add_csv_file(self, deposition_id: int, file_name: str, file_path: str) -> dict:
        """
        Attach a CSV file to an existing deposition record.

        Args:
            deposition_id (int): The deposition ID.
            file_name (str): The CSV filename.
            file_path (str): The simulated local path.

        Returns:
            dict: Updated meta_data with file information.
        """
        deposition = Fakenodo.query.get(deposition_id)
        if not deposition:
            raise Exception(f"Deposition with ID {deposition_id} not found.")

        # Add CSV info inside meta_data["files"]
        meta_data = deposition.meta_data or {}
        files = meta_data.get("files", [])
        files.append(
            {
                "file_name": file_name,
                "file_path": file_path,
                "file_type": "text/csv",
            }
        )
        meta_data["files"] = files
        deposition.meta_data = meta_data

        db.session.commit()

        logger.info(f"FakenodoRepository: Added CSV file '{file_name}' to deposition ID {deposition_id}")
        return meta_data

    def add_version(self, deposition_id: int, version_label: str, doi: str | None = None) -> dict:
        """Append a version entry to the deposition meta_data. Creates list if missing."""
        deposition = Fakenodo.query.get(deposition_id)
        if not deposition:
            raise Exception(f"Deposition with ID {deposition_id} not found.")

        meta_data = deposition.meta_data or {}
        versions = meta_data.get("versions", [])
        versions.append({
            "version": version_label,
            "doi": doi,
            "created_at": datetime.utcnow().isoformat() + "Z",
        })
        meta_data["versions"] = versions
        deposition.meta_data = meta_data

        db.session.commit()

        logger.info(f"FakenodoRepository: Added version '{version_label}' to deposition ID {deposition_id}")
        return meta_data

    def get_deposition(self, deposition_id: int) -> Fakenodo:
        """
        Retrieve a deposition entry by its ID.

        Args:
            deposition_id (int): The ID of the deposition.

        Returns:
            Fakenodo: The corresponding database object.
        """
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
        """
        Delete a deposition entry from the database.

        Args:
            deposition_id (int): The ID of the deposition to delete.

        Returns:
            bool: True if deleted, False otherwise.
        """
        deposition = Fakenodo.query.get(deposition_id)
        if deposition:
            db.session.delete(deposition)
            db.session.commit()
            logger.info(f"FakenodoRepository: Deleted deposition with ID {deposition_id}")
            return True

        logger.warning(f"FakenodoRepository: Tried to delete non-existent deposition ID {deposition_id}")
        return False
