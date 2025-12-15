import os
import shutil
import time
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import (
    Author,
    DataSet,
    DatasetConcept,
    DatasetVersion,
    Download,
    DSMetaData,
    PublicationType,
    TabularDataset,
)
from app.modules.dataset.services import DataSetService
from app.modules.fileModel.models import FileModel, FMMetaData, FMMetrics
from app.modules.hubfile.models import Hubfile
from app.modules.profile.models import UserProfile


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

        concept = DatasetConcept(conceptual_doi="10.concept.svc", name="Svc Concept")
        db.session.add(concept)
        db.session.flush()

        v1 = DatasetVersion(concept_id=concept.id, dataset_id=original.id, version_major=1, version_minor=0)
        db.session.add(v1)
        db.session.commit()

        svc = DataSetService()
        new_version = svc.create_version(original, major=1, minor=1, changelog="Create via service")

        db.session.refresh(concept)

        labels = sorted([v.version_label() for v in concept.versions])
        assert "1.0" in labels and "1.1" in labels

        ds_ids = {v.dataset_id for v in concept.versions}
        assert original.id in ds_ids
        assert len(ds_ids) == 2
    

def test_service_get_dataset_version(clean_database, test_client):
    dataset_service = DataSetService()

    concept = DatasetConcept(
        conceptual_doi="10.1234/concept1",
        name="Concept for dataset 1"
    )
    db.session.add(concept)
    db.session.commit()  

    user, meta, dataset1 = create_dataset("user1@example.com")
    user, meta, dataset2 = create_dataset("user2@example.com")

    dataset_version_1 = DatasetVersion(
        concept_id=concept.id,  
        dataset_id=dataset1.id,  
        version_major=1,
        version_minor=0,
        changelog="Initial release"
    )
    db.session.add(dataset_version_1)

    dataset_version_2 = DatasetVersion(
        concept_id=concept.id,  
        dataset_id=dataset2.id,  
        version_major=1,
        version_minor=1,
        changelog="Minor updates"
    )
    db.session.add(dataset_version_2)
    db.session.commit()  

    versions = dataset_service.get_dataset_versions(dataset1.id)  

    assert len(versions) == 2  
    assert versions[0].version_major == 1
    assert versions[0].version_minor == 0
    assert versions[1].version_major == 1
    assert versions[1].version_minor == 1


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


def test_clone_creates_new_dataset(ds_with_file, test_client):
    with test_client.application.app_context():
        original = ds_with_file
        clone = original.clone()
        db.session.commit()

        assert clone.id != original.id


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


def test_filter_by_doi(clean_database, test_client):
    """Verifica que filter_by_doi encuentra un dataset por su version_doi."""
    with test_client.application.app_context():
        user, meta, ds = create_dataset("doi_test@example.com")
        
        ds.version_doi = "10.5281/test.123456"
        db.session.commit()
        
        service = DataSetService()
        found = service.filter_by_doi("10.5281/test.123456")
        
        assert found is not None
        assert found.id == ds.id


def test_filter_by_doi_not_found(clean_database, test_client):
    """Verifica que filter_by_doi retorna None si no existe el DOI."""
    with test_client.application.app_context():
        service = DataSetService()
        found = service.filter_by_doi("10.5281/nonexistent.999999")
        
        assert found is None


def test_count_synchronized_datasets(clean_database, test_client):
    """Verifica el conteo de datasets sincronizados."""
    with test_client.application.app_context():
        user = User(email="sync_count@example.com", password="1234")
        db.session.add(user)
        db.session.flush()
        
        for i in range(3):
            meta = DSMetaData(
                title=f"Sync DS {i}",
                description="Test",
                publication_type=PublicationType.NONE,
                dataset_doi=f"10.5281/sync.{i}" if i < 2 else None  
            )
            db.session.add(meta)
            db.session.flush()
            
            ds = TabularDataset(user_id=user.id, ds_meta_data_id=meta.id)
            db.session.add(ds)
        
        db.session.commit()
        
        service = DataSetService()
        count = service.count_synchronized_datasets()
        
        assert count >= 2  


