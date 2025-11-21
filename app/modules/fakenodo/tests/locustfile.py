from __future__ import annotations

import io
import json
import time
from typing import Optional

from locust import HttpUser, SequentialTaskSet, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing


def _now_suffix() -> str:
    return str(int(time.time() * 1000))


class FakenodoBrowseBehavior(TaskSet):
    """Tareas ligeras para navegación y listados."""

    @task(3)
    def list_depositions(self):
        resp = self.client.get("/fakenodo/deposit/depositions", name="GET /depositions")
        if resp.status_code != 200:
            resp.failure(f"/depositions status={resp.status_code}")


class FakenodoFlow(SequentialTaskSet):
    """Flujo E2E: crear -> subir -> publicar -> listar versiones -> eliminar."""

    deposition_id: Optional[int] = None

    @task
    def create_deposition(self):
        payload = {"metadata": {"title": f"locust-{_now_suffix()}"}}
        resp = self.client.post(
            "/fakenodo/deposit/depositions",
            data=json.dumps(payload),
            name="POST /depositions",
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 201:
            try:
                self.deposition_id = resp.json().get("id")
            except Exception:
                resp.failure("Invalid JSON creating deposition")
        else:
            resp.failure(f"Create status={resp.status_code}")

    @task
    def upload_file(self):
        if not self.deposition_id:
            return
        file_name = f"data-{_now_suffix()}.csv"
        file_content = b"col1,col2\n1,2\n"
        files = {"file": (file_name, io.BytesIO(file_content), "text/csv")}
        data = {"name": file_name}
        resp = self.client.post(
            f"/fakenodo/deposit/depositions/{self.deposition_id}/files",
            files=files,
            data=data,
            name="POST /depositions/{id}/files",
        )
        if resp.status_code not in (200, 201):
            resp.failure(f"Upload status={resp.status_code}")

    @task
    def publish(self):
        if not self.deposition_id:
            return
        resp = self.client.post(
            f"/fakenodo/deposit/depositions/{self.deposition_id}/actions/publish",
            name="POST /depositions/{id}/actions/publish",
        )
        if resp.status_code not in (200, 202):
            resp.failure(f"Publish status={resp.status_code}")

    @task
    def list_versions(self):
        if not self.deposition_id:
            return
        resp = self.client.get(
            f"/fakenodo/deposit/depositions/{self.deposition_id}/versions",
            name="GET /depositions/{id}/versions",
        )
        if resp.status_code != 200:
            resp.failure(f"List versions status={resp.status_code}")

    @task
    def delete(self):
        if not self.deposition_id:
            return
        resp = self.client.delete(
            f"/fakenodo/deposit/depositions/{self.deposition_id}",
            name="DELETE /depositions/{id}",
        )
        if resp.status_code not in (200, 204):
            resp.failure(f"Delete status={resp.status_code}")
        self.deposition_id = None
        self.interrupt()


class FakenodoUser(HttpUser):
    tasks = {FakenodoBrowseBehavior: 3, FakenodoFlow: 1}
    wait_time = between(1, 5)
    host = get_host_for_locust_testing()
