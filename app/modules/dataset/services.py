import hashlib
import logging
import os
import shutil
import uuid
from typing import Optional

from flask import request

from app import db
from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DataSet, DatasetVersion, DSMetaData, DSViewRecord
from app.modules.dataset.repositories import (
    AuthorRepository,
    DataSetRepository,
    DOIMappingRepository,
    DownloadRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
)
from app.modules.fileModel.repositories import FileModelRepository, FMMetaDataRepository
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)
from app.utils import notifications
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)


def calculate_checksum_and_size(file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file:
        content = file.read()
        hash_md5 = hashlib.md5(content, usedforsecurity=False).hexdigest()
        return hash_md5, file_size


class DataSetService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        # use FileModelRepository (previously FeatureModelRepository)
        self.feature_model_repository = FileModelRepository()
        self.author_repository = AuthorRepository()
        self.dsmetadata_repository = DSMetaDataRepository()
        self.fmmetadata_repository = FMMetaDataRepository()
        self.dsdownloadrecord_repository = DSDownloadRecordRepository()
        self.hubfiledownloadrecord_repository = HubfileDownloadRecordRepository()
        self.hubfilerepository = HubfileRepository()
        self.dsviewrecord_repostory = DSViewRecordRepository()
        self.hubfileviewrecord_repository = HubfileViewRecordRepository()
        self.download_repository = DownloadRepository()
    
    def filter_by_doi(self, doi: str) -> Optional[DataSet]:
        return self.repository.filter_by_doi(doi)
    
    def get_dataset_versions(self, dataset_id):
        # Primero buscamos el dataset por su ID
        dataset = DataSet.query.filter_by(id=dataset_id).first()
        if not dataset:
            return []

        version = DatasetVersion.query.filter_by(dataset_id=dataset.id).first()
        if not version:
            return []
        
        # Conseguimos el concept_id desde el dataset
        concept_id = version.concept_id

        # Ahora obtenemos todas las versiones asociadas a este DatasetConcept
        return ["b", "c"]


    def update_download_count(self, dataset_id):
        self.download_repository.create_download_record(dataset_id=dataset_id)

    def move_file_models(self, dataset: DataSet):
        current_user = AuthenticationService().get_authenticated_user()
        source_dir = current_user.temp_folder()

        working_dir = os.getenv("WORKING_DIR", "")
        dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")

        os.makedirs(dest_dir, exist_ok=True)

        for file_model in dataset.file_models:
            csv_filename = file_model.fm_meta_data.csv_filename
            src_path = os.path.join(source_dir, csv_filename)
            if not os.path.exists(src_path):
                logger.warning("Source CSV not found for move: %s", src_path)
                continue

            # If destination file exists, create a unique filename to avoid shutil.Error
            dest_path = os.path.join(dest_dir, csv_filename)
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(csv_filename)
                i = 1
                new_name = f"{base} ({i}){ext}"
                new_dest = os.path.join(dest_dir, new_name)
                while os.path.exists(new_dest):
                    i += 1
                    new_name = f"{base} ({i}){ext}"
                    new_dest = os.path.join(dest_dir, new_name)
                # Update fm_meta_data and hubfile name to the unique filename
                try:
                    file_model.fm_meta_data.csv_filename = new_name
                except Exception:
                    pass
                # If there is an associated hubfile created, update its name as well
                try:
                    if getattr(file_model, "files", None):
                        hf = file_model.files[0]
                        hf.name = new_name
                except Exception:
                    pass
                shutil.move(src_path, new_dest)
            else:
                shutil.move(src_path, dest_dir)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_synchronized(current_user_id)

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_unsynchronized(current_user_id)

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return self.repository.get_unsynchronized_dataset(current_user_id, dataset_id)

    def latest_synchronized(self):
        return self.repository.latest_synchronized()

    def count_synchronized_datasets(self):
        return self.repository.count_synchronized_datasets()

    def count_file_models(self):
        return self.feature_model_service.count_file_models()

    def count_authors(self) -> int:
        return self.author_repository.count()

    def count_dsmetadata(self) -> int:
        return self.dsmetadata_repository.count()

    def total_dataset_downloads(self) -> int:
        return self.dsdownloadrecord_repository.total_dataset_downloads()

    def total_dataset_views(self) -> int:
        return self.dsviewrecord_repostory.total_dataset_views()

    def create_from_form(self, form, current_user) -> DataSet:
        main_author = {
            "name": f"{current_user.profile.surname}, {current_user.profile.name}",
            "affiliation": current_user.profile.affiliation,
            "orcid": current_user.profile.orcid,
        }
        try:
            # 1) Crear DSMetaData del dataset
            logger.info(f"Creating dsmetadata...: {form.get_dsmetadata()}")
            dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())

            # 2) Autor del dataset (regla de negocio: un dataset tiene 1 autor)
            # Preferimos reutilizar un Author existente vinculado al usuario (user_id),
            # luego por ORCID y finalmente por name+affiliation. Si no existe, lo creamos.
            author_data = None
            extra_authors = form.get_authors()
            if extra_authors and len(extra_authors) > 0:
                author_data = extra_authors[0]
            else:
                author_data = main_author

            existing_author = None
            try:
                # 1) Prefer user-associated author
                if current_user and getattr(current_user, "id", None):
                    existing_author = self.author_repository.model.query.filter_by(user_id=current_user.id).first()

                # 2) Then ORCID
                if not existing_author and author_data.get("orcid"):
                    existing_author = self.author_repository.model.query.filter_by(orcid=author_data.get("orcid")).first()

                # 3) Finally name + affiliation
                if not existing_author and author_data.get("name"):
                    existing_author = (
                        self.author_repository.model.query.filter_by(name=author_data.get("name"), affiliation=author_data.get("affiliation")).first()
                    )
            except Exception:
                existing_author = None

            if existing_author:
                dsmetadata.author = existing_author
            else:
                author = self.author_repository.create(
                    commit=False,
                    user_id=current_user.id if current_user and getattr(current_user, "id", None) else None,
                    **author_data,
                )
                dsmetadata.author = author

            # 3) Crear el TabularDataset asociado
            from app.modules.dataset.models import TabularDataset

            dataset = TabularDataset(user_id=current_user.id, ds_meta_data_id=dsmetadata.id)
            self.repository.session.add(dataset)
            self.repository.session.flush()  # Para tener dataset.id

            # 4) Crear FileModel + FMMetaData + Hubfile por cada entry de file_models
            for file_model in form.file_models:
                csv_filename = file_model.csv_filename.data

                # Diccionario base desde el form
                fmmetadata_data = file_model.get_fmmetadata()

                # ⚠️ FMMetaData NO tiene 'publication_type' → lo eliminamos
                fmmetadata_data.pop("publication_type", None)

                # Rellenar valores por defecto desde dsmetadata si vienen vacíos
                if not fmmetadata_data.get("title"):
                    fmmetadata_data["title"] = dsmetadata.title

                if not fmmetadata_data.get("description"):
                    fmmetadata_data["description"] = dsmetadata.description

                if "publication_doi" in fmmetadata_data and not fmmetadata_data["publication_doi"]:
                    fmmetadata_data["publication_doi"] = dsmetadata.publication_doi

                if "tags" in fmmetadata_data and not fmmetadata_data["tags"]:
                    fmmetadata_data["tags"] = dsmetadata.tags

                # 4.1 Crear FMMetaData
                fmmetadata = self.fmmetadata_repository.create(commit=False, **fmmetadata_data)

                # 4.2 Autor del FMMetaData: use the same author as the DSMetaData
                if dsmetadata and dsmetadata.author:
                    fmmetadata.author = dsmetadata.author
                else:
                    # Fallback (should be rare): reuse same logic to create/reuse an author
                    fm_author_data = None
                    fm_authors_list = file_model.get_authors()
                    if fm_authors_list and len(fm_authors_list) > 0:
                        fm_author_data = fm_authors_list[0]
                    else:
                        fm_author_data = {"name": dsmetadata.title if dsmetadata else "", "affiliation": None, "orcid": None}

                    existing_fm_author = None
                    try:
                        if current_user and getattr(current_user, "id", None):
                            existing_fm_author = self.author_repository.model.query.filter_by(user_id=current_user.id).first()
                        if not existing_fm_author and fm_author_data.get("orcid"):
                            existing_fm_author = self.author_repository.model.query.filter_by(orcid=fm_author_data.get("orcid")).first()
                        if not existing_fm_author and fm_author_data.get("name"):
                            existing_fm_author = (
                                self.author_repository.model.query.filter_by(name=fm_author_data.get("name"), affiliation=fm_author_data.get("affiliation")).first()
                            )
                    except Exception:
                        existing_fm_author = None

                    if existing_fm_author:
                        fmmetadata.author = existing_fm_author
                    else:
                        author = self.author_repository.create(
                            commit=False,
                            user_id=current_user.id if current_user and getattr(current_user, "id", None) else None,
                            **fm_author_data,
                        )
                        fmmetadata.author = author

                # 4.3 Crear FileModel
                fm = self.feature_model_repository.create(
                    commit=False,
                    data_set_id=dataset.id,
                    fm_meta_data_id=fmmetadata.id,
                )

                # 4.4 Crear Hubfile asociado al FileModel
                file_path = os.path.join(current_user.temp_folder(), csv_filename)
                checksum, size = calculate_checksum_and_size(file_path)

                file = self.hubfilerepository.create(
                    commit=False,
                    name=csv_filename,
                    checksum=checksum,
                    size=size,
                    file_model_id=fm.id,
                )
                fm.files.append(file)

            # 5) Crear DatasetConcept y DatasetVersion 1.0
            from app.modules.dataset.models import DatasetConcept, DatasetVersion

            # Generar DOI conceptual único
            concept_doi = f"concept-{dataset.id}-{uuid.uuid4().hex[:8]}"
            
            concept = DatasetConcept(
                conceptual_doi=concept_doi,
                name=dsmetadata.title
            )
            self.repository.session.add(concept)
            self.repository.session.flush()
            
            # Crear versión inicial 1.0
            version = DatasetVersion(
                concept_id=concept.id,
                dataset_id=dataset.id,
                version_major=1,
                version_minor=0,
                changelog="Initial version"
            )
            self.repository.session.add(version)

            # 6) Confirmar todo
            self.repository.session.commit()
            notifications.notify_followers_of_author(current_user.id, dataset)
        except Exception as exc:
            logger.info(f"Exception creating dataset from form...: {exc}")
            self.repository.session.rollback()
            raise exc
        return dataset

    def update_dsmetadata(self, id, **kwargs):
        return self.dsmetadata_repository.update(id, **kwargs)

    def update_version_doi(self, dataset_id: int):
        dataset = self.repository.get_by_id(dataset_id)
        if not dataset:
            return None
        
        new_doi = dataset.ds_meta_data.dataset_doi

        dataset.version_doi = new_doi
        self.repository.session.add(dataset)
        self.repository.session.commit()
        return dataset

    def get_rubikhub_doi(self, dataset: DataSet) -> str:
        domain = os.getenv("DOMAIN", "localhost")
        return f"http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}"

    def get_number_of_downloads(self, dataset_id: int) -> int:
        return self.repository.get_number_of_downloads(dataset_id)

    def get_actual_version(self, dataset_id: int):
        """Obtiene la versión actual de un dataset."""
        dataset = DataSet.query.filter_by(id=dataset_id).first()
        if not dataset:
            return None
        version = DatasetVersion.query.filter_by(dataset_id=dataset.id).first()
        if not version:
            return None
        return version

    def get_dataset_versions(self, dataset_id: int):
        """Obtiene todas las versiones de un dataset."""
        dataset = DataSet.query.filter_by(id=dataset_id).first()
        if not dataset:
            return []
        version = DatasetVersion.query.filter_by(dataset_id=dataset.id).first()
        if not version:
            return []
        concept_id = version.concept_id if dataset.version else None
        if not concept_id:
            return []
        return DatasetVersion.query.filter_by(concept_id=concept_id).all()
    
    def get_author_id_by_user_id(self, user_id: int) -> Optional[int]:
        author = self.author_repository.model.query.filter_by(user_id=user_id).first()
        if author:
            return author.id
        return None

    def get_top_downloaded_last_week(self, limit: int = 3):
        return self.repository.top_downloaded_last_week(limit)
        
    def create_version(self, dataset: DataSet, major: int, minor: int, changelog=""):
        # Clone the dataset first
        new_dataset = dataset.clone()

        # Try to determine the concept_id for the new version.
        # Prefer dataset.version if present, otherwise look up an existing DatasetVersion
        concept_id = None
        try:
            if getattr(dataset, "version", None) is not None and getattr(dataset.version, "concept_id", None):
                concept_id = dataset.version.concept_id
        except Exception:
            concept_id = None

        if concept_id is None:
            # Fallback: search for a DatasetVersion that references this dataset
            dv = DatasetVersion.query.filter_by(dataset_id=dataset.id).first()
            if dv:
                concept_id = dv.concept_id

        if concept_id is None:
            raise ValueError("Cannot determine concept for dataset when creating a new version")

        version = DatasetVersion(
            concept_id=concept_id,
            dataset_id=new_dataset.id,
            version_major=major,
            version_minor=minor,
            changelog=changelog,
        )
        db.session.add(version)
        db.session.commit()

        # Do NOT touch FakeNODO here. Zenodo logic: editing metadata only should not
        # generate a new DOI/version. Publishing after changing files will handle
        # DOI and versioning in the route.

        # Return the created DatasetVersion object for further processing
        return version