def test_count_authors(clean_database, test_client):
    """Verifica el conteo de autores."""
    with test_client.application.app_context():
        from app.modules.dataset.models import Author

        for i in range(3):
            author = Author(name=f"Author {i}", affiliation=f"Affiliation {i}")
            db.session.add(author)
        
        db.session.commit()
        
        service = DataSetService()
        count = service.count_authors()
        
        assert count >= 3


def test_count_dsmetadata(clean_database, test_client):
    """Verifica el conteo de DSMetaData."""
    with test_client.application.app_context():
        for i in range(4):
            meta = DSMetaData(
                title=f"Meta {i}",
                description="Test",
                publication_type=PublicationType.NONE,
            )
            db.session.add(meta)
        
        db.session.commit()
        
        service = DataSetService()
        count = service.count_dsmetadata()
        
        assert count >= 4


def test_update_dsmetadata(clean_database, test_client):
    """Verifica que update_dsmetadata actualiza los campos correctamente."""
    with test_client.application.app_context():
        user, meta, ds = create_dataset("update_meta@example.com", title="Original Title")
        
        service = DataSetService()
        service.update_dsmetadata(meta.id, title="Updated Title", description="Updated Desc")
        
        db.session.refresh(meta)
        
        assert meta.title == "Updated Title"
        assert meta.description == "Updated Desc"


def test_get_rubikhub_doi(clean_database, test_client):
    """Verifica que get_rubikhub_doi genera la URL correcta."""
    with test_client.application.app_context():
        user, meta, ds = create_dataset("rubikhub_doi@example.com")
        meta.dataset_doi = "10.5281/rubik.789"
        db.session.commit()
        
        service = DataSetService()
        url = service.get_rubikhub_doi(ds)
        
        assert "doi/10.5281/rubik.789" in url


def test_get_actual_version(clean_database, test_client):
    """Verifica que get_actual_version retorna la versión actual."""
    with test_client.application.app_context():
        user, meta, ds = create_dataset("actual_version@example.com")
        
        concept = DatasetConcept(conceptual_doi="10.concept.actual", name="Actual Concept")
        db.session.add(concept)
        db.session.flush()
        
        version = DatasetVersion(
            concept_id=concept.id,
            dataset_id=ds.id,
            version_major=2,
            version_minor=1,
            changelog="Test version"
        )
        db.session.add(version)
        db.session.commit()
        
        service = DataSetService()
        actual = service.get_actual_version(ds.id)
        
        assert actual is not None
        assert actual.version_major == 2
        assert actual.version_minor == 1


def test_get_actual_version_not_found(clean_database, test_client):
    """Verifica que get_actual_version retorna None si no hay versión."""
    with test_client.application.app_context():
        user, meta, ds = create_dataset("no_version@example.com")
        
        service = DataSetService()
        actual = service.get_actual_version(ds.id)
        
        assert actual is None


def test_get_actual_version_dataset_not_found(clean_database, test_client):
    """Verifica que get_actual_version retorna None si no existe el dataset."""
    with test_client.application.app_context():
        service = DataSetService()
        actual = service.get_actual_version(99999)
        
        assert actual is None


def test_get_author_id_by_user_id(clean_database, test_client):
    """Verifica que get_author_id_by_user_id encuentra el autor correcto."""
    with test_client.application.app_context():
        from app.modules.dataset.models import Author
        
        user = User(email="author_lookup@example.com", password="1234")
        db.session.add(user)
        db.session.flush()
        
        author = Author(name="Test Author", user_id=user.id)
        db.session.add(author)
        db.session.commit()
        
        service = DataSetService()
        author_id = service.get_author_id_by_user_id(user.id)
        
        assert author_id == author.id


def test_get_author_id_by_user_id_not_found(clean_database, test_client):
    """Verifica que get_author_id_by_user_id retorna None si no existe."""
    with test_client.application.app_context():
        service = DataSetService()
        author_id = service.get_author_id_by_user_id(99999)
        
        assert author_id is None


