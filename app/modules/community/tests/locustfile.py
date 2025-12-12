from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import fake, get_csrf_token


class CommunityBehavior(TaskSet):
    def on_start(self):
        # Al iniciar el usuario virtual, hacemos login para endpoints que requieren autenticación
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

    @task(3)
    def index(self):
        # La ruta correcta para el listado es /community/list
        response = self.client.get("/community/list")
        if response.status_code != 200:
            print(f"Community index failed: {response.status_code}")

    @task(1)
    def view_community(self):
        # Intenta acceder a una comunidad concreta.
        # Primero obtenemos el listado y extraemos un slug disponible en la página.
        list_resp = self.client.get("/community/list")
        slug = None
        if list_resp.status_code == 200:
            import re

            m = re.search(r'href="/community/([a-zA-Z0-9_\-]+)"', list_resp.text)
            if m:
                slug = m.group(1)

        if not slug:
            # Fallback a un slug por defecto que puedas tener en tu entorno de pruebas
            slug = "test"

        response = self.client.get(f"/community/{slug}")
        if response.status_code != 200:
            print(f"Community view failed: {response.status_code}")

    @task
    def create_community(self):
        response = self.client.get("/community/create")
        csrf_token = get_csrf_token(response)
        # CommunityForm requiere 'name' y 'slug' (restricción: lowercase, numbers y guiones)
        name = fake.text(max_nb_chars=30)
        # Generar slug seguro: solo lowercase, digits y guiones
        import re

        slug = re.sub(r"[^a-z0-9-]", "-", re.sub(r"\s+", "-", name.lower()))
        slug = re.sub(r"-+", "-", slug).strip("-") or "test"

        with self.client.post(
            "/community/create",
            data={
                "name": name,
                "slug": slug,
                "description": fake.text(max_nb_chars=200),
                "csrf_token": csrf_token,
            },
            catch_response=True,
        ) as resp:
            if resp.status_code != 201:
                # El endpoint devuelve 201 en creación exitosa
                resp.failure(f"Create community failed: {resp.status_code} - {resp.text[:200]}")
            else:
                resp.success()


class CommunityUser(HttpUser):
    tasks = [CommunityBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
