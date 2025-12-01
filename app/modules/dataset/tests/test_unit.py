
import pytest

from app import db
from app.modules.dataset.services import DataSetService
from app.modules.dataset.models import TabularDataset, PublicationType, DSMetaData, Download, DatasetConcept, DatasetVersion
from app.modules.fileModel.models import FileModel, FMMetaData, FMMetrics
from app.modules.auth.models import User

from datetime import datetime, timezone, timedelta


@pytest.fixture(scope="module")
def test_client(test_client):
	# reuse application test_client fixture but ensure app context
	with test_client.application.app_context():
		yield test_client


def test_get_number_of_downloads(clean_database, test_client):
	"""Verifica que DataSetService.get_number_of_downloads devuelve el valor almacenado en FMMetrics."""
	with test_client.application.app_context():
		# Crear usuario necesario para la FK
		user = User(email="user1@example.com", password="1234")
		db.session.add(user)
		db.session.flush()

		# Crear DSMetaData requerido por TabularDataset
		dsmetadata = DSMetaData(title="DS Title", description="DS Desc", publication_type=PublicationType.NONE)
		db.session.add(dsmetadata)
		db.session.flush()

		# Crear dataset asociado al usuario y a los metadatos
		dataset = TabularDataset(user_id=user.id, ds_meta_data_id=dsmetadata.id)
		db.session.add(dataset)
		db.session.flush()

		# Crear métricas con número de descargas concreto
		fmMetrics = FMMetrics()
		db.session.add(fmMetrics)
		db.session.flush()

		# Crear metadatos que apunten a las métricas
		fmMetaData = FMMetaData(
			csv_filename="data.csv",
			title="Test Data",
			description="Test Description",
			fm_metrics_id=fmMetrics.id,
		)
		db.session.add(fmMetaData)
		db.session.flush()

		# Crear FileModel y asociarlo al dataset
		fileModel = FileModel(data_set_id=dataset.id, fm_meta_data_id=fmMetaData.id)
		db.session.add(fileModel)
		db.session.flush()

		# Commit final
		db.session.commit()

		for _ in range(7):
			download = Download(dataset_id=dataset.id)
			db.session.add(download)
		db.session.commit()

		# Llamar al servicio y comprobar el resultado
		service = DataSetService()
		downloads = service.get_number_of_downloads(dataset.id)

		assert downloads == 7, f"Expected 7 downloads, got {downloads}"


def test_update_download_count_increments(clean_database, test_client):
	"""Verifica que DataSetService.update_download_count incrementa number_of_downloads en 1."""
	with test_client.application.app_context():
		# Crear usuario necesario para la FK
		user = User(email="user2@example.com", password="1234")
		db.session.add(user)
		db.session.flush()

		# Crear DSMetaData requerido por TabularDataset
		dsmetadata = DSMetaData(title="DS Title 2", description="DS Desc 2", publication_type=PublicationType.NONE)
		db.session.add(dsmetadata)
		db.session.flush()

		# Crear dataset asociado al usuario y a los metadatos
		dataset = TabularDataset(user_id=user.id, ds_meta_data_id=dsmetadata.id)
		db.session.add(dataset)
		db.session.flush()

		# Crear métricas con número de descargas concreto
		fmMetrics = FMMetrics()
		db.session.add(fmMetrics)
		db.session.flush()

		# Crear metadatos que apunten a las métricas
		fmMetaData = FMMetaData(
			csv_filename="data2.csv",
			title="Test Data 2",
			description="Test Description 2",
			fm_metrics_id=fmMetrics.id,
		)
		db.session.add(fmMetaData)
		db.session.flush()

		# Crear FileModel y asociarlo al dataset
		fileModel = FileModel(data_set_id=dataset.id, fm_meta_data_id=fmMetaData.id)
		db.session.add(fileModel)
		db.session.flush()

		for _ in range(5):
			download = Download(dataset_id=dataset.id)
			db.session.add(download)
		db.session.flush()

		# Commit final
		db.session.commit()

		# Llamar al servicio para incrementar el contador
		service = DataSetService()
		service.update_download_count(dataset.id)

		# Refrescar las métricas desde la DB y comprobar el valor
		assert service.get_number_of_downloads(dataset.id) == 6, f"Expected 6 downloads after increment, got {service.get_number_of_downloads(dataset.id)}"

