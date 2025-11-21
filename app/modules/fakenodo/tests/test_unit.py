import json
import os
import tempfile

import pytest

from app.modules.fakenodo.routes import service as global_service
from app.modules.fakenodo.services import FakenodoService


@pytest.fixture()
def temp_service():
	"""Provide a FakenodoService instance using an isolated temp directory.

	Each test gets a fresh JSON DB file so state does not leak.
	"""
	with tempfile.TemporaryDirectory() as td:
		svc = FakenodoService(working_dir=td)
		yield svc


@pytest.fixture()
def svc():
	with tempfile.TemporaryDirectory() as td:
		yield FakenodoService(working_dir=td)

def test_create_and_list(svc):
    r1 = svc.create_deposition(metadata={"title": "A"})
    r2 = svc.create_new_deposition(metadata={"title": "B"})
    assert r1["id"] == 1 and r2["id"] == 2
    recs = svc.list_depositions()
    assert len(recs) == 2


def test_upload_and_dirty_flag(svc):
    dep = svc.create_deposition(metadata={"title": "Upload"})
    file_rec = svc.upload_file(dep["id"], "file.txt", b"data")
    assert file_rec and file_rec["name"] == "file.txt"
    dep_after = svc.get_deposition(dep["id"])
    assert dep_after["dirty"] is True


def test_publish_and_versioning(svc):
    dep = svc.create_deposition(metadata={"title": "Version"})
    v1 = svc.publish_deposition(dep["id"])
    assert v1 and v1["version"] == 1
    v1b = svc.publish_deposition(dep["id"])
    assert v1b is v1
    svc.upload_file(dep["id"], "new.txt", b"hi")
    v2 = svc.publish_deposition(dep["id"])
    assert v2["version"] == 2 and v2["doi"].endswith(".v2")
    assert svc.get_doi(dep["id"]) == v2["doi"]


def test_delete_deposition(svc):
    dep = svc.create_deposition(metadata={"title": "Delete"})
    assert svc.get_deposition(dep["id"]) is not None
    assert svc.delete_deposition(dep["id"]) is True
    assert svc.get_deposition(dep["id"]) is None


def test_edge_cases(svc):
    assert svc.upload_file(9999, "ghost.txt", b"ghost") is None
    assert svc.publish_deposition(9999) is None


def test_create_deposition_increments_ids(temp_service):
	r1 = temp_service.create_new_deposition(metadata={"title": "First"})
	r2 = temp_service.create_new_deposition(metadata={"title": "Second"})

	assert r1["id"] == 1
	assert r2["id"] == 2
	all_records = temp_service.list_depositions()
	assert len(all_records) == 2
	assert all_records[0]["metadata"]["title"] == "First"


def test_upload_file_marks_dirty_and_adds_file(temp_service):
	dep = temp_service.create_new_deposition(metadata={"title": "Files"})
	file_rec = temp_service.upload_file(dep["id"], "data.csv", b"a,b,c\n1,2,3\n")
	assert file_rec is not None
	fetched = temp_service.get_deposition(dep["id"])
	assert fetched["dirty"] is True
	assert len(fetched["files"]) == 1
	assert fetched["files"][0]["name"] == "data.csv"


def test_publish_creates_version_and_resets_dirty(temp_service):
	dep = temp_service.create_new_deposition(metadata={"title": "Publish"})
	v1 = temp_service.publish_deposition(dep["id"])
	assert v1 is not None
	assert v1["version"] == 1
	rec = temp_service.get_deposition(dep["id"])
	assert rec["published"] is True
	assert rec["dirty"] is False
	assert rec.get("doi")

	v1_again = temp_service.publish_deposition(dep["id"])
	assert v1_again is v1  
	versions = temp_service.list_versions(dep["id"])
	assert len(versions) == 1


def test_publish_after_change_increments_version(temp_service):
	dep = temp_service.create_deposition(metadata={"title": "Versioning"})
	v1 = temp_service.publish_deposition(dep["id"])  
	temp_service.upload_file(dep["id"], "file.txt", b"hello")  
	v2 = temp_service.publish_deposition(dep["id"]) 
	assert v2 is not None
	assert v2["version"] == 2
	assert v2["doi"].endswith(".v2")
	versions = temp_service.list_versions(dep["id"])
	assert [v["version"] for v in versions] == [1, 2]
	assert temp_service.get_doi(dep["id"]).endswith(".v2")


def test_get_doi_latest(temp_service):
	dep = temp_service.create_deposition(metadata={"title": "DOI"})
	v1 = temp_service.publish_deposition(dep["id"])  
	temp_service.upload_file(dep["id"], "f.txt", b"x")
	v2 = temp_service.publish_deposition(dep["id"])  
	doi_latest = temp_service.get_doi(dep["id"])
	assert doi_latest == v2["doi"]


def test_delete_deposition(temp_service):
	dep = temp_service.create_deposition(metadata={"title": "Delete"})
	assert temp_service.get_deposition(dep["id"]) is not None
	assert temp_service.delete_deposition(dep["id"]) is True
	assert temp_service.get_deposition(dep["id"]) is None
	assert len(temp_service.list_depositions()) == 0


def test_upload_file_nonexistent_returns_none(temp_service):
	res = temp_service.upload_file(9999, "ghost.txt", b"ghost")
	assert res is None


def test_publish_nonexistent_returns_none(temp_service):
	res = temp_service.publish_deposition(9999)
	assert res is None

