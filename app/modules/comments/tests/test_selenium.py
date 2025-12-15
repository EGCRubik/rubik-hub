import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def test_comments_index():
    driver = initialize_driver()
    wait = WebDriverWait(driver, 10)

    try:
        host = get_host_for_selenium_testing()

        # Open home page
        driver.get(f"{host}/")
        time.sleep(2)  # ensure page loads

        # Click on dataset link
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sample dataset 10 (Version: 2.0) ⭐"))).click()

        # Enter first comment
        comment_input = wait.until(EC.presence_of_element_located((By.NAME, "content")))
        comment_input.click()
        comment_input.send_keys("Buenas tardes")
        add_comment_btn = driver.find_element(By.XPATH, "//button[text()='Add Comment']")
        add_comment_btn.click()

        # Log in
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.click()
        email_input.clear()
        email_input.send_keys("user1@example.com")

        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.click()
        password_input.clear()
        password_input.send_keys("1234")
        password_input.send_keys(Keys.RETURN)

        # Wait for redirect after login
        time.sleep(2)

        # Click dataset again
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sample dataset 10 (Version: 2.0) ⭐"))).click()

        # Enter second comment
        comment_input = wait.until(EC.presence_of_element_located((By.NAME, "content")))
        comment_input.click()
        comment_input.send_keys("A mí me gusta tu perfil")
        add_comment_btn = driver.find_element(By.XPATH, "//button[text()='Add Comment']")
        add_comment_btn.click()

        # Interact with a stable button example: DOI button
        doi_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.doi_button")))
        doi_button.click()

        # Interact with a file's View button as an example
        view_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'viewFile')]")))
        view_button.click()

        print("Test pased!")

    except (NoSuchElementException, TimeoutException) as e:
        raise AssertionError(f"[ERROR] Test failed! Element not found or timeout: {e}")

    finally:
        close_driver(driver)


# Call the test function
test_comments_index()

# He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código. 
# La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.
