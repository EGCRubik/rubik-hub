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
    self.driver.get(f"{self.host}/")
    self.driver.set_window_size(2494, 1408)
    
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    
    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar-item:nth-child(8) .align-middle:nth-child(2)")))
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(8) .align-middle:nth-child(2)").click()
    
    self.wait.until(EC.presence_of_element_located((By.ID, "title")))
    self.driver.find_element(By.ID, "title").send_keys("test fakenodo selenium")
    self.driver.find_element(By.ID, "desc").send_keys("test selenium description")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    
    self.wait.until(EC.presence_of_element_located((By.ID, "csv_file")))
    csv_file_path = os.path.abspath("app/modules/dataset/csv_examples/file6.csv")
    self.driver.find_element(By.ID, "csv_file").send_keys(csv_file_path)
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    
    time.sleep(2)
    
    try:
      sync_button = self.driver.find_element(By.CSS_SELECTOR, "form > .btn-outline-primary")
      sync_button.click()
      self.wait.until(EC.alert_is_present())
      self.driver.switch_to.alert.accept()
      time.sleep(2)
    except NoSuchElementException:
      pass
    
    self.driver.get(f"{self.host}/dataset/list")
    self.wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "test fakenodo selenium")))
    self.driver.find_element(By.PARTIAL_LINK_TEXT, "test fakenodo selenium").click()
    
    time.sleep(1)
    try:
      sync_button = self.driver.find_element(By.CSS_SELECTOR, "form > .btn-outline-primary")
      sync_button.click()
      self.wait.until(EC.alert_is_present())
      self.driver.switch_to.alert.accept()
      time.sleep(2)
      self.driver.refresh()
      time.sleep(1)
    except NoSuchElementException:
      pass
    
    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".doi_text")))
    doi_element = self.driver.find_element(By.CSS_SELECTOR, ".doi_text")
    doi_text = doi_element.text
    assert "10.5281/fakenodo" in doi_text
    
  
    doi_match = re.search(r"10\.5281/fakenodo\.\d+", doi_text)
    assert doi_match, f"Could not extract DOI from: {doi_text}"
    doi_value = doi_match.group(0)
    self.driver.get(f"{self.host}/doi/{doi_value}")
    
    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-header")))
    assert "Version" in self.driver.page_source or "version" in self.driver.page_source
    
    self.driver.back()
    self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Crear nueva versión")))
    self.driver.find_element(By.LINK_TEXT, "Crear nueva versión").click()
    
    self.wait.until(EC.presence_of_element_located((By.ID, "version_comment")))
    self.driver.find_element(By.ID, "version_comment").send_keys("cambio menor selenium")
    self.driver.find_element(By.ID, "desc").send_keys(" - updated")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    
    time.sleep(1)
    self.driver.get(f"{self.host}/dataset/list")
    self.wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "test fakenodo selenium")))
    datasets = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "test fakenodo selenium")
    datasets[0].click()
    
    self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Crear nueva versión")))
    self.driver.find_element(By.LINK_TEXT, "Crear nueva versión").click()
    
    self.wait.until(EC.presence_of_element_located((By.ID, "is_major")))
    dropdown = self.driver.find_element(By.ID, "is_major")
    dropdown.find_element(By.XPATH, "//option[. = 'Major release (X.0)']").click()
    self.driver.find_element(By.ID, "version_comment").send_keys("major release with new file")
    
    self.driver.find_element(By.ID, "modify_file_checkbox").click()
    time.sleep(0.5) 
    
    csv_file_path2 = os.path.abspath("app/modules/dataset/csv_examples/file10.csv")
    self.driver.find_element(By.ID, "csv_file").send_keys(csv_file_path2)
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    
    time.sleep(3)
    
    self.driver.get(f"{self.host}/dataset/list")
    self.wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "test fakenodo selenium")))
    datasets = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "test fakenodo selenium")
    datasets[0].click()
    
    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".doi_text")))
    doi_element = self.driver.find_element(By.CSS_SELECTOR, ".doi_text")
    doi_pattern = r"10\.5281/fakenodo\.\d{7}"
    assert re.search(doi_pattern, doi_element.text), f"DOI format invalid: {doi_element.text}"


if __name__ == "__main__":
  pytest.main([__file__])