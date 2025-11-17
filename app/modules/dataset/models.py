from datetime import datetime
from enum import Enum

from flask import request
import math
from sqlalchemy import Enum as SQLAlchemyEnum

from app import db


class PublicationType(Enum):
    NONE = "none"
    SPECIFICATIONS = "specifications"
    SALES = "sales"
    RANKINGS = "rankings"
    REVIEWS = "reviews"
    MATERIALS = "materials"
    METHODS = "methods"
    RESULTS = "results"
    DISTRIBUTORS = "distributors"
    COMPETITORS = "competitors"
    RECORDS = "records"
    OTHER = "other"


class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    download_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    affiliation = db.Column(db.String(120))
    orcid = db.Column(db.String(120))
    # Optional link to a user account (allows reusing the same author for uploads)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    # Note: file-level authorship is represented from FMMetaData via FMMetaData.author_id

    def to_dict(self):
        return {"name": self.name, "affiliation": self.affiliation, "orcid": self.orcid}


class DSMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_models = db.Column(db.String(120))
    number_of_files = db.Column(db.String(120))
    

    def __repr__(self):
        return f"DSMetrics<models={self.number_of_models}, files={self.number_of_files}, downloads={self.number_of_downloads}>"


class DSMetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deposition_id = db.Column(db.Integer)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publication_type = db.Column(SQLAlchemyEnum(PublicationType), nullable=False)
    publication_doi = db.Column(db.String(120))
    dataset_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))
    ds_metrics_id = db.Column(db.Integer, db.ForeignKey("ds_metrics.id"))
    ds_metrics = db.relationship("DSMetrics", uselist=False, backref="ds_meta_data", cascade="all, delete")

    # Each DSMetaData points to a single Author (business rule: one author per dataset)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=True)
    author = db.relationship("Author", backref=db.backref("datasets", lazy=True), uselist=False)

class BaseDataset(db.Model):
    __tablename__ = "data_set"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ds_meta_data_id = db.Column(db.Integer, db.ForeignKey("ds_meta_data.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(50), nullable=False, server_default="csv", index=True)

    downloads = db.relationship("Download", backref="data_set", lazy=True, cascade="all, delete-orphan")

    ds_meta_data = db.relationship("DSMetaData", backref=db.backref("data_set", uselist=False))
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "base",
        "with_polymorphic": "*",
    }

    def get_cleaned_publication_type(self):
        """Devuelve el tipo de publicación limpiado desde DSMetaData si existe."""
        if self.ds_meta_data and hasattr(self.ds_meta_data, "get_cleaned_publication_type"):
            return self.ds_meta_data.get_cleaned_publication_type()
        return None
    
    def get_files_count(self):
        """
        Devuelve el número de archivos asociados al dataset.
        Por defecto, los datasets tabulares tienen un único CSV.
        """
        try:
            # Si hay un atributo 'files' en otros tipos de dataset (por ejemplo image, model, etc.)
            if hasattr(self, "files") and self.files:
                return len(self.files)
            # En datasets tabulares normalmente hay 1 archivo CSV
            return 1
        except Exception:
            return 0
    
    def get_file_total_size_for_human(self):
        """
        Devuelve el tamaño total de los archivos del dataset en formato legible (KB, MB, GB).
        Para datasets tabulares, devuelve el tamaño estimado del CSV si existe.
        """
        total_bytes = 0

        # 1️⃣ Si hay relación con archivos (otros tipos de dataset)
        if hasattr(self, "files") and self.files:
            total_bytes = sum(getattr(f, "size", 0) for f in self.files)

        # 2️⃣ Si es tabular, intenta estimar a partir del CSV en carpeta temporal
        elif hasattr(self, "get_csv_path"):
            try:
                import os
                csv_path = self.get_csv_path()
                if csv_path and os.path.exists(csv_path):
                    total_bytes = os.path.getsize(csv_path)
            except Exception:
                pass

        # 3️⃣ Convierte a formato legible
        if total_bytes == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(total_bytes)
        i = int(math.floor(math.log(size, 1024)))
        human_size = round(size / (1024 ** i), 2)
        return f"{human_size} {units[i]}"

    def validate_domain(self):
        pass

    def ui_blocks(self):
        return ["common-meta", "versioning"]

    def get_rubikhub_doi(self):
        from app.modules.dataset.services import DataSetService

        return DataSetService().get_rubikhub_doi(self)


class TabularDataset(BaseDataset):
    __mapper_args__ = {"polymorphic_identity": "tabular"}

    rows_count = db.Column(db.Integer, nullable=True)
    schema_json = db.Column(db.Text, nullable=True)

    tabular_meta_data = db.relationship("TabularMetaData", backref="dataset", uselist=False, cascade="all, delete-orphan")

    tabular_metrics = db.relationship("TabularMetrics", backref="dataset", uselist=False, cascade="all, delete-orphan")

    file_models = db.relationship("FileModel", backref="data_set", lazy=True, cascade="all, delete")

    def name(self):
        return self.ds_meta_data.title

    def files(self):
        return [file for fm in self.file_models for file in fm.files]

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_cleaned_publication_type(self):
        return self.ds_meta_data.publication_type.name.replace("_", " ").title()

    def get_zenodo_url(self):
        return f"https://zenodo.org/record/{self.ds_meta_data.deposition_id}" if self.ds_meta_data.dataset_doi else None

    def get_files_count(self):
        return sum(len(fm.files) for fm in self.file_models)

    def get_file_total_size(self):
        return sum(file.size for fm in self.file_models for file in fm.files)

    def get_file_total_size_for_human(self):
        from app.modules.dataset.services import SizeService

        return SizeService().get_human_readable_size(self.get_file_total_size())
    
    def validate_domain(self):
        if self.rows_count is not None and self.rows_count < 0:
            raise ValueError("rows_count cannot be negative")

    def ui_blocks(self):
        return ["common-meta", "table-schema", "sample-rows", "versioning"]
    
    def get_csv_path(self):
        """Devuelve la ruta completa del CSV asociado a este dataset."""
        import os

        temp_folder = self.user.temp_folder()
        if os.path.exists(temp_folder):
            for f in os.listdir(temp_folder):
                if f.lower().endswith(".csv"):
                    return os.path.join(temp_folder, f)
        return None

    def to_dict(self):
        return {
            "title": self.ds_meta_data.title,
            "id": self.id,
            "created_at": self.created_at,
            "created_at_timestamp": int(self.created_at.timestamp()),
            "description": self.ds_meta_data.description,
            # Keep compatibility with previous API returning a list of authors
            "authors": ([self.ds_meta_data.author.to_dict()] if self.ds_meta_data and self.ds_meta_data.author else []),
            "publication_type": self.get_cleaned_publication_type(),
            "publication_doi": self.ds_meta_data.publication_doi,
            "dataset_doi": self.ds_meta_data.dataset_doi,
            "tags": self.ds_meta_data.tags.split(",") if self.ds_meta_data.tags else [],
            "url": self.get_rubikhub_doi(),
            "download": f'{request.host_url.rstrip("/")}/dataset/download/{self.id}',
            "downloads": (self.file_models[0].fm_meta_data.fm_metrics.number_of_downloads
                          if self.file_models and self.file_models[0].fm_meta_data and self.file_models[0].fm_meta_data.fm_metrics
                          else 0),
            "zenodo": self.get_zenodo_url(),
            "files": [file.to_dict() for fm in self.file_models for file in fm.files],
            "files_count": self.get_files_count(),
            "total_size_in_bytes": self.get_file_total_size(),
            "total_size_in_human_format": self.get_file_total_size_for_human(),
        }

    def __repr__(self):
        return f"DataSet<{self.id}>"


class TabularMetaData(db.Model):
    """
    Guarda los metadatos generales del archivo CSV (la "radiografía").
    Relación 1-a-1 con TabularDataset.
    """

    __tablename__ = "tabular_meta_data"
    id = db.Column(db.Integer, primary_key=True)

    # --- Campos del checklist ---
    hubfile_id = db.Column(db.Integer)
    delimiter = db.Column(db.String(5))
    encoding = db.Column(db.String(20))
    has_header = db.Column(db.Boolean, default=True)
    n_rows = db.Column(db.Integer)
    n_cols = db.Column(db.Integer)

    # JSON para datos complejos
    primary_keys = db.Column(db.JSON)
    index_cols = db.Column(db.JSON)
    sample_rows = db.Column(db.JSON)

    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), unique=True, nullable=False)

    columns = db.relationship("TabularColumn", backref="meta_data", lazy="dynamic", cascade="all, delete-orphan")


