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
    """Test set_dataset_version updates dataset_version and also appends to versions list by default."""
    dep = Fakenodo(meta_data={})
    db.session.add(dep)
    db.session.commit()

    updated = service.set_dataset_version(deposition_id=dep.id, version_major=2, version_minor=0)
    assert isinstance(updated, dict)
    assert updated.get("dataset_version") == "2.0"
    
    dep_reloaded = db.session.get(Fakenodo, dep.id)
    versions = (dep_reloaded.meta_data or {}).get("versions", [])
    assert len(versions) >= 1
    assert versions[-1].get("version") == "2.0"

    db.session.delete(dep_reloaded)
    db.session.commit()


def test_service_set_dataset_version_without_appending(test_client):
    """Test set_dataset_version with append_to_versions=False."""
    dep = Fakenodo(meta_data={})
    db.session.add(dep)
    db.session.commit()

    updated = service.set_dataset_version(deposition_id=dep.id, version_major=3, version_minor=1, append_to_versions=False)
    assert isinstance(updated, dict)
    assert updated.get("dataset_version") == "3.1"
    
    dep_reloaded = db.session.get(Fakenodo, dep.id)
    versions = (dep_reloaded.meta_data or {}).get("versions", [])
    assert versions == []

    db.session.delete(dep_reloaded)
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


def test_service_list_depositions(test_client):
    """Test list_depositions returns all depositions."""
    dep1 = Fakenodo(meta_data={"title": "Dep 1"})
    dep2 = Fakenodo(meta_data={"title": "Dep 2"})
    db.session.add_all([dep1, dep2])
    db.session.commit()

    depositions = service.list_depositions()
    assert isinstance(depositions, list)
    assert len(depositions) >= 2

    ids = [d["id"] for d in depositions]
    assert dep1.id in ids
    assert dep2.id in ids

    db.session.delete(dep1)
    db.session.delete(dep2)
    db.session.commit()


def test_service_get_deposition(test_client):
    """Test get_deposition returns correct deposition dict."""
    dep = Fakenodo(meta_data={"title": "Test Get"}, status="draft")
    db.session.add(dep)
    db.session.commit()

    result = service.get_deposition(dep.id)
    assert isinstance(result, dict)
    assert result.get("id") == dep.id
    assert result.get("metadata", {}).get("title") == "Test Get"
    assert result.get("status") == "draft"

    db.session.delete(dep)
    db.session.commit()


def test_service_get_deposition_not_found(test_client):
    """Test get_deposition returns None for non-existent ID."""
    result = service.get_deposition(999999)
    assert result is None


def test_service_create_deposition_from_metadata(test_client):
    """Test create_deposition method which is called by the API endpoint."""
    metadata = {"title": "API Test", "description": "Created via API"}

    resp = service.create_deposition(metadata=metadata)
    assert isinstance(resp, dict)
    dep_id = resp.get("id")
    assert dep_id is not None
    assert resp.get("metadata", {}).get("title") == "API Test"
    assert resp.get("status") == "draft"
    assert "links" in resp

    dep = Fakenodo.query.get(dep_id)
    db.session.delete(dep)
    db.session.commit()


def test_service_update_metadata_sets_dirty_no_new_doi(test_client):
    """Test that update_metadata sets dirty flag and does NOT generate new DOI."""
    dep = Fakenodo(meta_data={"title": "Original"})
    db.session.add(dep)
    db.session.commit()
    dep_id = dep.id
    original_doi = dep.doi  # Should be None initially

    updated = service.update_metadata(dep_id, {"title": "Updated Title", "description": "New desc"})
    assert isinstance(updated, dict)
    assert updated.get("dirty") is True
    assert updated.get("metadata", {}).get("title") == "Updated Title"
    assert updated.get("metadata", {}).get("description") == "New desc"
    # DOI should NOT change (remains None or original value)
    assert updated.get("doi") == original_doi

    # Re-fetch from DB to verify persistence
    dep_refreshed = Fakenodo.query.get(dep_id)
    assert dep_refreshed.meta_data.get("dirty") is True
    assert dep_refreshed.meta_data.get("title") == "Updated Title"
    assert dep_refreshed.doi == original_doi

    db.session.delete(dep_refreshed)
    db.session.commit()


def test_service_delete_deposition(test_client):
    """Test delete_deposition removes the record from DB."""
    dep = Fakenodo(meta_data={"title": "To Delete"})
    db.session.add(dep)
    db.session.commit()
    dep_id = dep.id

    result = service.delete_deposition(dep_id)
    assert result is True

    deleted = Fakenodo.query.get(dep_id)
    assert deleted is None


def test_service_delete_nonexistent_deposition(test_client):
    """Test delete_deposition returns False for non-existent ID."""
    result = service.delete_deposition(999999)
    assert result is False


def test_publish_after_file_upload_generates_new_doi(test_client):
    """Test that uploading files and publishing generates a new DOI (Zenodo logic)."""
    dep = Fakenodo(meta_data={"title": "Test Publish"})
    db.session.add(dep)
    db.session.commit()

    # Upload a file (marks files as changed)
    ds = _make_dataset_stub(id=555)
    fm = _make_fm_stub(name="data.csv", path="/tmp/data.csv")
    service.upload_file(ds, dep.id, fm)

    # Publish should generate a DOI
    pub = service.publish_deposition(dep.id)
    assert pub.get("submitted") is True
    new_doi = pub.get("doi")
    assert new_doi is not None
    assert new_doi.startswith("10.5281/fakenodo.")

    db.session.refresh(dep)
    assert dep.doi == new_doi
    assert dep.status == "published"

    db.session.delete(dep)
    db.session.commit()


def test_list_versions_returns_versions_after_publish(test_client):
    """Test that list_versions returns version history after publishing."""
    dep = Fakenodo(meta_data={"title": "Test Versions"})
    db.session.add(dep)
    db.session.commit()

    # Initially no versions
    versions = service.list_versions(dep.id)
    assert versions == [] or versions == []

    # Publish creates a version entry
    service.publish_deposition(dep.id)

    versions = service.list_versions(dep.id)
    assert isinstance(versions, list)
    assert len(versions) >= 1
    assert versions[0].get("doi") is not None

    db.session.delete(dep)
    db.session.commit()


def test_list_versions_endpoint(test_client):
    """Test the /versions endpoint returns correct JSON."""
    dep = Fakenodo(meta_data={"title": "Endpoint Test"})
    db.session.add(dep)
    db.session.commit()

    resp = test_client.get(f"/fakenodo/deposit/depositions/{dep.id}/versions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "versions" in data
    assert isinstance(data["versions"], list)

    db.session.delete(dep)
    db.session.commit()


def test_list_versions_endpoint_404_for_missing(test_client):
    """Test the /versions endpoint returns 404 for non-existent deposition."""
    resp = test_client.get("/fakenodo/deposit/depositions/999999/versions")
    assert resp.status_code == 404