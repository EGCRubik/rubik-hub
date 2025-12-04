from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class FakenodoBehavior(TaskSet):

    deposition_id: int | None = None
    published_once: bool = False
    toggle_metadata_format: bool = False

    def on_start(self):
        self.login()
        self.create_deposition()

    def login(self):
        resp = self.client.get("/login")
        csrf = get_csrf_token(resp)
        self.client.post(
            "/login",
            data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf},
        )

    def create_deposition(self):
        payload = {"metadata": {"title": "LocustLoad", "description": "Initial desc"}}
        r = self.client.post("/fakenodo/deposit/depositions", json=payload)
        if r.status_code == 201:
            self.deposition_id = r.json().get("id")
        else:
            self.deposition_id = None

    @task
    def patch_metadata(self):
        if not self.deposition_id:
            return
        if self.toggle_metadata_format:
            payload = {"metadata": {"title": "LocustNested", "description": "Nested desc", "tags": ["a", "b"]}}
        else:
            payload = {"title": "LocustFlat", "description": "Flat desc", "tags": ["x"]}
        self.client.patch(f"/fakenodo/deposit/depositions/{self.deposition_id}/metadata", json=payload)
        self.toggle_metadata_format = not self.toggle_metadata_format

    @task
    def upload_file(self):
        if not self.deposition_id:
            return
        self.client.post(
            f"/fakenodo/deposit/depositions/{self.deposition_id}/files",
            data={"name": "locust.txt"},
        )

    @task
    def publish(self):
        if not self.deposition_id:
            return
        r = self.client.post(f"/fakenodo/deposit/depositions/{self.deposition_id}/actions/publish")
        if r.status_code == 202:
            self.published_once = True

    @task
    def list_versions(self):
        if not self.deposition_id:
            return
        self.client.get(f"/fakenodo/deposit/depositions/{self.deposition_id}/versions")

    @task
    def maybe_delete_and_recreate(self):
        if self.deposition_id and self.published_once:
            self.client.delete(f"/fakenodo/deposit/depositions/{self.deposition_id}")
            self.deposition_id = None
            self.published_once = False
            self.create_deposition()


class FakenodoUser(HttpUser):
    tasks = [FakenodoBehavior]
    min_wait = 3000
    max_wait = 7000
    host = get_host_for_locust_testing()
