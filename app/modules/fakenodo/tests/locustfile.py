from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class FakenodoBehavior(TaskSet):

    def on_start(self):
        self.deposition_id = None
        self.create_deposition()

    @task(3)
    def create_deposition(self):
        """Create a new deposition and store the ID for other tasks."""
        response = self.client.post("/fakenodo/deposit/depositions")
        if response.status_code == 201:
            try:
                data = response.json()
                self.deposition_id = data.get("id")
            except Exception:
                pass

    @task(2)
    def list_depositions(self):
        """List all depositions."""
        self.client.get("/fakenodo/deposit/depositions")

    @task(2)
    def publish(self):
        """Publish the current deposition."""
        if not self.deposition_id:
            return
        self.client.post(f"/fakenodo/deposit/depositions/{self.deposition_id}/actions/publish")

    @task(2)
    def get_deposition(self):
        """Get details of the current deposition."""
        if not self.deposition_id:
            return
        self.client.get(f"/fakenodo/deposit/depositions/{self.deposition_id}")

    @task(1)
    def list_versions(self):
        """List versions of the current deposition."""
        if not self.deposition_id:
            return
        self.client.get(f"/fakenodo/deposit/depositions/{self.deposition_id}/versions")

    @task(1)
    def test_endpoint(self):
        """Test the fakenodo test endpoint."""
        self.client.get("/fakenodo/test")

    @task(1)
    def index_page(self):
        """Access the fakenodo index page."""
        self.client.get("/fakenodo")


class FakenodoUser(HttpUser):
    tasks = [FakenodoBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
