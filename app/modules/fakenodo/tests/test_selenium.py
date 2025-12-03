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
    self.driver.set_window_size(2494, 1408)
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.LINK_TEXT, "Upload dataset").click()
    self.driver.find_element(By.ID, "title").click()
    num_random = str(int(time.time()))
    dataset_initial_title = "tester fakenodo selenium" + num_random
    self.driver.find_element(By.ID, "title").send_keys(dataset_initial_title)
    self.driver.find_element(By.ID, "desc").click()
    self.driver.find_element(By.ID, "desc").send_keys("tester")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    self.driver.find_element(By.ID, "csv_file").send_keys(os.path.abspath("app/modules/dataset/csv_examples/file1.csv"))
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    self.driver.find_element(By.LINK_TEXT, dataset_initial_title).click()
    self.driver.find_element(By.CSS_SELECTOR, "form > .btn-outline-primary").click()
    assert self.driver.switch_to.alert.text == "Crear un registro preliminar en FakeNODO para este dataset?"
    self.driver.switch_to.alert.accept()
    WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.NAME, "title")))
    self.driver.find_element(By.NAME, "title").click()
    dataset_updated_title = "tester fakenodo selenium 2"
    self.driver.find_element(By.NAME, "title").send_keys(dataset_updated_title)
    self.driver.find_element(By.CSS_SELECTOR, ".mb-2:nth-child(2) > .form-control:nth-child(2)").click()
    self.driver.find_element(By.CSS_SELECTOR, ".mb-2:nth-child(2) > .form-control:nth-child(2)").send_keys("tester lalala")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-outline-secondary:nth-child(4)").click()
    assert self.driver.switch_to.alert.text == "Metadata guardada (sin nuevo DOI)."
    self.driver.switch_to.alert.accept()
    self.driver.find_element(By.NAME, "file").send_keys(os.path.abspath("app/modules/dataset/csv_examples/file10.csv"))
    self.driver.find_element(By.CSS_SELECTOR, ".btn-outline-primary:nth-child(3)").click()
    assert self.driver.switch_to.alert.text == "Archivo subido. Se marcó dirty para nueva versión."
    self.driver.switch_to.alert.accept()
    self.driver.find_element(By.ID, "publishBtn").click()
    assert self.driver.switch_to.alert.text == "¿Publicar el dataset en FakeNODO? Esto generará el DOI y notificará a tus seguidores."
    self.driver.switch_to.alert.accept()
    try:
      self.driver.find_element(By.LINK_TEXT, dataset_updated_title).click()
    except NoSuchElementException:
      try:
        self.driver.find_element(By.LINK_TEXT, dataset_initial_title).click()
      except NoSuchElementException:
        pass
    self.vars["window_handles"] = self.driver.window_handles

if __name__ == "__main__":
  pytest.main([__file__])