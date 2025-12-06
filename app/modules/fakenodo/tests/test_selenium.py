import json
import os
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


class TestTesterseleniumfakenodo():
  def setup_method(self, method):
    self.driver = initialize_driver()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def wait_for_window(self, timeout = 2):
    time.sleep(round(timeout / 1000))
    wh_now = self.driver.window_handles
    wh_then = self.vars["window_handles"]
    if len(wh_now) > len(wh_then):
      return set(wh_now).difference(set(wh_then)).pop()
  
  def test_testerseleniumfakenodo(self):
    self.driver.get("http://127.0.0.1:5000/")
    try:
      self.driver.set_window_size(1280, 800)
    except Exception:
      pass
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").click()
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(8) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.ID, "title").click()
    self.driver.find_element(By.ID, "title").send_keys("test fakenodo")
    self.driver.find_element(By.ID, "title").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "desc").send_keys("test")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    csv_input = self.driver.find_element(By.ID, "csv_file")
    csv_path = os.path.abspath("app/modules/dataset/csv_examples/file2.csv")
    csv_input.send_keys(csv_path)
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    WebDriverWait(self.driver, 5).until(
      expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr td a"))
    )
    self.driver.find_element(By.CSS_SELECTOR, "table tbody tr td a").click()


if __name__ == "__main__":
  pytest.main([__file__])