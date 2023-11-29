"""
    Created by @namhainguyen2803 in 25/11/2023
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_BINARY_LOCATION = "/usr/bin/chrome-linux64/chrome"
CHROMEDRIVER_BINARY_LOCATION = "/usr/bin/chromedriver-linux64/chromedriver"

def add_driver_options(options):
    """
    Add configurable options
    """
    chrome_options = Options()
    for opt in options:
        chrome_options.add_argument(opt)
    return chrome_options

def initialize_driver():
    """
    Initialize the web driver
    """
    driver_config = {
        "options": [
            "--headless",
            "--no-sandbox",
            "--allow-insecure-localhost",
            "--disable-dev-shm-usage",
            "--incognito",
            "--window-size=1920x1080"
            "user-agent=Chrome/116.0.5845.96"
        ],
    }
    options = add_driver_options(driver_config["options"])
    options.binary_location = CHROME_BINARY_LOCATION
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_BINARY_LOCATION,
        options=options)
    return driver
