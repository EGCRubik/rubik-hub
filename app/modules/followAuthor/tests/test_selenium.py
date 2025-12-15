import pytest
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=5):
  WebDriverWait(driver, timeout).until(
    lambda drv: drv.execute_script("return document.readyState") == "complete"
  )


def find_follow_buttons(driver):
  # Look for follow/unfollow buttons under the Authors list
  buttons = driver.find_elements(
    By.XPATH,
    "//h2[contains(., 'Authors')]/following::ul[1]//button",
  )
  if buttons:
    return buttons
  return driver.find_elements(By.XPATH, "//button[contains(., 'Seguir') or contains(., 'seguir') or contains(., 'Dejar')]" )


class TestFollowAuthor:
  def setup_method(self, method):
    self.driver = initialize_driver()
    self.vars = {}

  def teardown_method(self, method):
    try:
      close_driver(self.driver)
    except Exception:
      self.driver.quit()

  def login(self, host):
    self.driver.get(host)
    wait_for_page_to_load(self.driver)
    self.driver.set_window_size(1280, 800)

    login_clicked = False
    try:
      self.driver.find_element(By.LINK_TEXT, "Login").click()
      login_clicked = True
    except Exception:
      pass

    if not login_clicked:
      links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/auth/login')]")
      if links:
        links[0].click()
        login_clicked = True

    assert login_clicked, "No se pudo abrir la página de login"
    wait_for_page_to_load(self.driver)

    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    wait_for_page_to_load(self.driver)

  def test_follow_unfollow_author(self):
    host = get_host_for_selenium_testing()
    self.login(host)

    self.driver.get(f"{host}/authors-and-communities")
    wait_for_page_to_load(self.driver)

    buttons = find_follow_buttons(self.driver)
    assert buttons, "No se encontraron autores ni botones de seguir"

    initial_label = buttons[0].text.strip().lower()
    buttons[0].click()
    wait_for_page_to_load(self.driver)
    time.sleep(1)

    buttons_after = find_follow_buttons(self.driver)
    assert buttons_after, "La página no mostró botones tras seguir/deseguir"
    new_label = buttons_after[0].text.strip().lower()

    assert initial_label != new_label, "El estado de seguimiento no cambió tras el click"


if __name__ == "__main__":
  pytest.main([__file__])