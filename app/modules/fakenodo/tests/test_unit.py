import io
import os
import re

import pytest

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.fakenodo.models import Fakenodo
from app.modules.fakenodo.services import FakenodoService


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        yield test_client


def create_dataset_for_user(user):
    meta = DSMetaData(title="T", description="D", publication_type=PublicationType.NONE)
    db.session.add(meta)
    db.session.commit()

    ds = DataSet(user_id=user.id, ds_meta_data_id=meta.id)
    db.session.add(ds)
    db.session.commit()
    return ds


def test_fakenodo_service_flow(clean_database, test_client, tmp_path, monkeypatch):
    """
    Test the FakenodoService end-to-end flow without using HTTP:
    create deposition, upload file, publish, check DOI/versions and delete.
    """
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))

    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None

    ds = create_dataset_for_user(user)

    service = FakenodoService()

    rec = service.create_new_deposition({"title": "My Dep", "description": "desc", "dataset_id": ds.id})
    assert "id" in rec
    dep_id = rec["id"]

    file_record = service.upload_file(dep_id, "hello.txt", b"hello world")
    assert file_record and file_record.get("filename") == "hello.txt"

    published = service.publish_deposition(dep_id)
    assert published and published.get("doi") is not None
    doi = published.get("doi")
    assert re.match(r"^10\.1234/fake-doi-\d+\.v\d+$", doi)

    versions = service.list_versions(dep_id)
    assert isinstance(versions, list) and len(versions) >= 1

    got = service.get_doi(dep_id)
    assert got == doi

    meta_path = os.path.join(os.getenv("WORKING_DIR"), "uploads", "fakenodo", str(dep_id), "meta.json")
    assert os.path.exists(meta_path)

    ok = service.delete_deposition(dep_id)
    assert ok
    assert Fakenodo.query.get(dep_id) is None


def test_fakenodo_routes_endpoints(clean_database, test_client, tmp_path, monkeypatch):
    """
    Test the HTTP routes that wrap the service: create, get, upload file, publish, versions, delete.
    """
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))

    user = User.query.filter_by(email="test@example.com").first()
    ds = create_dataset_for_user(user)

    resp = test_client.post(
        "/fakenodo/deposit/depositions", json={"metadata": {"title": "HTTP Dep", "description": "x", "dataset_id": ds.id}}
    )
    assert resp.status_code == 201
    data = resp.get_json()
    dep_id = data.get("id")

    resp = test_client.get(f"/fakenodo/deposit/depositions/{dep_id}")
    assert resp.status_code == 200

    data = {"name": "upload.txt"}
    file_stream = (io.BytesIO(b"content"), "upload.txt")
    resp = test_client.post(
        f"/fakenodo/deposit/depositions/{dep_id}/files",
        data={"name": "upload.txt", "file": file_stream},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 201

    resp = test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/actions/publish")
    assert resp.status_code == 202
    published = resp.get_json()
    assert published.get("doi") is not None

    resp = test_client.get(f"/fakenodo/deposit/depositions/{dep_id}/versions")
    assert resp.status_code == 200
    versions = resp.get_json().get("versions")
    assert isinstance(versions, list)

    resp = test_client.delete(f"/fakenodo/deposit/depositions/{dep_id}")
    assert resp.status_code == 200