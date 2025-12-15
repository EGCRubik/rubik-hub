from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token
import pyotp
import json


class TwoFactorBehavior(TaskSet):
    def on_start(self):
        # Login to perform authenticated actions
        self.login()
        self.totp_key = None

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
            # Endpoint returns JSON with key and uri
            if resp.status_code not in (200, 302):
                resp.failure(f"Enable 2FA failed: {resp.status_code} - {resp.text[:200]}")
            else:
                try:
                    data = resp.json()
                    # Extract the key from response
                    self.totp_key = data.get("key")
                    if self.totp_key:
                        print(f"✓ Got 2FA key from enable response")
                    resp.success()
                except:
                    resp.failure("Could not parse JSON response from enable endpoint")

        # Visit setup page and attempt verification
        setup_resp = self.client.get("/profile/twofactor-setup")
        
        # Try to get CSRF token
        try:
            setup_csrf = get_csrf_token(setup_resp)
            
            # Generate real TOTP code using the key we received
            if self.totp_key:
                code = pyotp.TOTP(self.totp_key).now()
                print(f"✓ Generated TOTP code: {code}")
            else:
                code = "000000"
                print("⚠ No key available, using placeholder code")
            
            verify_resp = self.client.post(
                "/two_factor/verify",
                data={"two_factor_code": code, "csrf_token": setup_csrf},
                catch_response=True,
            )

            if verify_resp.status_code in (200, 302):
                verify_resp.success()
                print("✓ 2FA verification successful")
            else:
                verify_resp.failure(f"Verify 2FA failed: {verify_resp.status_code} - {verify_resp.text[:200]}")
                print(f"⚠ Verify 2FA failed: {verify_resp.status_code}")
                
        except ValueError:
            # CSRF token not found
            print("⚠ CSRF token not found on twofactor-setup; skipping verify step")
        

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
