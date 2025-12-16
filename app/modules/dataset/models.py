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
    version_doi = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ds_meta_data_id = db.Column(db.Integer, db.ForeignKey("ds_meta_data.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(50), nullable=False, server_default="csv", index=True)

    downloads = db.relationship("Download", backref="data_set", lazy="dynamic", cascade="all, delete-orphan")
    version = db.relationship("DatasetVersion", backref="data_set", lazy="dynamic", cascade="all, delete-orphan")

    ds_meta_data = db.relationship("DSMetaData", backref=db.backref("data_set", uselist=False))
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "base",
        "with_polymorphic": "*",
    }

    version = db.relationship("DatasetVersion", backref="data_set", uselist=False, cascade="all, delete-orphan")


    def get_number_of_downloads(self):
        return self.downloads.count()

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

        base_title = self.ds_meta_data.title
        v = getattr(self, "version", None)

        if v is not None:
            base_title = f'{base_title} (version {v.version_major}.{v.version_minor})'

        # Añadimos estrellita si esta versión es la última del concepto
        star = ""
        try:
            if v is not None and getattr(v, "concept", None) is not None:
                latest = v.concept.latest_version()
                if latest and latest.id == v.id:
                    star = " ⭐"
        except Exception:
            # Por si acaso algo viene a None o la relación no está cargada
            star = ""

        full_title = base_title + star
        return {
            "title": full_title,
            "id": self.id,
            "created_at": self.created_at,
            "created_at_timestamp": int(self.created_at.timestamp()),
            "description": self.ds_meta_data.description,
            # Keep compatibility with previous API returning a list of authors
            "authors": ([self.ds_meta_data.author.to_dict()] if self.ds_meta_data and self.ds_meta_data.author else []),
            "publication_type": self.get_cleaned_publication_type(),
            "publication_doi": self.ds_meta_data.publication_doi,
            "dataset_doi": self.ds_meta_data.dataset_doi,
            "tags": self.ds_meta_data.tags.split(",") if self.ds_meta_data.tags else ["None"],
            "url": f'/dataset/doi/{self.version_doi}' if self.version_doi else None,
            "download": f'{request.host_url.rstrip("/")}/dataset/download/{self.id}',
            # Use the dataset-level method to obtain the number of downloads (counts Download rows)
            "downloads": self.get_number_of_downloads() or 0,
            "zenodo": self.get_zenodo_url(),
            "files": [file.to_dict() for fm in self.file_models for file in fm.files],
            "files_count": self.get_files_count(),
            "total_size_in_bytes": self.get_file_total_size(),
            "total_size_in_human_format": self.get_file_total_size_for_human(),
        }
    def clone(self):
        # Import local to avoid circular imports with fileModel.models
        from app.modules.fileModel.models import FMMetaData, FileModel
        
        # Crear nuevo dataset
        new_ds = TabularDataset(
            user_id=self.user_id,
            ds_meta_data_id=self.ds_meta_data.id,
            rows_count=self.rows_count,
            schema_json=self.schema_json
        )
        db.session.add(new_ds)
        db.session.flush()

        # Clonar FileModels + archivos físicos
        for fm in self.file_models:
            new_fm_meta = FMMetaData(
                csv_filename=fm.fm_meta_data.csv_filename,
                title=fm.fm_meta_data.title,
                description=fm.fm_meta_data.description,
                publication_doi=fm.fm_meta_data.publication_doi,
                tags=fm.fm_meta_data.tags,
                csv_version=fm.fm_meta_data.csv_version,
                author_id=fm.fm_meta_data.author_id
            )
            db.session.add(new_fm_meta)
            db.session.flush()

            new_fm = FileModel(
                data_set_id=new_ds.id,
                fm_meta_data_id=new_fm_meta.id
            )
            db.session.add(new_fm)
            db.session.flush()

            # Copiar archivos físicos + crear Hubfile para cada archivo
            import shutil, os
            from app.modules.hubfile.models import Hubfile
            
            user_folder = f"user_{self.user_id}/dataset_{self.id}"
            new_folder = f"user_{self.user_id}/dataset_{new_ds.id}"

            old_path = os.path.join("uploads", user_folder)
            new_path = os.path.join("uploads", new_folder)
            os.makedirs(new_path, exist_ok=True)

            for f in fm.files:
                # Resolve the source path in a backward-compatible way.
                src = None
                # Preferred: Hubfile.get_path() which uses HubfileService
                if hasattr(f, "get_path"):
                    try:
                        src = f.get_path()
                    except Exception:
                        src = None
                # Older code might expose a path() method
                if not src and hasattr(f, "path"):
                    try:
                        src = f.path()
                    except Exception:
                        src = None

                # As a last resort try to compose the path from the known uploads layout
                if not src:
                    src = os.path.join(old_path, getattr(f, "name", ""))

                # Only copy if the source exists
                if src and os.path.exists(src):
                    dest_file = os.path.join(new_path, os.path.basename(src))
                    shutil.copy(src, dest_file)
                    
                    # Create a new Hubfile entry for the cloned file
                    new_hubfile = Hubfile(
                        name=f.name,
                        checksum=f.checksum,
                        size=f.size,
                        file_model_id=new_fm.id
                    )
                    db.session.add(new_hubfile)
                    new_fm.files.append(new_hubfile)

        db.session.flush()
        return new_ds

    def __repr__(self):
        return f"DataSet<{self.id}>"


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

class DatasetConcept(db.Model):
    __tablename__ = "dataset_concept"

    id = db.Column(db.Integer, primary_key=True)

    # DOI conceptual → siempre apunta a la última versión
    conceptual_doi = db.Column(db.String(255), unique=True, nullable=False)

    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    versions = db.relationship(
        "DatasetVersion",
        backref="concept",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def latest_version(self):
        return max(self.versions, key=lambda v: (v.version_major, v.version_minor), default=None)

class DatasetVersion(db.Model):
    __tablename__ = "dataset_version"

    id = db.Column(db.Integer, primary_key=True)

    concept_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset_concept.id"),
        nullable=False
    )

    # Dataset real, donde están archivos y metadata
    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("data_set.id"),
        nullable=False
        )

    version_major = db.Column(db.Integer, nullable=False)
    version_minor = db.Column(db.Integer, nullable=False, default=0)

    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    changelog = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint(
            "concept_id",
            "version_major",
            "version_minor",
            name="uq_dataset_version_number"
        ),
    )

    def is_major(self):
        return self.version_minor == 0

    def version_label(self):
        return f"{self.version_major}.{self.version_minor}"



DataSet = TabularDataset  # Alias para compatibilidad hacia atrás

#He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código.
#La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.