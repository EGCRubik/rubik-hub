import pytest

from app import db
from app.modules.dataset.services import DataSetService
from app.modules.dataset.models import DSMetrics, DSMetaData, UVLDataset, PublicationType
from app.modules.auth.models import User


@pytest.fixture(scope="module")
def test_client(test_client):
	# reuse application test_client fixture but ensure app context
	with test_client.application.app_context():
		yield test_client


def test_get_number_of_downloads(clean_database, test_client):
	"""Verifica que DataSetService.get_number_of_downloads devuelve el valor almacenado en DSMetrics."""
	with test_client.application.app_context():
		# Crear usuario necesario para la FK
		user = User(email="user1@example.com", password="1234")
		db.session.add(user)
		db.session.flush()

		# Crear métricas con número de descargas concreto
		metrics = DSMetrics(number_of_models="1", number_of_features="10", number_of_downloads=7)
		db.session.add(metrics)
		db.session.flush()

		# Crear metadatos que apunten a las métricas
		dsmeta = DSMetaData(
			deposition_id=1,
			title="Test Dataset",
			description="Description",
			publication_type=PublicationType.NONE,
			publication_doi=None,
			dataset_doi=None,
			tags="",
			ds_metrics_id=metrics.id,
		)
		db.session.add(dsmeta)
		db.session.flush()

		# Crear dataset asociado al usuario y a los metadatos
		dataset = UVLDataset(user_id=user.id, ds_meta_data_id=dsmeta.id)
		db.session.add(dataset)
		db.session.commit()

		# Llamar al servicio y comprobar el resultado
		service = DataSetService()
		downloads = service.get_number_of_downloads(dataset.id)

		assert downloads == 7, f"Expected 7 downloads, got {downloads}"