def test_size_service_bytes(test_client):
    """Verifica formato de bytes."""
    from app.modules.dataset.services import SizeService
    
    service = SizeService()
    result = service.get_human_readable_size(500)
    
    assert result == "500 bytes"


def test_size_service_kilobytes(test_client):
    """Verifica formato de kilobytes."""
    from app.modules.dataset.services import SizeService
    
    service = SizeService()
    result = service.get_human_readable_size(2048)
    
    assert "KB" in result
    assert "2" in result


def test_size_service_megabytes(test_client):
    """Verifica formato de megabytes."""
    from app.modules.dataset.services import SizeService
    
    service = SizeService()
    result = service.get_human_readable_size(5 * 1024 * 1024)
    
    assert "MB" in result
    assert "5" in result


def test_size_service_gigabytes(test_client):
    """Verifica formato de gigabytes."""
    from app.modules.dataset.services import SizeService
    
    service = SizeService()
    result = service.get_human_readable_size(3 * 1024 * 1024 * 1024)
    
    assert "GB" in result
    assert "3" in result


def test_dsmetadata_service_update(clean_database, test_client):
    """Verifica que DSMetaDataService.update funciona correctamente."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DSMetaDataService
        
        meta = DSMetaData(
            title="Original",
            description="Original desc",
            publication_type=PublicationType.NONE,
        )
        db.session.add(meta)
        db.session.commit()
        
        service = DSMetaDataService()
        service.update(meta.id, title="Modified", description="Modified desc")
        
        db.session.refresh(meta)
        
        assert meta.title == "Modified"
        assert meta.description == "Modified desc"


def test_dsmetadata_service_filter_by_doi(clean_database, test_client):
    """Verifica que DSMetaDataService.filter_by_doi encuentra el metadata."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DSMetaDataService
        
        meta = DSMetaData(
            title="DOI Meta",
            description="Test",
            publication_type=PublicationType.NONE,
            dataset_doi="10.5281/meta.555"
        )
        db.session.add(meta)
        db.session.commit()
        
        service = DSMetaDataService()
        found = service.filter_by_doi("10.5281/meta.555")
        
        assert found is not None
        assert found.id == meta.id


