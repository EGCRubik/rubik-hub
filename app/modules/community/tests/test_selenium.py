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


class TestTesterseleniumcommunity():
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
  
  def test_testerseleniumcommunity(self):
    self.driver.get("http://127.0.0.1:5000/")
    self.driver.set_window_size(2494, 1408)
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(8) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").click()
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(11) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.CSS_SELECTOR, ".feather-plus-circle").click()
    self.driver.find_element(By.ID, "name").click()
    self.driver.find_element(By.ID, "name").send_keys("test selenium")
    self.driver.find_element(By.ID, "slug").click()
    self.driver.find_element(By.ID, "slug").send_keys("selenium")
    self.driver.find_element(By.ID, "description").click()
    self.driver.find_element(By.ID, "description").send_keys("selenium")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    self.driver.find_element(By.LINK_TEXT, "Back to list").click()
    self.driver.find_element(By.LINK_TEXT, "View").click()
    self.driver.find_element(By.NAME, "dataset_id").click()
    self.driver.find_element(By.NAME, "dataset_id").send_keys("1")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-outline-primary").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(9) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(11) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.LINK_TEXT, "View").click()
    self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(11) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.LINK_TEXT, "View").click()

    

if __name__ == "__main__":
  pytest.main([__file__])