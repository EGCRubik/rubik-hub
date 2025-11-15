
import pytest

from app import db
from app.modules.dataset.services import DataSetService
from app.modules.dataset.models import TabularDataset, PublicationType, DSMetaData
from app.modules.fileModel.models import FileModel, FMMetaData, FMMetrics
from app.modules.auth.models import User


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
		fmMetrics = FMMetrics(number_of_downloads=7)
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

		# Llamar al servicio y comprobar el resultado
		service = DataSetService()
		downloads = service.get_number_of_downloads(dataset.id)

		assert downloads == 7, f"Expected 7 downloads, got {downloads}"
