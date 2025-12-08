import json
import os
import re
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


class TestTesterseleniumfakenodo():
  def setup_method(self, method):
    self.driver = initialize_driver()
    self.vars = {}
    self.wait = WebDriverWait(self.driver, 10)
    self.host = get_host_for_selenium_testing()
  
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
    self.driver.set_window_size(2494, 1408)
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").click()
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(8) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.ID, "title").click()
    self.driver.find_element(By.ID, "title").send_keys("test fakenodo")
    self.driver.find_element(By.ID, "desc").click()
    self.driver.find_element(By.ID, "desc").send_keys("test")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    self.driver.find_element(By.ID, "csv_file").send_keys(os.path.abspath("app/modules/dataset/csv_examples/file1.csv"))
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    self.driver.find_element(By.CSS_SELECTOR, ".card-body:nth-child(2) td:nth-child(1)").click()
    self.driver.find_element(By.CSS_SELECTOR, ".card-body:nth-child(2) td:nth-child(1) > a").click()
    self.driver.find_element(By.CSS_SELECTOR, "form > .btn-outline-primary").click()
    assert self.driver.switch_to.alert.text == "Crear un registro preliminar en el repositorio para este dataset?"
    self.driver.switch_to.alert.accept()
    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .card")))
    doi_link = self.wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "doi/10.5281/fakenodo")))
    doi_url = doi_link.get_attribute("href")
    self.driver.get(doi_url)
    self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Crear nueva versión"))).click()
    self.driver.find_element(By.CSS_SELECTOR, ".form-check-label").click()
    self.driver.find_element(By.ID, "csv_file").send_keys(os.path.abspath("app/modules/dataset/csv_examples/file6.csv"))
    dropdown = self.driver.find_element(By.ID, "is_major")
    dropdown.find_element(By.XPATH, "//option[. = 'Major release (X.0)']").click()
    self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(2)").click()
    self.driver.find_element(By.ID, "version_comment").click()
    self.driver.find_element(By.ID, "version_comment").send_keys("nuevo file")
    self.driver.find_element(By.ID, "desc").click()
    self.driver.find_element(By.ID, "desc").send_keys("test nuevo")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(10) > td:nth-child(1) > a").click()
    self.driver.find_element(By.CSS_SELECTOR, ".doi_text").click()


if __name__ == "__main__":
  pytest.main([__file__])