import io
import json
import os
import sys
import types

import pytest

from app.modules.fakenodo import routes as fakenodo_routes
from app.modules.fakenodo.services import FakenodoService

# Use the top-level `test_client` fixture from the project's conftest.
# Do not re-wrap it in an app context here because the project fixture
# already yields a client inside the application context. Creating
# additional contexts in the module caused mismatched app-context
# teardown errors.


def test_create_list_get_delete(tmp_path, test_client):
	"""Verifica crear, listar, obtener y eliminar deposiciones en el servicio fakenodo."""
	with test_client.application.app_context():
		svc = FakenodoService(working_dir=str(tmp_path))

		# Create
		rec = svc.create_deposition({"title": "Test Dep"})
		assert isinstance(rec, dict)
		assert rec["id"] == 1
		assert rec["metadata"]["title"] == "Test Dep"

		# List
		all_recs = svc.list_depositions()
		assert isinstance(all_recs, list)
		assert len(all_recs) == 1

		# Get
		got = svc.get_deposition(1)
		assert got is not None
		assert got["id"] == 1

		# Delete
		assert svc.delete_deposition(1) is True
		assert svc.get_deposition(1) is None
		# Deleting non-existing returns False
		assert svc.delete_deposition(999) is False


def test_upload_publish_versions_and_get_doi(tmp_path, test_client):
	"""Verifica upload de ficheros, publicación y versiones/DOI."""
	with test_client.application.app_context():
		svc = FakenodoService(working_dir=str(tmp_path))

		rec = svc.create_deposition({"title": "WithFiles"})
		did = rec["id"]

		# Upload a file
		file_rec = svc.upload_file(did, "file1.txt", b"hello")
		assert file_rec is not None
		assert file_rec["name"] == "file1.txt"
		assert file_rec["size"] == 5

		# Publish -> version 1
		version = svc.publish_deposition(did)
		assert version is not None
		assert version["version"] == 1
		doi = svc.get_doi(did)
		assert doi is not None and str(did) in doi

		# Publishing again without changes should return same version
		same = svc.publish_deposition(did)
		assert same["version"] == 1

		# Upload another file (marks dirty) and publish -> new version
		svc.upload_file(did, "file2.txt", b"bye")
		v2 = svc.publish_deposition(did)
		assert v2["version"] == 2


def test_update_metadata_and_list_versions(tmp_path, test_client):
	"""Verifica actualización de metadata y listado de versiones."""
	with test_client.application.app_context():
		svc = FakenodoService(working_dir=str(tmp_path))

		rec = svc.create_deposition({"title": "MetaOld"})
		did = rec["id"]
		svc.publish_deposition(did)

		# Update metadata (should not mark dirty)
		svc.update_metadata(did, {"title": "MetaNew"})
		got = svc.get_deposition(did)
		assert got["metadata"]["title"] == "MetaNew"

		versions = svc.list_versions(did)
		assert isinstance(versions, list)


def test_create_new_deposition_alias_and_get_doi_none(tmp_path, test_client):
	"""Verifica alias create_new_deposition y comportamiento de get_doi cuando no hay versiones."""
	with test_client.application.app_context():
		svc = FakenodoService(working_dir=str(tmp_path))

		rec = svc.create_new_deposition({"a": 1})
		did = rec["id"]
		# Before publish, get_doi should be None
		assert svc.get_doi(did) is None
		# After publish, DOI exists
		svc.publish_deposition(did)
		assert svc.get_doi(did) is not None

def _patch_service(tmp_path, monkeypatch):
    svc = FakenodoService(working_dir=str(tmp_path))
    # ensure the routes module uses this instance
    monkeypatch.setattr(fakenodo_routes, "service", svc)
    return svc


def test_create_list_get_delete_routes(tmp_path, test_client, monkeypatch):
    svc = _patch_service(tmp_path, monkeypatch)

    # Create via HTTP
    resp = test_client.post(
        "/fakenodo/deposit/depositions",
        json={"metadata": {"title": "Routed"}},
    )
    assert resp.status_code == 201
    created = resp.get_json()
    did = created["id"]

    # List
    list_resp = test_client.get("/fakenodo/deposit/depositions")
    assert list_resp.status_code == 200
    body = list_resp.get_json()
    assert any(r.get("id") == did for r in body.get("depositions", []))

    # Get
    get_resp = test_client.get(f"/fakenodo/deposit/depositions/{did}")
    assert get_resp.status_code == 200
    assert get_resp.get_json().get("id") == did

    # Delete
    del_resp = test_client.delete(f"/fakenodo/deposit/depositions/{did}")
    assert del_resp.status_code == 200
    # Confirm gone
    get2 = test_client.get(f"/fakenodo/deposit/depositions/{did}")
    assert get2.status_code == 404