def test_get_top_downloaded_last_week(clean_database, test_client):
	"""Verifica que DataSetService.get_top_downloaded_last_week devuelve los 3 datasets más descargados en la última semana."""
	with test_client.application.app_context():
		user = User(email="user3@example.com", password="1234")
		db.session.add(user)
		db.session.flush()

		two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
		twelve_days_ago = datetime.now(timezone.utc) - timedelta(days=12)

		datasets = []
		for i in range(1, 11):  # 1..10
			dsmd = DSMetaData(title=f"DS{i}", description=f"Desc {i}", publication_type=PublicationType.NONE)
			db.session.add(dsmd)
			db.session.flush()

			ds = TabularDataset(user_id=user.id, ds_meta_data_id=dsmd.id)
			db.session.add(ds)
			db.session.flush()

			# Create downloads: dataset 10 older than a week; others recent
			count = i
			when = twelve_days_ago if i == 10 else two_days_ago
			for _ in range(count):
				db.session.add(Download(dataset_id=ds.id, download_date=when))

			datasets.append(ds)

		db.session.commit()

		service = DataSetService()
		top3 = service.get_top_downloaded_last_week(limit=3)

		assert len(top3) == 3, f"Expected 3 datasets, got {len(top3)}"
		# Verify order and specific datasets by title (9,8,7)
		titles = [d.ds_meta_data.title for d in top3]
		assert titles == ["DS9", "DS8", "DS7"], f"Unexpected order: {titles}"


def create_dataset(user_email, title="Test DS"):
    """Utility para crear un dataset mínimo válido."""
    user = User(email=user_email, password="1234")
    db.session.add(user)
    db.session.flush()

    meta = DSMetaData(
        title=title,
        description="DS description",
        publication_type=PublicationType.NONE
    )
    db.session.add(meta)
    db.session.flush()

    ds = TabularDataset(
        user_id=user.id,
        ds_meta_data_id=meta.id
    )
    db.session.add(ds)
    db.session.flush()

    return user, meta, ds


def test_create_version_1_0(clean_database, test_client):
    """Verifica que se puede crear una versión 1.0 asociada a un concepto."""
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest1@example.com", "Dataset V1")

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

        assert v1.id is not None, "Version 1.0 did not persist"
        assert v1.version_major == 1
        assert v1.version_minor == 0
        assert v1.dataset_id == ds.id
        assert concept.versions[0].version_doi == "10.concept.1.v1"


def test_multiple_versions_same_dataset(clean_database, test_client):
    """Verifica que un dataset puede tener varias versiones sin UNIQUE(dataset_id)."""
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest2@example.com", "Dataset V2")

        concept = DatasetConcept(
            conceptual_doi="10.concept.2",
            name="Concept 2"
        )
        db.session.add(concept)
        db.session.flush()

        versions = [
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=1),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=0),
        ]

        for v in versions:
            db.session.add(v)

        db.session.commit()

        assert len(concept.versions) == 3, f"Expected 3 versions, got {len(concept.versions)}"

def test_unique_version_number_constraint(clean_database, test_client):
    """Verifica que NO se permiten dos versiones con {concept_id,major,minor} iguales."""
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest3@example.com", "Dataset V3")

        concept = DatasetConcept(conceptual_doi="10.concept.3", name="Concept 3")
        db.session.add(concept)
        db.session.flush()

        # Create 1.0
        v1 = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0)
        db.session.add(v1)
        db.session.commit()

        # Attempt to create duplicate 1.0
        dup = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0)
        db.session.add(dup)

        with pytest.raises(Exception):
            db.session.commit()


def test_latest_version(clean_database, test_client):
    """Verifica que latest_version devuelve la versión mayor correcta."""
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest4@example.com", "Dataset V4")

        concept = DatasetConcept(conceptual_doi="10.concept.4", name="Concept 4")
        db.session.add(concept)
        db.session.flush()

        versions = [
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=1),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=0),
            DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=3),
        ]

        for v in versions:
            db.session.add(v)

        db.session.commit()

        latest = concept.latest_version()

        assert latest.version_major == 2
        assert latest.version_minor == 3
        assert latest.dataset_id == ds.id


def test_concept_relationship(clean_database, test_client):
    """Verifica que DatasetConcept -> DatasetVersion genera la relación correcta."""
    with test_client.application.app_context():

        user, meta, ds = create_dataset("vtest5@example.com", "Dataset V5")

        concept = DatasetConcept(conceptual_doi="10.concept.5", name="Concept 5")
        db.session.add(concept)
        db.session.flush()

        v10 = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=1, version_minor=0)
        v20 = DatasetVersion(concept_id=concept.id, dataset_id=ds.id, version_major=2, version_minor=0)

        db.session.add_all([v10, v20])
        db.session.commit()

        assert len(concept.versions) == 2
        assert (concept.versions[0].version_major, concept.versions[1].version_major) == (1,2)