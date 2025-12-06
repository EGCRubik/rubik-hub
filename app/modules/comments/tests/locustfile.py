from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token, fake


class CommentBehavior(TaskSet):
    def on_start(self):
        # Al iniciar el usuario virtual, hacemos login
        self.login()

    def login(self):
        response = self.client.get("/login")
        self.csrf_token = get_csrf_token(response)
        response = self.client.post(
            "/login",
            data={"email": "user1@example.com", "password": "1234", "csrf_token": self.csrf_token},
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")

    @task
    def view_comment(self):
        # Simulamos ver un comentario existente
        dataset_doi = "10.1234/dataset10/" 
        response = self.client.get(f"/doi/{dataset_doi}/")
        csrf_token = get_csrf_token(response)


class CommentUser(HttpUser):
    tasks = [CommentBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