def test_upload_publish_and_versions_routes(tmp_path, test_client, monkeypatch):
    svc = _patch_service(tmp_path, monkeypatch)

    # Create
    rec = svc.create_deposition({"title": "Files"})
    did = rec["id"]

    # Upload file via multipart/form-data
    data = {
        "file": (io.BytesIO(b"hello world"), "hello.txt"),
    }
    upload_resp = test_client.post(f"/fakenodo/deposit/depositions/{did}/files", data=data, content_type="multipart/form-data")
    assert upload_resp.status_code == 201
    file_rec = upload_resp.get_json()
    assert file_rec["name"] == "hello.txt"

    # Publish
    pub = test_client.post(f"/fakenodo/deposit/depositions/{did}/actions/publish")
    assert pub.status_code == 202
    version = pub.get_json()
    assert version["version"] == 1

    # List versions route
    versions_resp = test_client.get(f"/fakenodo/deposit/depositions/{did}/versions")
    assert versions_resp.status_code == 200
    vs = versions_resp.get_json().get("versions")
    assert isinstance(vs, list) and len(vs) >= 1


def test_update_metadata_route(tmp_path, test_client, monkeypatch):
    svc = _patch_service(tmp_path, monkeypatch)

    rec = svc.create_deposition({"title": "Before"})
    did = rec["id"]

    # Patch metadata via route
    patch_resp = test_client.patch(f"/fakenodo/deposit/depositions/{did}/metadata", json={"metadata": {"title": "After"}})
    assert patch_resp.status_code == 200
    body = patch_resp.get_json()
    assert body["id"] == did
    assert body["metadata"]["title"] == "After"


def test_test_endpoint_callable(tmp_path, test_client, monkeypatch):
    svc = _patch_service(tmp_path, monkeypatch)
    # route calls service.test_full_connection(); add a dummy
    setattr(svc, "test_full_connection", lambda: ("pong", 200))
    monkeypatch.setattr(fakenodo_routes, "service", svc)

    resp = test_client.get("/fakenodo/test")
    assert resp.status_code == 200
    # flask will return the tuple content as response body
    assert resp.get_data(as_text=True) == 'pong'


def test_dataset_create_and_publish_routes(tmp_path, test_client, monkeypatch):
    """Integration-style tests for dataset-related routes by injecting a fake dataset services module."""
    svc = _patch_service(tmp_path, monkeypatch)

    # Prepare a fake dataset object matching expectations in the route
    class FakeMeta:
        def __init__(self):
            self.title = "FM"
            self.dataset_doi = None
            self.deposition_id = None

    class FakeDataset:
        def __init__(self, user_id=1):
            self.id = 1
            self.user_id = user_id
            self.ds_meta_data = FakeMeta()
            # routes expect a ds_meta_data_id attribute on the dataset
            self.ds_meta_data_id = 1
            # and the meta itself may have an id
            self.ds_meta_data.id = 1
            self.feature_models = []
            self.file_models = []

    fake_ds = FakeDataset(user_id=1)

    # Create a fake DataSetService module and inject into sys.modules so route's import finds it
    mod_name = "app.modules.dataset.services"
    fake_mod = types.ModuleType(mod_name)

    class FakeDataSetService:
        def __init__(self):
            class Repo:
                @staticmethod
                def get_by_id(_id):
                    return fake_ds if _id == 1 else None

            self.repository = Repo()

        def update_dsmetadata(self, ds_meta_id, deposition_id=None, dataset_doi=None):
            # simulate updating meta
            fake_ds.ds_meta_data.deposition_id = deposition_id or fake_ds.ds_meta_data.deposition_id
            fake_ds.ds_meta_data.dataset_doi = dataset_doi or fake_ds.ds_meta_data.dataset_doi

    fake_mod.DataSetService = FakeDataSetService

    # Inject the fake module (back up real if present)
    real_mod = sys.modules.get(mod_name)
    sys.modules[mod_name] = fake_mod

    try:
        # Log in as the default test user (created by project conftest)
        login = test_client.post("/login", data={"email": "test@example.com", "password": "test1234"})
        assert login.status_code in (200, 302)

        # Call create_dataset_deposition -> should redirect on success
        resp = test_client.post("/fakenodo/dataset/1/create", follow_redirects=False)
        assert resp.status_code in (302, 200)

        # Ensure service created a deposition and ds metadata was updated
        assert fake_ds.ds_meta_data.deposition_id is not None

        # Now test publish_dataset_deposition: ensure deposition exists
        dep_id = fake_ds.ds_meta_data.deposition_id
        assert dep_id is not None

        # Call publish route
        resp2 = test_client.post("/fakenodo/dataset/1/publish", follow_redirects=False)
        assert resp2.status_code in (302, 200)
    finally:
        # restore real module
        if real_mod is not None:
            sys.modules[mod_name] = real_mod
        else:
            del sys.modules[mod_name]


