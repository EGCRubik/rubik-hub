import pytest

from app import db
from app.modules.fakenodo.models import Fakenodo
from app.modules.fakenodo.services import FakenodoService

service = FakenodoService()


def _make_dataset_stub(id: int = 1, title: str = "Stub Title", desc: str = "Stub Description", tags: str = "tag1,tag2"):
    class Meta:
        def __init__(self):
            self.title = title
            self.description = desc
            self.tags = tags

    class DS:
        def __init__(self):
            self.id = id
            self.ds_meta_data = Meta()

    return DS()


def _make_fm_stub(name: str = "file.csv", path: str = "/tmp/file.csv"):
    class HubFile:
        def __init__(self):
            self.name = name
            self.path = path

    class FMStub:
        def __init__(self):
            self.files = [HubFile()]
            self.fm_meta_data = None

    return FMStub()


def test_service_create_new_deposition_creates_db_record(test_client):
    ds = _make_dataset_stub(id=123)

    resp = service.create_new_deposition(ds)
    assert isinstance(resp, dict)
    dep_id = resp.get("id")
    assert dep_id is not None

    dep = Fakenodo.query.get(dep_id)
    assert dep is not None
    assert isinstance(dep.meta_data, dict)
    assert dep.meta_data.get("title") == ds.ds_meta_data.title
    assert dep.meta_data.get("dataset_id") == ds.id

    db.session.delete(dep)
    db.session.commit()


def test_service_upload_file_appends_meta_files(test_client):
    dep = Fakenodo(meta_data={})
    db.session.add(dep)
    db.session.commit()

    ds = _make_dataset_stub(id=999)
    fm = _make_fm_stub(name="example.csv", path="/uploads/example.csv")

    result = service.upload_file(ds, dep.id, fm)
    assert result.get("status") == "completed"

    db.session.refresh(dep)
    files = dep.meta_data.get("files", [])
    assert len(files) == 1
    assert files[0]["file_name"] == "example.csv"
    assert files[0]["file_type"] == "text/csv"

    db.session.delete(dep)
    db.session.commit()


def test_service_publish_and_get_doi(test_client):
    dep = Fakenodo(meta_data={})
    db.session.add(dep)
    db.session.commit()

    pub = service.publish_deposition(dep.id)
    assert pub.get("submitted") is True
    assert isinstance(pub.get("doi"), str) and pub.get("doi")

    db.session.refresh(dep)
    assert dep.status == "published"
    assert isinstance(dep.doi, str) and dep.doi

    doi = service.get_doi(dep.id)
    assert doi == dep.doi

    db.session.delete(dep)
    db.session.commit()


def test_service_append_version_updates_versions_and_dataset_version(test_client):
    dep = Fakenodo(meta_data={})
    db.session.add(dep)
    db.session.commit()

    updated = service.append_version(deposition_id=dep.id, version_major=1, version_minor=1, doi="10.fake/1.1")
    assert isinstance(updated, dict)
    assert updated.get("dataset_version") == "1.1"
    assert isinstance(updated.get("versions"), list)
    assert updated["versions"][0]["version"] == "1.1"
    assert updated["versions"][0]["doi"] == "10.fake/1.1"

    db.session.delete(dep)
    db.session.commit()


def test_service_set_dataset_version_only(test_client):
    dep = Fakenodo(meta_data={})
    db.session.add(dep)
    db.session.commit()

    updated = service.set_dataset_version(deposition_id=dep.id, version_major=2, version_minor=0)
    assert isinstance(updated, dict)
    assert updated.get("dataset_version") == "2.0"
    assert updated.get("versions") in (None, [])

    db.session.delete(dep)
    db.session.commit()


def test_service_get_by_doi_returns_record_dict(test_client):
    dep = Fakenodo(meta_data={})
    db.session.add(dep)
    db.session.commit()

    pub = service.publish_deposition(dep.id)
    doi = pub.get("doi")
    assert doi

    rec = service.get_by_doi(doi)
    assert isinstance(rec, dict)
    assert rec.get("id") == dep.id
    assert rec.get("doi") == doi

    db.session.delete(dep)
    db.session.commit()


def test_fakenodo_test_route_ok(test_client):
    resp = test_client.get("/fakenodo/test")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("success") is True
