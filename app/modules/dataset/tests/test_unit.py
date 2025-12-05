import pytest
import os
import shutil
import time

from app import db
from datetime import datetime, timezone, timedelta

from unittest import mock

from app.modules.dataset.services import DataSetService
from app.modules.dataset.models import (
    TabularDataset,
    PublicationType,
    DSMetaData,
    Download,
    DatasetConcept,
    DatasetVersion,
    DataSet
)

from app.modules.fileModel.models import (
    FileModel,
    FMMetaData,
    FMMetrics
)

from app.modules.auth.models import User


# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        yield test_client


def create_dataset(email, title="Test DS"):
    """Helper para crear un dataset mínimo válido."""
    user = User(email=email, password="1234")
    db.session.add(user)
    db.session.flush()

    meta = DSMetaData(
        title=title,
        description="DS description",
        publication_type=PublicationType.NONE,
    )
    db.session.add(meta)
    db.session.flush()

    ds = TabularDataset(user_id=user.id, ds_meta_data_id=meta.id)
    db.session.add(ds)
    db.session.flush()

    return user, meta, ds


# =====================================================
# TESTS DE DOWNLOAD STATS
# =====================================================

def test_get_number_of_downloads(clean_database, test_client):
    with test_client.application.app_context():

        user, meta, ds = create_dataset("user1@example.com")

        for _ in range(7):
            db.session.add(Download(dataset_id=ds.id))

        db.session.commit()

        service = DataSetService()
        assert service.get_number_of_downloads(ds.id) == 7


def test_update_download_count_increments(clean_database, test_client):
    with test_client.application.app_context():

        user, meta, ds = create_dataset("user2@example.com")

        for _ in range(5):
            db.session.add(Download(dataset_id=ds.id))
        db.session.commit()

        service = DataSetService()
        service.update_download_count(ds.id)

        assert service.get_number_of_downloads(ds.id) == 6


def test_get_top_downloaded_last_week(clean_database, test_client):
    with test_client.application.app_context():

        user = User(email="user3@example.com", password="1234")
        db.session.add(user)
        db.session.flush()

        d2 = datetime.now(timezone.utc) - timedelta(days=2)
        d12 = datetime.now(timezone.utc) - timedelta(days=12)

        for i in range(1, 11):
            meta = DSMetaData(
                title=f"DS{i}",
                description=f"Desc{i}",
                publication_type=PublicationType.NONE,
            )
            db.session.add(meta)
            db.session.flush()

            ds = TabularDataset(user_id=user.id, ds_meta_data_id=meta.id)
            db.session.add(ds)
            db.session.flush()

            when = d12 if i == 10 else d2
            for _ in range(i):
                db.session.add(Download(dataset_id=ds.id, download_date=when))

        db.session.commit()

        service = DataSetService()
        top3 = service.get_top_downloaded_last_week(limit=3)
        titles = [d.ds_meta_data.title for d in top3]

        assert titles == ["DS9", "DS8", "DS7"]


# =====================================================
# TESTS DE VERSIONADO
# =====================================================

def test_create_version_1_0(clean_database, test_client):
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest1@example.com")

        concept = DatasetConcept(
            conceptual_doi="10.concept.1",
            name="Concept 1"
        )
        db.session.add(concept)
        db.session.flush()

        v1 = DatasetVersion(
            concept_id=concept.id,
            dataset_id=ds.id,
            version_major=1,
            version_minor=0,
            version_doi="10.concept.1.v1",
            changelog="Initial release"
        )
        db.session.add(v1)
        db.session.commit()

        assert v1.id is not None
        assert concept.versions[0].version_major == 1


def test_multiple_versions_same_dataset(clean_database, test_client):
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest2@example.com")

        concept = DatasetConcept(conceptual_doi="10.concept.2", name="Concept 2")
        db.session.add(concept)
        db.session.flush()

        versions = [
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=1),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=0),
        ]

        db.session.add_all(versions)
        db.session.commit()

        assert len(concept.versions) == 3


