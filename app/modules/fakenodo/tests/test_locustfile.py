from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class FakenodoBehavior(TaskSet):
    """Load test behavior for FakeNODO API and dataset-related endpoints.

    This simulates a minimal workflow:
    - List depositions
    - Create a deposition (POST /fakenodo/deposit/depositions)
    - Upload a file to the deposition
    - Publish the deposition (new DOI)
    - Fetch deposition and versions
    - Call test endpoint
    """

    def on_start(self):
        # Shared state across tasks for a single user
        self.deposition_id = None

    @task(2)
    def list_depositions(self):
        self.client.get("/fakenodo/deposit/depositions")

    @task(3)
    def create_deposition(self):
        if self.deposition_id is not None:
            return
        payload = {"metadata": {"title": "Locust Deposition", "description": "Load test item"}}
        with self.client.post("/fakenodo/deposit/depositions", json=payload, catch_response=True) as resp:
            try:
                data = resp.json()
                if resp.status_code in (200, 201) and data.get("id"):
                    self.deposition_id = data["id"]
                    resp.success()
                else:
                    resp.failure(f"Unexpected response: {resp.status_code} {resp.text}")
            except Exception:
                resp.failure("Invalid JSON response")

    @task(3)
    def upload_file(self):
        if not self.deposition_id:
            return
        # Simulate CSV upload; name field is used by route when file isn't present
        files = {"file": ("locust.csv", "id,value\n1,100\n", "text/csv")}
        data = {"name": "locust.csv"}
        self.client.post(f"/fakenodo/deposit/depositions/{self.deposition_id}/files", files=files, data=data)

    @task(3)
    def publish(self):
        if not self.deposition_id:
            return
        self.client.post(f"/fakenodo/deposit/depositions/{self.deposition_id}/actions/publish")

    @task(2)
    def get_deposition(self):
        if not self.deposition_id:
            return
        self.client.get(f"/fakenodo/deposit/depositions/{self.deposition_id}")

    @task(1)
    def list_versions(self):
        if not self.deposition_id:
            return
        self.client.get(f"/fakenodo/deposit/depositions/{self.deposition_id}/versions")

    @task(1)
    def test_endpoint(self):
        self.client.get("/fakenodo/test")


class FakenodoUser(HttpUser):
    tasks = [FakenodoBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
