import os
import shutil

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


def initialize_driver():
    options = webdriver.FirefoxOptions()

    snap_tmp = os.path.expanduser("~/snap/firefox/common/tmp")
    os.makedirs(snap_tmp, exist_ok=True)
    os.environ["TMPDIR"] = snap_tmp

    gecko_path = shutil.which("geckodriver")
    if gecko_path is None:
        raise RuntimeError(
            "geckodriver no se encuentra en PATH. "
            "Instálalo o añade su ruta al PATH."
        )

    service = Service(gecko_path)
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def close_driver(driver):
    driver.quit()