def test_unique_version_number_constraint(clean_database, test_client):
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest3@example.com")

        concept = DatasetConcept(conceptual_doi="10.concept.3", name="Concept 3")
        db.session.add(concept)
        db.session.flush()

        v1 = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0)
        db.session.add(v1)
        db.session.commit()

        dup = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0)
        db.session.add(dup)

        with pytest.raises(Exception):
            db.session.commit()


def test_latest_version(clean_database, test_client):
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest4@example.com")

        concept = DatasetConcept(conceptual_doi="10.concept.4", name="Concept 4")
        db.session.add(concept)
        db.session.flush()

        versions = [
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=1),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=0),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=3),
        ]

        db.session.add_all(versions)
        db.session.commit()

        latest = concept.latest_version()
        assert (latest.version_major, latest.version_minor) == (2, 3)


def test_concept_relationship(clean_database, test_client):
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest5@example.com")

        concept = DatasetConcept(conceptual_doi="10.concept.5", name="Concept 5")
        db.session.add(concept)
        db.session.flush()

        v10 = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0)
        v20 = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=0)

        db.session.add_all([v10, v20])
        db.session.commit()

        assert len(concept.versions) == 2


def test_service_create_version_via_service(ds_with_file, test_client):
    """Verifica que DataSetService.create_version clona el dataset y añade una nueva DatasetVersion."""
    with test_client.application.app_context():
        original = ds_with_file

        # crear concepto y versión inicial
        concept = DatasetConcept(conceptual_doi="10.concept.svc", name="Svc Concept")
        db.session.add(concept)
        db.session.flush()

        v1 = DatasetVersion(concept_id=concept.id, dataset_id=original.id, version_major=1, version_minor=0)
        db.session.add(v1)
        db.session.commit()

        svc = DataSetService()
        new_version = svc.create_version(original, major=1, minor=1, changelog="Create via service")

        # recargar datos
        db.session.refresh(concept)

        labels = sorted([v.version_label() for v in concept.versions])
        assert "1.0" in labels and "1.1" in labels

        # comprobar que el dataset original y el nuevo existen y son distintos
        ds_ids = {v.dataset_id for v in concept.versions}
        assert original.id in ds_ids
        assert len(ds_ids) == 2
    

def test_service_get_dataset_version(clean_database, test_client):
    dataset_service = DataSetService()

    # Crear un Dataset Concept
    concept = DatasetConcept(
        conceptual_doi="10.1234/concept1",
        name="Concept for dataset 1"
    )
    db.session.add(concept)
    db.session.commit()  # Commit para asegurarnos de que el concepto esté persistido en la base de datos

    user, meta, dataset1 = create_dataset("user1@example.com")
    user, meta, dataset2 = create_dataset("user2@example.com")

    # Crear las versiones de los datasets (en este caso con dataset1 y dataset2)
    dataset_version_1 = DatasetVersion(
        concept_id=concept.id,  # Asociamos la versión al concepto correcto
        dataset_id=dataset1.id,  # Relacionamos con dataset1
        version_major=1,
        version_minor=0,
        version_doi="10.1234/dataset1.v1",
        changelog="Initial release"
    )
    db.session.add(dataset_version_1)

    dataset_version_2 = DatasetVersion(
        concept_id=concept.id,  # Asociamos la versión al concepto correcto
        dataset_id=dataset2.id,  # Relacionamos con dataset2
        version_major=1,
        version_minor=1,
        version_doi="10.1234/dataset2.v1",
        changelog="Minor updates"
    )
    db.session.add(dataset_version_2)
    db.session.commit()  # Commit para guardar las versiones en la base de datos

    # Llamamos a la función que queremos probar
    versions = dataset_service.get_dataset_versions(dataset1.id)  # Cambié `dataset.id` por `dataset1.id` para la prueba

    # Verificamos que las versiones obtenidas son las correctas
    assert len(versions) == 2  # Solo debe haber 2 versiones asociadas a dataset1
    assert versions[0].version_major == 1
    assert versions[0].version_minor == 0
    assert versions[1].version_major == 1
    assert versions[1].version_minor == 1
    assert versions[0].version_doi == "10.1234/dataset1.v1"
    assert versions[1].version_doi == "10.1234/dataset2.v1"






# =====================================================
# FIXTURE PARA TESTS DE CLONE()
# =====================================================

