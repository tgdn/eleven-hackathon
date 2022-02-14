from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class Scraper:
    def __init__(self):
        chrome_options = Options()
        # We dont want to see the window.
        chrome_options.add_argument("--headless")

        # log_level: disable annoying logs.
        # cache_valid_range: cache the driver for n days.
        self.driver = webdriver.Chrome(
            ChromeDriverManager(log_level=0, cache_valid_range=7).install(),
            options=chrome_options,
        )

    def get_airlines():
        pass

    def get(self, url):
        """Return a soup of the scraped page"""
        self.driver.get(url)
        return BeautifulSoup(self.driver.page_source, "lxml")