def test_dsmetadata_service_filter_by_doi_not_found(clean_database, test_client):
    """Verifica que DSMetaDataService.filter_by_doi retorna None si no existe."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DSMetaDataService
        
        service = DSMetaDataService()
        found = service.filter_by_doi("10.5281/nonexistent.000")
        
        assert found is None


class MockProfile:
    """Mock del perfil de usuario."""
    def __init__(self, name="Test", surname="User", affiliation="Test Affiliation", orcid="0000-0000-0000-0001"):
        self.name = name
        self.surname = surname
        self.affiliation = affiliation
        self.orcid = orcid


class MockUser:
    """Mock del usuario para tests de create_from_form."""
    def __init__(self, user_id, profile=None, temp_folder_path="/tmp/test"):
        self.id = user_id
        self.profile = profile or MockProfile()
        self._temp_folder = temp_folder_path
    
    def temp_folder(self):
        return self._temp_folder


class MockFileModelField:
    """Mock de un campo de FileModel del formulario."""
    def __init__(self, csv_filename, title=None, description=None):
        self.csv_filename = mock.MagicMock()
        self.csv_filename.data = csv_filename
        self._title = title
        self._description = description
    
    def get_fmmetadata(self):
        return {
            "csv_filename": self.csv_filename.data,
            "title": self._title,
            "description": self._description,
            "publication_type": None,
            "publication_doi": None,
            "tags": None,
            "csv_version": "1.0",
        }
    
    def get_authors(self):
        return []


class MockDataSetForm:
    """Mock del formulario DataSetForm."""
    def __init__(self, title="Test Dataset", description="Test Description", 
                 authors=None, file_models_data=None):
        self._title = title
        self._description = description
        self._authors = authors or []
        
        if file_models_data:
            self.file_models = [MockFileModelField(**fm) for fm in file_models_data]
        else:
            self.file_models = [MockFileModelField(csv_filename="test.csv")]
    
    def get_dsmetadata(self):
        return {
            "title": self._title,
            "description": self._description,
            "publication_type": "NONE",
            "publication_doi": None,
            "dataset_doi": None,
            "tags": None,
        }
    
    def get_authors(self):
        return self._authors


@pytest.fixture
def setup_temp_folder_with_file(test_client):
    """Fixture que crea un directorio temporal con un archivo CSV de prueba."""
    temp_folder = "/tmp/test_create_from_form"
    os.makedirs(temp_folder, exist_ok=True)
    
    csv_path = os.path.join(temp_folder, "test.csv")
    with open(csv_path, "w") as f:
        f.write("id,name,value\n1,test,100\n")
    
    yield temp_folder
    
    shutil.rmtree(temp_folder, ignore_errors=True)


def test_create_from_form_basic(clean_database, test_client, setup_temp_folder_with_file):
    """Test básico de create_from_form con datos mínimos."""

    user = User(email="form_test@example.com", password="1234")
    db.session.add(user)
    db.session.flush()
        
    profile = UserProfile(
    user_id=user.id,
        name="Test",
        surname="User",
        affiliation="Test Affiliation",
        orcid="0000-0000-0000-0001"
    )
    db.session.add(profile)
    db.session.commit()
    
    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile
    
    form = MockDataSetForm(
        title="Dataset From Form",
        description="Created via create_from_form",
        file_models_data=[{"csv_filename": "test.csv", "title": "Test File", "description": "File desc"}]
    )
    
    service = DataSetService()
    
    with mock.patch("app.utils.notifications.notify_followers_of_author"):
        dataset = service.create_from_form(form, mock_user)
    
    assert dataset is not None
    assert dataset.id is not None
    assert dataset.ds_meta_data.title == "Dataset From Form"
    assert dataset.ds_meta_data.description == "Created via create_from_form"
    assert len(dataset.file_models) == 1


def test_create_from_form_creates_concept_and_version(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que create_from_form crea DatasetConcept y DatasetVersion 1.0."""
    with test_client.application.app_context():
        from app.modules.dataset.models import DatasetConcept, DatasetVersion
        from app.modules.profile.models import UserProfile
        
        user = User(email="concept_test@example.com", password="1234")
        db.session.add(user)
        db.session.flush()
        
        profile = UserProfile(
            user_id=user.id,
            name="Concept",
            surname="Tester",
            affiliation="Test Org"
        )
        db.session.add(profile)
        db.session.commit()
        
        mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
        mock_user.profile = profile
        
        form = MockDataSetForm(title="Versioned Dataset", description="With concept")
        
        service = DataSetService()
        
        with mock.patch("app.utils.notifications.notify_followers_of_author"):
            dataset = service.create_from_form(form, mock_user)
        
        version = DatasetVersion.query.filter_by(dataset_id=dataset.id).first()
        
        assert version is not None
        assert version.version_major == 1
        assert version.version_minor == 0
        assert version.changelog == "Initial version"
        
        concept = DatasetConcept.query.get(version.concept_id)
        assert concept is not None
        assert concept.name == "Versioned Dataset"
        assert concept.conceptual_doi.startswith("concept-")