@pytest.fixture
def ds_with_file(clean_database, test_client):
    """Dataset mínimo con archivo real para test de clone()."""
    with test_client.application.app_context():

        email = f"clone_{int(time.time()*1000)}@test.com"

        user = User(email=email, password="1234")
        db.session.add(user)
        db.session.flush()

        meta = DSMetaData(
            title="Original Dataset",
            description="Original desc",
            publication_type=PublicationType.NONE,
        )
        db.session.add(meta)
        db.session.flush()

        ds = TabularDataset(user_id=user.id, ds_meta_data_id=meta.id)
        db.session.add(ds)
        db.session.flush()

        fm_metrics = FMMetrics()
        db.session.add(fm_metrics)
        db.session.flush()

        # IMPORT DENTRO DEL FIXTURE (seguro y estable)
        from app.modules.fileModel.models import FMMetaData

        fm_meta = FMMetaData(
            csv_filename="original.csv",
            title="Original file",
            description="File desc",
            csv_version="1.0",
            fm_metrics_id=fm_metrics.id
        )
        db.session.add(fm_meta)
        db.session.flush()

        fm = FileModel(data_set_id=ds.id, fm_meta_data_id=fm_meta.id)
        db.session.add(fm)
        db.session.flush()

        folder = f"uploads/user_{user.id}/dataset_{ds.id}"
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "original.csv"), "w") as f:
            f.write("id,value\n1,100")

        # Create a Hubfile record so FileModel.files contains a Hubfile and
        # clone() can copy the physical file via HubfileService.get_path_by_hubfile
        from app.modules.hubfile.models import Hubfile
        file_path = os.path.join(folder, "original.csv")
        size = os.path.getsize(file_path)

        hubfile = Hubfile(name="original.csv", checksum="dummysum", size=size, file_model_id=fm.id)
        db.session.add(hubfile)
        db.session.flush()

        db.session.commit()

        yield ds

        shutil.rmtree("uploads", ignore_errors=True)


# =====================================================
# TESTS DE CLONE()
# =====================================================

def test_clone_creates_new_dataset(ds_with_file, test_client):
    with test_client.application.app_context():
        original = ds_with_file
        clone = original.clone()
        db.session.commit()

        assert clone.id != original.id
        assert clone.ds_meta_data_id != original.ds_meta_data_id


def test_clone_copies_metadata(ds_with_file, test_client):
    with test_client.application.app_context():
        original = ds_with_file
        clone = original.clone()
        db.session.commit()

        assert clone.ds_meta_data.title == original.ds_meta_data.title
        assert clone.ds_meta_data.description == original.ds_meta_data.description


def test_clone_copies_files(ds_with_file, test_client):
    with test_client.application.app_context():
        original = ds_with_file
        clone = original.clone()
        db.session.commit()

        clone_folder = f"uploads/user_{clone.user_id}/dataset_{clone.id}"

        assert os.path.exists(clone_folder)
        assert os.path.exists(os.path.join(clone_folder, "original.csv"))


def test_clone_creates_new_file_models(ds_with_file, test_client):
    with test_client.application.app_context():
        original = ds_with_file
        clone = original.clone()
        db.session.commit()

        assert clone.file_models[0].id != original.file_models[0].id
        assert clone.file_models[0].fm_meta_data_id != original.file_models[0].fm_meta_data_id


def test_clone_integrates_with_versioning(ds_with_file, test_client):
    with test_client.application.app_context():
        original = ds_with_file

        concept = DatasetConcept(conceptual_doi="10.concept.clone", name="Clone Concept")
        db.session.add(concept)
        db.session.flush()

        v1 = DatasetVersion(concept_id=concept.id, dataset_id=original.id, version_major=1, version_minor=0)
        db.session.add(v1)
        db.session.flush()

        clone = original.clone()
        v11 = DatasetVersion(concept_id=concept.id, dataset_id=clone.id, version_major=1, version_minor=1)
        db.session.add(v11)
        db.session.commit()

        ids = {v.dataset_id for v in concept.versions}

        assert original.id in ids
        assert clone.id in ids
        assert len(ids) == 2