@pytest.fixture(autouse=True)
def reset_global_fakenodo_service():
	"""Reset the singleton service used by the routes before each integration test.

	The routes module instantiates a global `service = FakenodoService()` so we must
	clear it to avoid cross-test contamination.
	"""
	global_service._db = {"records": {}, "next_id": 1}
	global_service._save()
	yield
	global_service._db = {"records": {}, "next_id": 1}
	global_service._save()


def _post_json(client, url, payload, expected_status=200):
	resp = client.post(url, data=json.dumps(payload), content_type="application/json")
	assert resp.status_code == expected_status, f"Expected {expected_status} got {resp.status_code} body={resp.get_data(as_text=True)}"
	return resp


def test_api_create_get_list_delete(test_client):
	# Create
	r_create = _post_json(test_client, "/fakenodo/deposit/depositions", {"metadata": {"title": "Alpha"}}, expected_status=201)
	dep_id = r_create.get_json()["id"]
	assert dep_id == 1
	# List
	r_list = test_client.get("/fakenodo/deposit/depositions")
	assert r_list.status_code == 200
	assert len(r_list.get_json()["depositions"]) == 1
	# Get
	r_get = test_client.get(f"/fakenodo/deposit/depositions/{dep_id}")
	assert r_get.status_code == 200
	assert r_get.get_json()["metadata"]["title"] == "Alpha"
	# Delete
	r_del = test_client.delete(f"/fakenodo/deposit/depositions/{dep_id}")
	assert r_del.status_code == 200
	# Get after delete should 404
	r_get_missing = test_client.get(f"/fakenodo/deposit/depositions/{dep_id}")
	assert r_get_missing.status_code == 404


def test_api_upload_file_sets_dirty_and_lists_files(test_client):
	dep_id = _post_json(test_client, "/fakenodo/deposit/depositions", {"metadata": {"title": "Files"}}, expected_status=201).get_json()["id"]
	resp_up = test_client.post(
		f"/fakenodo/deposit/depositions/{dep_id}/files",
		data={"name": "data.csv"},
		content_type="multipart/form-data",
	)
	assert resp_up.status_code == 201
	r_get = test_client.get(f"/fakenodo/deposit/depositions/{dep_id}")
	rec = r_get.get_json()
	assert rec["dirty"] is True
	assert len(rec["files"]) == 1
	assert rec["files"][0]["name"] == "data.csv"


def test_api_publish_versioning_behavior(test_client):
	dep_id = _post_json(test_client, "/fakenodo/deposit/depositions", {"metadata": {"title": "Version"}}, expected_status=201).get_json()["id"]
	v1 = test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/actions/publish")
	assert v1.status_code == 202
	assert v1.get_json()["version"] == 1
	v1b = test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/actions/publish")
	assert v1b.status_code == 202
	assert v1b.get_json()["version"] == 1
	# Upload file -> dirty -> new version
	test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/files", data={"name": "new.txt"}, content_type="multipart/form-data")
	v2 = test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/actions/publish")
	assert v2.status_code == 202
	assert v2.get_json()["version"] == 2
	assert v2.get_json()["doi"].endswith(".v2")
	r_versions = test_client.get(f"/fakenodo/deposit/depositions/{dep_id}/versions")
	versions = r_versions.get_json()["versions"]
	assert [v["version"] for v in versions] == [1, 2]


def test_api_metadata_patch_flat_and_nested_formats(test_client):
	dep_id = _post_json(test_client, "/fakenodo/deposit/depositions", {"metadata": {"title": "Meta"}}, expected_status=201).get_json()["id"]
	# Initial publish
	test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/actions/publish")
	# Nested format
	r_patch_nested = test_client.patch(
		f"/fakenodo/deposit/depositions/{dep_id}/metadata",
		data=json.dumps({"metadata": {"title": "MetaUpdated", "description": "Desc", "tags": ["a", "b"]}}),
		content_type="application/json",
	)
	assert r_patch_nested.status_code == 200
	body_nested = r_patch_nested.get_json()
	assert body_nested["metadata"]["title"] == "MetaUpdated"
	assert body_nested["metadata"]["tags"] == "a,b"
	v_after_patch = test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/actions/publish")
	assert v_after_patch.status_code == 202
	assert v_after_patch.get_json()["version"] == 1
	# Flat format
	r_patch_flat = test_client.patch(
		f"/fakenodo/deposit/depositions/{dep_id}/metadata",
		data=json.dumps({"title": "FlatTitle", "description": "FlatDesc", "tags": ["x"]}),
		content_type="application/json",
	)
	assert r_patch_flat.status_code == 200
	body_flat = r_patch_flat.get_json()
	assert body_flat["metadata"]["title"] == "FlatTitle"
	assert body_flat["metadata"]["tags"] == "x"
	v_after_flat = test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/actions/publish")
	assert v_after_flat.status_code == 202
	assert v_after_flat.get_json()["version"] == 1


def test_api_upload_missing_name_returns_400(test_client):
	dep_id = _post_json(test_client, "/fakenodo/deposit/depositions", {"metadata": {"title": "NoName"}}, expected_status=201).get_json()["id"]
	r = test_client.post(f"/fakenodo/deposit/depositions/{dep_id}/files", data={}, content_type="multipart/form-data")
	assert r.status_code == 400


def test_api_get_and_delete_nonexistent(test_client):
	r_get = test_client.get("/fakenodo/deposit/depositions/9999")
	assert r_get.status_code == 404
	r_del = test_client.delete("/fakenodo/deposit/depositions/9999")
	assert r_del.status_code == 404
