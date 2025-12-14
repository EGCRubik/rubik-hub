from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class TwoFactorBehavior(TaskSet):
    def on_start(self):
        # Login to perform authenticated actions
        self.login()

    def login(self):
        resp = self.client.get("/login")
        csrf = get_csrf_token(resp)
        resp = self.client.post(
            "/login",
            data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf},
        )
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code}")

    @task(2)
    def enable_two_factor(self):
        # Fetch CSRF from profile edit page where the 2FA toggle form is rendered
        edit_resp = self.client.get("/profile/edit")
        csrf = get_csrf_token(edit_resp)
        if not csrf:
            print("CSRF token not found on /profile/edit")
            return

        # Enable 2FA
        with self.client.post(
            "/two_factor/update-factor-enabled",
            data={"enabled": "1", "csrf_token": csrf},
            catch_response=True,
        ) as resp:
            # Endpoint may return JSON with redirect_url or an HTTP redirect
            if resp.status_code not in (200, 302):
                resp.failure(f"Enable 2FA failed: {resp.status_code} - {resp.text[:200]}")
            else:
                resp.success()

        # Optionally visit the setup page to simulate user flow
        self.client.get("/profile/twofactor-setup")

    @task(1)
    def disable_two_factor(self):
        # Fetch CSRF again (fresh token)
        edit_resp = self.client.get("/profile/edit")
        csrf = get_csrf_token(edit_resp)
        if not csrf:
            print("CSRF token not found on /profile/edit")
            return

        # Disable 2FA
        with self.client.post(
            "/two_factor/update-factor-enabled",
            data={"enabled": "0", "csrf_token": csrf},
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Disable 2FA failed: {resp.status_code} - {resp.text[:200]}")
            else:
                resp.success()


class TwoFactorUser(HttpUser):
    tasks = [TwoFactorBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
