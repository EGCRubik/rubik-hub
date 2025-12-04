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
        dataset_doi = "10.1234/dataset10/"  # asegúrate que existe en tu entorno de pruebas
        response = self.client.get(f"/doi/{dataset_doi}/")
        csrf_token = get_csrf_token(response)

    # @task
    # def create_comment(self):
    #     dataset_id = 10
    #     dataset_doi = "10.1234/dataset10"

    #     # Paso 1: obtener la vista del dataset para extraer CSRF
    #     response = self.client.get(f"/doi/{dataset_doi}/")

    #     # Paso 2: enviar el POST al endpoint de creación de comentario
    #     with self.client.post(
    #         f"/comments/create/{dataset_id}",
    #         data={"content": fake.text(max_nb_chars=100), "csrf_token": self.csrf_token},
    #         catch_response=True
    #     ) as response:
    #         if response.status_code != 200:
    #             # Esto aparecerá en la UI de Locust como fallo con detalle
    #             response.failure(
    #                 f"Failed {response.status_code}: {response.text[:200]}"
    #             )
    #         else:
    #             response.success()

    # @task
    # def delete_comment(self):
    #     comment_id = 1  # comentario válido
    #     response = self.client.get(f"/comments/view/{comment_id}")  # para obtener CSRF si aplica
    #     csrf_token = get_csrf_token(response)

    #     response = self.client.post(
    #         f"/comments/delete/{comment_id}",
    #         data={"csrf_token": csrf_token},
    #     )
    #     if response.status_code != 200:
    #         print(f"Delete comment failed: {response.status_code}")


class CommentUser(HttpUser):
    tasks = [CommentBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
