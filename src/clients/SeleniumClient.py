from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumClient():
    _service = Service(ChromeDriverManager().install())

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.experimental_options["prefs"] = {
            "profile.default_content_settings": {"images": 2},
            "profile.managed_default_content_settings": {"images": 2}
        }

        self.driver = webdriver.Chrome(service=self._service, chrome_options=chrome_options)
        self.wait = WebDriverWait(self.driver, 5)

    def try_find_visible_element(self, by, value):
        try:
            return self.wait.until(EC.visibility_of_element_located((by, value)))
        except:
            return None

    def try_find_visible_elements(self, by, value):
        try:
            return self.wait.until(EC.visibility_of_all_elements_located((by, value)))
        except:
            return None

    def try_find_elements(self, by, value):
        try:
            return self.driver.find_elements(by, value)
        except:
            return None

    def try_find_elements_with_fallbacks(self, by, *values):
        for value in values:
            elements = self.try_find_elements(by, value)
            if elements is not None and len(elements) > 0:
                return elements
        return None

    def try_find_element_then_click(self, by, value):
        try:
            self.wait.until(EC.element_to_be_clickable((by, value))).click()
            return True
        except:
            return False

    def try_find_elements_until(self, find_elements_fn, until_condition_fn, attempt_limit = 5, second_delay = 1):
        elements = find_elements_fn()
        attempts = 0

        while not until_condition_fn(elements) and attempts < attempt_limit:
            sleep(second_delay)
            elements = find_elements_fn()
            attempts += 1
        
        return elements