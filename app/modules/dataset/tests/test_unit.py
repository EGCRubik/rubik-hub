
import pytest

from app import db
from app.modules.dataset.services import DataSetService
from app.modules.dataset.models import TabularDataset, PublicationType, DSMetaData, Download
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
	