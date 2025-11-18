import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestTestDownloadDataset:
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def recuperar_texto_descargas(self):
        # Buscar el elemento que contiene el texto de descargas (el <small> al lado del ícono de descarga)
        descarga_texto = self.driver.find_element(By.CSS_SELECTOR, ".d-flex.flex-column.align-items-center small.text-muted.mt-1")
        # Recuperar y convertir el texto a entero
        return int(descarga_texto.text)

    def test_testDownloadDataset(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(602, 819)
        
        # Hacer clic en "Sample dataset 9"
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 9").click()

        # Recuperar el texto del número de descargas antes de hacer clic en "Download all"
        numero_descargas_inicio = self.recuperar_texto_descargas()

        # Hacer clic en "Download all (1.58 KB)"
        self.driver.find_element(By.LINK_TEXT, "Download all (1.58 KB)").click()
        
        self.driver.find_element(By.CSS_SELECTOR, ".col-xl-8").click()
        self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()

        # Esperar hasta que el elemento sea clickeable y desplazarse a la vista
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".sidebar-item:nth-child(2) .align-middle:nth-child(2)"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()

        self.driver.find_element(By.LINK_TEXT, "Sample dataset 9").click()

        numero_descargas_final = self.recuperar_texto_descargas()

        # Aquí puedes hacer una aserción si es necesario
        assert numero_descargas_final == numero_descargas_inicio + 1, "El número de descargas no se incrementó correctamente."