class AuthorService(BaseService):
    def __init__(self):
        super().__init__(AuthorRepository())


class DSDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(DSDownloadRecordRepository())


class DSMetaDataService(BaseService):
    def __init__(self):
        super().__init__(DSMetaDataRepository())

    def update(self, id, **kwargs):
        return self.repository.update(id, **kwargs)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.repository.filter_by_doi(doi)


class DSViewRecordService(BaseService):
    def __init__(self):
        super().__init__(DSViewRecordRepository())

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.repository.the_record_exists(dataset, user_cookie)

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.repository.create_new_record(dataset, user_cookie)

    def create_cookie(self, dataset: DataSet) -> str:

        user_cookie = request.cookies.get("view_cookie")
        if not user_cookie:
            user_cookie = str(uuid.uuid4())

        existing_record = self.the_record_exists(dataset=dataset, user_cookie=user_cookie)

        if not existing_record:
            self.create_new_record(dataset=dataset, user_cookie=user_cookie)

        return user_cookie


class DOIMappingService(BaseService):
    def __init__(self):
        super().__init__(DOIMappingRepository())

    def get_new_doi(self, old_doi: str) -> str:
        doi_mapping = self.repository.get_new_doi(old_doi)
        if doi_mapping:
            return doi_mapping.dataset_doi_new
        else:
            return None


class SizeService:

    def __init__(self):
        pass

    def get_human_readable_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024**2:
            return f"{round(size / 1024, 2)} KB"
        elif size < 1024**3:
            return f"{round(size / (1024 ** 2), 2)} MB"
        else:
            return f"{round(size / (1024 ** 3), 2)} GB"