class TabularColumn(db.Model):
    """
    Guarda los metadatos de CADA columna del CSV.
    Relación N-a-1 con TabularMetaData.
    """

    __tablename__ = "tabular_column"
    id = db.Column(db.Integer, primary_key=True)

    # --- Campos del checklist ---
    name = db.Column(db.String(255), nullable=False)
    dtype = db.Column(db.String(50))
    null_count = db.Column(db.Integer, default=0)
    unique_count = db.Column(db.Integer, default=0)
    stats = db.Column(db.JSON)

    # --- Conexión (ForeignKey) ---
    # Conexión N-a-1 con TabularMetaData
    meta_id = db.Column(db.Integer, db.ForeignKey("tabular_meta_data.id"), nullable=False)


class TabularMetrics(db.Model):
    """
    (Opcional) Guarda métricas de calidad de alto nivel.
    Relación 1-a-1 con TabularDataset.
    """

    __tablename__ = "tabular_metrics"
    id = db.Column(db.Integer, primary_key=True)

    # --- Campos del checklist ---
    null_ratio = db.Column(db.Float)
    avg_cardinality = db.Column(db.Float)

    # --- Conexión (ForeignKey) ---
    # Conexión 1-a-1 con TabularDataset
    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), unique=True, nullable=False)


class DSDownloadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"))
    download_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    download_cookie = db.Column(db.String(36), nullable=False)

    def __repr__(self):
        return (
            f"<Download id={self.id} "
            f"dataset_id={self.dataset_id} "
            f"date={self.download_date} "
            f"cookie={self.download_cookie}>"
        )


class DSViewRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"))
    view_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    view_cookie = db.Column(db.String(36), nullable=False)

    def __repr__(self):
        return f"<View id={self.id} dataset_id={self.dataset_id} date={self.view_date} cookie={self.view_cookie}>"


class DOIMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_doi_old = db.Column(db.String(120))
    dataset_doi_new = db.Column(db.String(120))


DataSet = TabularDataset  # Alias para compatibilidad hacia atrás
