from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token
from core.locust.common import fake
import io


class TopDatasetsBehavior(TaskSet):
    @task
    def top(self):
        """GET the public top datasets page."""
        response = self.client.get("/dataset/top")
        if response.status_code != 200:
            print(f"top datasets failed: {response.status_code}")


class DownloadDatasetBehavior(TaskSet):
    @task
    def download(self):
        """Attempt to download a dataset zip by id.

        Uses a small set of candidate ids to increase the chance one exists in the test DB.
        """
        # Candidate ids - adjust if your test DB has specific ids
        candidate_ids = [1, 2, 3, 10]
        for ds_id in candidate_ids:
            response = self.client.get(f"/dataset/download/{ds_id}")
            if response.status_code == 200:
                # successful download; stop iterating
                return
            # otherwise continue to next id (helps find an existing dataset)


class TopDatasetsUser(HttpUser):
    tasks = [TopDatasetsBehavior]
    min_wait = 3000
    max_wait = 7000
    host = get_host_for_locust_testing()


class DownloadDatasetUser(HttpUser):
    tasks = [DownloadDatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()


class UploadDatasetBehavior(TaskSet):
    def on_start(self):
        # Login required for upload endpoints
        self.login()

    def login(self):
        # Ensure logged out then get login page to extract CSRF
        self.client.get("/logout")
        response = self.client.get("/login")
        try:
            csrf = get_csrf_token(response)
        except Exception:
            print("Could not get CSRF token from login page")
            return

        resp = self.client.post(
            "/login",
            data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf},
        )
        if resp.status_code != 200:
            print(f"Login failed during upload behavior: {resp.status_code}")

    @task
    def upload_csv(self):
        # GET the upload tabular page to fetch CSRF token embedded in the form
        response = self.client.get("/dataset/upload")
        try:
            csrf_token = get_csrf_token(response)
        except Exception:
            print("CSRF token not found on upload page")
            return

        # Build a small in-memory CSV
        csv_content = "col1,col2\n1,2\n"
        csv_file = io.BytesIO(csv_content.encode("utf-8"))

        # Prepare form data and files
        data = {
            "title": f"Locust upload {fake.word()}",
            "desc": "Upload test from locust",
            # publication_type is required by the form - use a valid enum value
            "publication_type": "none",
            "publication_doi": "",
            "dataset_doi": "",
            "tags": "locust,upload",
            "csrf_token": csrf_token,
            # dataset_type hidden field used by the JS flow
            "dataset_type": "tabular",
        }

        csv_file.seek(0)
        files = {"csv_file": ("test.csv", csv_file, "text/csv")}

        # Post the CSV to the upload endpoint
        post_resp = self.client.post("/dataset/upload/csv", data=data, files=files)
        if post_resp.status_code not in (200, 302):
            # Print response body to help debugging
            try:
                print(f"upload_csv failed: {post_resp.status_code} body={post_resp.text}")
            except Exception:
                print(f"upload_csv failed: {post_resp.status_code} (no body available)")


class UploadDatasetUser(HttpUser):
    tasks = [UploadDatasetBehavior]
    min_wait = 8000
    max_wait = 12000
    host = get_host_for_locust_testing()
