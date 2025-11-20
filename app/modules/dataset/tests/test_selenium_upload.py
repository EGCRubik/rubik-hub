import os
import pytest
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets
    

class TestTestupload():
    def setup_method(self, method):
        # Usa el helper del proyecto, que ya configura bien el navegador
        self.driver = initialize_driver()
        self.vars = {}
    
    def teardown_method(self, method):
        # Puedes usar close_driver, que probablemente maneja bien errores
        try:
            close_driver(self.driver)
        except Exception:
            # Por si acaso:
            self.driver.quit()
  
    def test_testupload(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1224, 688)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()

        initial_datasets = count_datasets(self.driver, "http://127.0.0.1:5000")

        self.driver.find_element(By.LINK_TEXT, "Upload dataset").click()
        wait_for_page_to_load(self.driver)

        # Assert: Verificar que el formulario de upload está cargado
        upload_button = self.driver.find_element(By.CSS_SELECTOR, ".btn-primary")
        assert upload_button.is_displayed(), "Upload button is not displayed!"

        self.driver.find_element(By.ID, "title").click()
        self.driver.find_element(By.ID, "title").send_keys("prueba csv")
        self.driver.find_element(By.ID, "desc").send_keys("prueba csv")

        # Assert: Verificar que los campos se rellenaron correctamente
        title_value = self.driver.find_element(By.ID, "title").get_attribute("value")
        desc_value = self.driver.find_element(By.ID, "desc").get_attribute("value")
        assert title_value == "prueba csv", f"Title field expected 'prueba csv' but got {title_value}"
        assert desc_value == "prueba csv", f"Description field expected 'prueba csv' but got {desc_value}"

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        csv_path = os.path.abspath("app/modules/dataset/csv_examples/file1.csv")

        # Assert: Verificar que el archivo se subió correctamente
        self.driver.find_element(By.ID, "csv_file").send_keys(csv_path)
        csv_input_value = self.driver.find_element(By.ID, "csv_file").get_attribute("value")
        assert "file1.csv" in csv_input_value, f"Expected file to be uploaded, but got {csv_input_value}"

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        wait_for_page_to_load(self.driver)

        # Assert: Verificar que la redirección ocurrió correctamente
        assert self.driver.current_url == "http://127.0.0.1:5000/dataset/list", "Failed to redirect to dataset list page!"

        final_datasets = count_datasets(self.driver, "http://127.0.0.1:5000")

        # Assert: Verificar que el dataset fue añadido correctamente
        assert final_datasets == initial_datasets + 1, "Dataset was not added!"