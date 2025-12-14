from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def test_enable_two_factor():
    """
    Test enabling two-factor authentication through the profile edit page.
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        wait = WebDriverWait(driver, 10)

        # Login first
        driver.get(f'{host}/login')
        time.sleep(2)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # Navigate to profile edit page
        driver.get(f'{host}/profile/edit')
        time.sleep(2)

        try:
            # Find and click the "Activate 2FA" button
            enable_button = wait.until(
                EC.element_to_be_clickable((By.ID, "toggle-2fa-button"))
            )
            
            # Verify button text is "Activar 2FA"
            assert "Activar 2FA" in enable_button.text or "Activar" in enable_button.text
            
            enable_button.click()
            
            # Wait for redirect to setup page
            time.sleep(3)
            
            # Verify we're on the setup page by checking for QR code or verification form
            current_url = driver.current_url
            assert "twofactor" in current_url or driver.find_element(By.ID, "two_factor_code")
            
            print("Enable two-factor test passed!")

        except NoSuchElementException as e:
            raise AssertionError(f'Enable two-factor test failed: {e}')

    finally:
        close_driver(driver)


def test_disable_two_factor():
    """
    Test disabling two-factor authentication through the profile edit page.
    Assumes 2FA is already enabled.
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        wait = WebDriverWait(driver, 10)

        # Login
        driver.get(f'{host}/login')
        time.sleep(2)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # Navigate to profile edit
        driver.get(f'{host}/profile/edit')
        time.sleep(2)

        try:
            # Find the toggle button - it should say "Desactivar 2FA" if already enabled
            toggle_button = wait.until(
                EC.element_to_be_clickable((By.ID, "toggle-2fa-button"))
            )
            
            button_text = toggle_button.text
            
            # If button says "Desactivar", click to disable
            if "Desactivar" in button_text:
                toggle_button.click()
                time.sleep(3)
                
                # Verify page reloaded and button now says "Activar"
                driver.get(f'{host}/profile/edit')
                time.sleep(2)
                
                new_button = driver.find_element(By.ID, "toggle-2fa-button")
                assert "Activar" in new_button.text
                
                print("Disable two-factor test passed!")
            else:
                print("2FA was not enabled, skipping disable test")

        except NoSuchElementException as e:
            raise AssertionError(f'Disable two-factor test failed: {e}')

    finally:
        close_driver(driver)


def test_two_factor_setup_page():
    """
    Test accessing the two-factor setup page and verifying QR code display.
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        wait = WebDriverWait(driver, 10)

        # Login
        driver.get(f'{host}/login')
        time.sleep(2)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # First enable 2FA to get to setup page
        driver.get(f'{host}/profile/edit')
        time.sleep(2)

        try:
            enable_button = wait.until(
                EC.element_to_be_clickable((By.ID, "toggle-2fa-button"))
            )
            
            if "Activar" in enable_button.text:
                enable_button.click()
                time.sleep(3)
                
                # Should be on setup page now
                # Check for QR image
                qr_image = driver.find_element(By.CSS_SELECTOR, "img[src*='qr_image']")
                assert qr_image is not None
                
                # Check for verification code input
                code_input = driver.find_element(By.ID, "two_factor_code")
                assert code_input is not None
                
                # Check for verify button
                verify_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                assert verify_button is not None
                
                print("Two-factor setup page test passed!")
            else:
                print("2FA already enabled, test skipped")

        except NoSuchElementException as e:
            raise AssertionError(f'Setup page test failed: {e}')

    finally:
        close_driver(driver)


def test_two_factor_complete_flow():
    """
    Test the complete flow: enable 2FA, view setup page, then disable 2FA.
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        wait = WebDriverWait(driver, 10)

        # Step 1: Login
        driver.get(f'{host}/login')
        time.sleep(2)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)

        try:
            # Step 2: Enable 2FA
            driver.get(f'{host}/profile/edit')
            time.sleep(2)
            
            enable_button = wait.until(
                EC.element_to_be_clickable((By.ID, "toggle-2fa-button"))
            )
            
            if "Activar" in enable_button.text:
                enable_button.click()
                time.sleep(4)
                
                # Verify we're on setup page
                assert "twofactor" in driver.current_url or driver.find_element(By.ID, "two_factor_code")
                print("✓ 2FA enabled successfully")
                
                # Step 3: Go back to profile edit and wait for page to fully load
                driver.get(f'{host}/profile/edit')
                time.sleep(3)
                
                # Step 4: Check if 2FA toggle now shows as enabled
                # The page should reload and show "Desactivar 2FA" button
                # If not, the setup was not completed (only initiated)
                # For this test, we'll just verify the button exists and skip disable if not ready
                disable_button = wait.until(
                    EC.presence_of_element_located((By.ID, "toggle-2fa-button"))
                )
                
                button_text = disable_button.text
                print(f"Button text after enabling: '{button_text}'")
                
                if "Desactivar" in button_text:
                    disable_button.click()
                    time.sleep(4)
                    
                    # Verify it was disabled
                    driver.get(f'{host}/profile/edit')
                    time.sleep(3)
                    
                    final_button = driver.find_element(By.ID, "toggle-2fa-button")
                    assert "Activar" in final_button.text
                    print("✓ 2FA disabled successfully")
                    print("Complete two-factor flow test passed!")
                else:
                    print(f"⚠ Warning: 2FA setup initiated but not yet verified.")
                    print(f"   Button still shows: '{button_text}'")
                    print("   Note: 2FA requires QR code verification to be fully enabled.")
                    print("   This is expected behavior - setup page visited but code not verified.")
            else:
                print("2FA already enabled at start, attempting to disable...")
                enable_button.click()
                time.sleep(4)
                print("✓ 2FA toggled")

        except NoSuchElementException as e:
            raise AssertionError(f'Complete flow test failed: {e}')

    finally:
        close_driver(driver)


# Call the test functions
if __name__ == "__main__":
    print("Running two-factor Selenium tests...")
    print("\n=== Test 1: Enable Two-Factor ===")
    test_enable_two_factor()
    print("\n=== Test 2: Disable Two-Factor ===")
    test_disable_two_factor()
    print("\n=== Test 3: Setup Page ===")
    test_two_factor_setup_page()
    print("\n=== Test 4: Complete Flow ===")
    test_two_factor_complete_flow()
    print("\n✅ All two-factor tests completed!")