def test_create_from_form_reuses_author_by_user_id(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que create_from_form reutiliza autor existente por user_id."""
    
        
    user = User(email="reuse_author@example.com", password="1234")
    db.session.add(user)
    db.session.flush()
        
    profile = UserProfile(
        user_id=user.id,
        name="Existing",
        surname="Author"
    )
    db.session.add(profile)
    db.session.flush()
        
    existing_author = Author(name="Existing Author", user_id=user.id, affiliation="Existing Affiliation")
    db.session.add(existing_author)
    db.session.commit()
        
    author_count_before = Author.query.count()
        
    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile
        
    form = MockDataSetForm(title="Reuse Author Test", description="Test")
        
    service = DataSetService()
        
    with mock.patch("app.utils.notifications.notify_followers_of_author"):
        dataset = service.create_from_form(form, mock_user)
        
    author_count_after = Author.query.count()
        
    assert author_count_after == author_count_before
    assert dataset.ds_meta_data.author.id == existing_author.id

def test_create_from_form_creates_new_author_if_not_exists(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que create_from_form crea nuevo autor si no existe."""
   
    user = User(email="new_author@example.com", password="1234")
    db.session.add(user)
    db.session.flush()
        
    profile = UserProfile(
        user_id=user.id,
        name="New",
        surname="Author",
        affiliation="New Affiliation",
        orcid="0000-0000-0000-9999"
    )
    db.session.add(profile)
    db.session.commit()
        
    author_count_before = Author.query.count()
        
    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile
        
    form = MockDataSetForm(title="New Author Test", description="Test")
        
    service = DataSetService()
        
    with mock.patch("app.utils.notifications.notify_followers_of_author"):
        dataset = service.create_from_form(form, mock_user)
        
    author_count_after = Author.query.count()
        
    assert author_count_after == author_count_before + 1


def test_create_from_form_with_custom_authors(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que create_from_form usa autores del formulario si se proporcionan."""
    user = User(email="custom_author@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    profile = UserProfile(
        user_id=user.id,
        name="Default",
        surname="User"
    )
    db.session.add(profile)
    db.session.commit()

    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile

    form = MockDataSetForm(
        title="Custom Author Test",
        description="Test",
        authors=[{"name": "Custom Author", "affiliation": "Custom Org", "orcid": "0000-0000-0000-8888"}]
    )

    service = DataSetService()

    with mock.patch("app.utils.notifications.notify_followers_of_author"):
        dataset = service.create_from_form(form, mock_user)

    assert dataset.ds_meta_data.author.name == "Custom Author"
    assert dataset.ds_meta_data.author.affiliation == "Custom Org"


def test_create_from_form_multiple_file_models(clean_database, test_client):
    """Verifica que create_from_form crea múltiples FileModels."""
    temp_folder = "/tmp/test_multi_files"
    os.makedirs(temp_folder, exist_ok=True)

    for name in ["file1.csv", "file2.csv", "file3.csv"]:
        with open(os.path.join(temp_folder, name), "w") as f:
            f.write(f"id,value\n1,{name}\n")

    try:
        user = User(email="multi_files@example.com", password="1234")
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(
            user_id=user.id,
            name="Multi",
            surname="Files"
        )
        db.session.add(profile)
        db.session.commit()

        mock_user = MockUser(user_id=user.id, temp_folder_path=temp_folder)
        mock_user.profile = profile

        form = MockDataSetForm(
            title="Multi File Dataset",
            description="Test",
            file_models_data=[
                {"csv_filename": "file1.csv", "title": "File 1"},
                {"csv_filename": "file2.csv", "title": "File 2"},
                {"csv_filename": "file3.csv", "title": "File 3"},
            ]
        )

        service = DataSetService()

        with mock.patch("app.utils.notifications.notify_followers_of_author"):
            dataset = service.create_from_form(form, mock_user)

        assert len(dataset.file_models) == 3

        filenames = [fm.fm_meta_data.csv_filename for fm in dataset.file_models]
        assert "file1.csv" in filenames
        assert "file2.csv" in filenames
        assert "file3.csv" in filenames
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


def test_create_from_form_fmmetadata_inherits_from_dsmetadata(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que FMMetaData hereda title/description de DSMetaData si están vacíos."""
    user = User(email="inherit_meta@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    profile = UserProfile(
        user_id=user.id,
        name="Inherit",
        surname="Meta"
    )
    db.session.add(profile)
    db.session.commit()

    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile

    form = MockDataSetForm(
        title="Parent Dataset Title",
        description="Parent Dataset Description",
        file_models_data=[{"csv_filename": "test.csv", "title": None, "description": None}]
    )

    service = DataSetService()

    with mock.patch("app.utils.notifications.notify_followers_of_author"):
        dataset = service.create_from_form(form, mock_user)

    fm_meta = dataset.file_models[0].fm_meta_data
    assert fm_meta.title == "Parent Dataset Title"
    assert fm_meta.description == "Parent Dataset Description"


def test_create_from_form_rollback_on_error(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que create_from_form lanza excepción y hace rollback si falla."""
    user = User(email="rollback_test@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    profile = UserProfile(
        user_id=user.id,
        name="Rollback",
        surname="Test"
    )
    db.session.add(profile)
    db.session.commit()

    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile

    form = MockDataSetForm(
        title="Rollback Test",
        description="Test",
        file_models_data=[{"csv_filename": "nonexistent_file.csv"}]
    )

    service = DataSetService()

    with pytest.raises(Exception):
        service.create_from_form(form, mock_user)


def test_create_from_form_creates_hubfiles(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que create_from_form crea Hubfiles con checksum y size correcto."""
    user = User(email="hubfile_test@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    profile = UserProfile(
        user_id=user.id,
        name="Hubfile",
        surname="Test"
    )
    db.session.add(profile)
    db.session.commit()

    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile

    form = MockDataSetForm(
        title="Hubfile Test",
        description="Test",
        file_models_data=[{"csv_filename": "test.csv"}]
    )

    service = DataSetService()

    with mock.patch("app.utils.notifications.notify_followers_of_author"):
        dataset = service.create_from_form(form, mock_user)

    hubfile = Hubfile.query.filter_by(file_model_id=dataset.file_models[0].id).first()

    assert hubfile is not None
    assert hubfile.name == "test.csv"
    assert hubfile.checksum is not None
    assert hubfile.size > 0


def test_create_from_form_reuses_author_by_orcid(clean_database, test_client, setup_temp_folder_with_file):
    """Verifica que create_from_form reutiliza autor existente por ORCID."""
    user = User(email="orcid_reuse@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    profile = UserProfile(
        user_id=user.id,
        name="ORCID",
        surname="Test",
        orcid="0000-0000-0000-5555"
    )
    db.session.add(profile)
    db.session.flush()

    other_user = User(email="other@example.com", password="1234")
    db.session.add(other_user)
    db.session.flush()

    existing_author = Author(
        name="ORCID Author",
        orcid="0000-0000-0000-5555",
        user_id=other_user.id
    )
    db.session.add(existing_author)
    db.session.commit()

    mock_user = MockUser(user_id=user.id, temp_folder_path=setup_temp_folder_with_file)
    mock_user.profile = profile

    form = MockDataSetForm(
        title="ORCID Reuse Test",
        description="Test",
        authors=[{"name": "New Name", "affiliation": "New Affiliation", "orcid": "0000-0000-0000-5555"}]
    )

    service = DataSetService()

    with mock.patch("app.utils.notifications.notify_followers_of_author"):
        dataset = service.create_from_form(form, mock_user)

    assert dataset.ds_meta_data.author.id == existing_author.id


@pytest.fixture
def dataset_with_file_model(clean_database, test_client):
    """Fixture que crea un dataset con un FileModel para tests de move_file_models."""
    user = User(email="move_test@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    meta = DSMetaData(
        title="Move Test Dataset",
        description="Test",
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

    fm_meta = FMMetaData(
        csv_filename="move_test.csv",
        title="Move test file",
        description="File to move",
        csv_version="1.0",
        fm_metrics_id=fm_metrics.id
    )
    db.session.add(fm_meta)
    db.session.flush()

    fm = FileModel(data_set_id=ds.id, fm_meta_data_id=fm_meta.id)
    db.session.add(fm)
    db.session.flush()

    hubfile = Hubfile(name="move_test.csv", checksum="testsum", size=100, file_model_id=fm.id)
    db.session.add(hubfile)
    db.session.commit()

    yield {"user": user, "dataset": ds, "file_model": fm}

    shutil.rmtree("uploads", ignore_errors=True)


def test_move_file_models_basic(dataset_with_file_model, test_client):
    """Test básico de move_file_models moviendo un archivo."""
    data = dataset_with_file_model
    user = data["user"]
    dataset = data["dataset"]

    temp_folder = f"/tmp/test_move_{user.id}"
    os.makedirs(temp_folder, exist_ok=True)

    src_file = os.path.join(temp_folder, "move_test.csv")
    with open(src_file, "w") as f:
        f.write("id,value\n1,test\n")

    try:
        mock_user = mock.MagicMock()
        mock_user.id = user.id
        mock_user.temp_folder.return_value = temp_folder

        service = DataSetService()

        with mock.patch("app.modules.dataset.services.AuthenticationService") as mock_auth:
            mock_auth.return_value.get_authenticated_user.return_value = mock_user
            service.move_file_models(dataset)

        dest_dir = os.path.join("uploads", f"user_{user.id}", f"dataset_{dataset.id}")
        dest_file = os.path.join(dest_dir, "move_test.csv")

        assert os.path.exists(dest_file)
        assert not os.path.exists(src_file)  
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


def test_move_file_models_creates_destination_dir(dataset_with_file_model, test_client):
    """Verifica que move_file_models crea el directorio destino si no existe."""
    data = dataset_with_file_model
    user = data["user"]
    dataset = data["dataset"]

    temp_folder = f"/tmp/test_move_dir_{user.id}"
    os.makedirs(temp_folder, exist_ok=True)

    src_file = os.path.join(temp_folder, "move_test.csv")
    with open(src_file, "w") as f:
        f.write("id,value\n1,test\n")

    try:
        dest_dir = os.path.join("uploads", f"user_{user.id}", f"dataset_{dataset.id}")

        shutil.rmtree(dest_dir, ignore_errors=True)
        assert not os.path.exists(dest_dir)

        mock_user = mock.MagicMock()
        mock_user.id = user.id
        mock_user.temp_folder.return_value = temp_folder

        service = DataSetService()

        with mock.patch("app.modules.dataset.services.AuthenticationService") as mock_auth:
            mock_auth.return_value.get_authenticated_user.return_value = mock_user
            service.move_file_models(dataset)

        assert os.path.exists(dest_dir)
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


def test_move_file_models_skips_missing_file(dataset_with_file_model, test_client):
    """Verifica que move_file_models no falla si el archivo origen no existe."""
    data = dataset_with_file_model
    user = data["user"]
    dataset = data["dataset"]

    temp_folder = f"/tmp/test_move_missing_{user.id}"
    os.makedirs(temp_folder, exist_ok=True)


    try:
        mock_user = mock.MagicMock()
        mock_user.id = user.id
        mock_user.temp_folder.return_value = temp_folder

        service = DataSetService()

        with mock.patch("app.modules.dataset.services.AuthenticationService") as mock_auth:
            mock_auth.return_value.get_authenticated_user.return_value = mock_user
            service.move_file_models(dataset)  
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


def test_move_file_models_renames_duplicate_file(clean_database, test_client):
    """Verifica que move_file_models renombra archivo si ya existe en destino."""
    user = User(email="rename_test@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    meta = DSMetaData(
        title="Rename Test",
        description="Test",
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

    fm_meta = FMMetaData(
        csv_filename="duplicate.csv",
        title="Duplicate file",
        description="File with duplicate name",
        csv_version="1.0",
        fm_metrics_id=fm_metrics.id
    )
    db.session.add(fm_meta)
    db.session.flush()

    fm = FileModel(data_set_id=ds.id, fm_meta_data_id=fm_meta.id)
    db.session.add(fm)
    db.session.flush()

    hubfile = Hubfile(name="duplicate.csv", checksum="testsum", size=100, file_model_id=fm.id)
    db.session.add(hubfile)
    db.session.commit()

    temp_folder = f"/tmp/test_rename_{user.id}"
    os.makedirs(temp_folder, exist_ok=True)

    src_file = os.path.join(temp_folder, "duplicate.csv")
    with open(src_file, "w") as f:
        f.write("new,data\n1,new\n")

    dest_dir = os.path.join("uploads", f"user_{user.id}", f"dataset_{ds.id}")
    os.makedirs(dest_dir, exist_ok=True)
    existing_file = os.path.join(dest_dir, "duplicate.csv")
    with open(existing_file, "w") as f:
        f.write("old,data\n1,old\n")

    try:
        mock_user = mock.MagicMock()
        mock_user.id = user.id
        mock_user.temp_folder.return_value = temp_folder

        service = DataSetService()

        with mock.patch("app.modules.dataset.services.AuthenticationService") as mock_auth:
            mock_auth.return_value.get_authenticated_user.return_value = mock_user
            service.move_file_models(ds)

        renamed_file = os.path.join(dest_dir, "duplicate (1).csv")
        assert os.path.exists(renamed_file)

        assert os.path.exists(existing_file)

        db.session.refresh(fm_meta)
        assert fm_meta.csv_filename == "duplicate (1).csv"

        db.session.refresh(hubfile)
        assert hubfile.name == "duplicate (1).csv"
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)
        shutil.rmtree("uploads", ignore_errors=True)


def test_move_file_models_multiple_duplicates(clean_database, test_client):
    """Verifica que move_file_models maneja múltiples archivos duplicados."""
    user = User(email="multi_dup@example.com", password="1234")
    db.session.add(user)
    db.session.flush()

    meta = DSMetaData(
        title="Multi Duplicate Test",
        description="Test",
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

    fm_meta = FMMetaData(
        csv_filename="multi.csv",
        title="Multi file",
        description="File",
        csv_version="1.0",
        fm_metrics_id=fm_metrics.id
    )
    db.session.add(fm_meta)
    db.session.flush()

    fm = FileModel(data_set_id=ds.id, fm_meta_data_id=fm_meta.id)
    db.session.add(fm)
    db.session.commit()

    temp_folder = f"/tmp/test_multi_dup_{user.id}"
    os.makedirs(temp_folder, exist_ok=True)

    src_file = os.path.join(temp_folder, "multi.csv")
    with open(src_file, "w") as f:
        f.write("new,data\n")

    dest_dir = os.path.join("uploads", f"user_{user.id}", f"dataset_{ds.id}")
    os.makedirs(dest_dir, exist_ok=True)

    with open(os.path.join(dest_dir, "multi.csv"), "w") as f:
        f.write("original")
    with open(os.path.join(dest_dir, "multi (1).csv"), "w") as f:
        f.write("dup1")
    with open(os.path.join(dest_dir, "multi (2).csv"), "w") as f:
        f.write("dup2")

    try:
        mock_user = mock.MagicMock()
        mock_user.id = user.id
        mock_user.temp_folder.return_value = temp_folder

        service = DataSetService()

        with mock.patch("app.modules.dataset.services.AuthenticationService") as mock_auth:
            mock_auth.return_value.get_authenticated_user.return_value = mock_user
            service.move_file_models(ds)

        assert os.path.exists(os.path.join(dest_dir, "multi (3).csv"))

        db.session.refresh(fm_meta)
        assert fm_meta.csv_filename == "multi (3).csv"
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)
        shutil.rmtree("uploads", ignore_errors=True)


def test_move_file_models_preserves_content(dataset_with_file_model, test_client):
    """Verifica que move_file_models preserva el contenido del archivo."""
    data = dataset_with_file_model
    user = data["user"]
    dataset = data["dataset"]

    temp_folder = f"/tmp/test_content_{user.id}"
    os.makedirs(temp_folder, exist_ok=True)

    original_content = "id,name,value\n1,test,100\n2,test2,200\n"
    src_file = os.path.join(temp_folder, "move_test.csv")
    with open(src_file, "w") as f:
        f.write(original_content)

    try:
        mock_user = mock.MagicMock()
        mock_user.id = user.id
        mock_user.temp_folder.return_value = temp_folder

        service = DataSetService()

        with mock.patch("app.modules.dataset.services.AuthenticationService") as mock_auth:
            mock_auth.return_value.get_authenticated_user.return_value = mock_user
            service.move_file_models(dataset)

        dest_file = os.path.join("uploads", f"user_{user.id}", f"dataset_{dataset.id}", "move_test.csv")

        with open(dest_file, "r") as f:
            moved_content = f.read()

        assert moved_content == original_content
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


#He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código.
#La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.