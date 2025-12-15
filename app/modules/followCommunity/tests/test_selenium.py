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


def go_to_authors_and_communities(driver, host):
  driver.get(host)
  wait_for_page_to_load(driver)

  try:
    driver.find_element(By.LINK_TEXT, "Authors & Communities").click()
    return
  except Exception:
    pass

  links = driver.find_elements(By.XPATH, "//a[contains(@href, '/authors-and-communities')]")
  if links:
    links[0].click()
    return

  raise AssertionError("No se pudo abrir Authors & Communities")


def find_follow_button(driver):
  buttons = driver.find_elements(
    By.XPATH,
    "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'seguir')]",
  )
  if buttons:
    return buttons[0]
  return None


def open_first_community(driver):
  try:
    link = driver.find_element(By.LINK_TEXT, "View")
    link.click()
    return True
  except Exception:
    pass

  links = driver.find_elements(By.XPATH, "//a[contains(@href, '/community/')]")
  for link in links:
    if "community" in link.get_attribute("href"):
      link.click()
      return True
  return False


class TestFollowCommunity:
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

  def test_follow_unfollow_community(self):
    host = get_host_for_selenium_testing()
    self.login(host)

    go_to_authors_and_communities(self.driver, host)
    wait_for_page_to_load(self.driver)

    opened = open_first_community(self.driver)
    assert opened, "No se encontró ninguna comunidad para abrir"
    wait_for_page_to_load(self.driver)

    btn = find_follow_button(self.driver)
    assert btn, "No se encontró el botón de seguir/dejar de seguir"

    initial_label = btn.text.strip().lower()
    btn.click()
    wait_for_page_to_load(self.driver)
    time.sleep(1)

    btn_after = find_follow_button(self.driver)
    assert btn_after, "No se encontró el botón tras actualizar"
    new_label = btn_after.text.strip().lower()

    assert initial_label != new_label, "El estado de seguimiento no cambió tras el click"


if __name__ == "__main__":
  pytest.main([__file__])