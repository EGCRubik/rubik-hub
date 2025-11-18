from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
from core.locust.common import fake, get_csrf_token


class AuthBehavior(TaskSet):
    def on_start(self):
        self.ensure_logged_out()
        self.login()

    @task
    def ensure_logged_out(self):
        response = self.client.get("/logout")
        if response.status_code != 200:
            print(f"Logout failed or no active session: {response.status_code}")

    @task
    def login(self):
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            # En caso de estar logueado o respuesta inesperada
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login",
            data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token},
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class CommentsBehavior(TaskSet):
    def on_start(self):
        self.auth_behavior = AuthBehavior(self)
        self.auth_behavior.on_start()
        self.view_comments()

    @task
    def view_comments(self):
        response = self.client.get("/comments")
        if response.status_code != 200:
            print(f"Comments index failed: {response.status_code}")

    @task
    def add_comment(self):
        # Obtener CSRF token de la página de comentarios
        response = self.client.get("/comments")
        if response.status_code != 200:
            print(f"Failed to load comments page: {response.status_code}")
            return

        csrf_token = get_csrf_token(response)

        # Publicar un comentario de prueba
        response = self.client.post(
            "/comments",
            data={"content": f"Test comment {fake.sentence()}", "csrf_token": csrf_token},
        )
        if response.status_code != 200:
            print(f"Failed to add comment: {response.status_code}")


class CommentsUser(HttpUser):
    tasks = [CommentsBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
