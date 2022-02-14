import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# hide webdriver_manager logs:
os.environ['WDM_LOG_LEVEL'] = '0'

# create service object:
_service = Service(ChromeDriverManager().install())

# disable image loading:
_chrome_options = webdriver.ChromeOptions()
_chrome_options.experimental_options["prefs"] = {
    "profile.default_content_settings": {"images": 2},
    "profile.managed_default_content_settings": {"images": 2}
}

# hide selenium logs:
_chrome_options.add_argument("--log-level=3")

# create WebDriver
driver = webdriver.Chrome(service=_service, chrome_options=_chrome_options)
_wait = WebDriverWait(driver, 5)
    

def try_find_visible_element(by, value):
    '''
    Attempts to find a visible element. If an element could not be found before the timeout has elapsed, returns None.
    '''
    try:
        return _wait.until(EC.visibility_of_element_located((by, value)))
    except:
        return

def try_find_visible_elements(by, value):
    '''
    Attempts to find visible elements. If the elements could not be found before the timeout has elapsed, returns None.
    '''
    try:
        return _wait.until(EC.visibility_of_all_elements_located((by, value)))
    except:
        return

def try_find_elements(by, value):
    '''
    Attempts to find elements. If the elements could not be found, returns None.
    '''
    try:
        return driver.find_elements(by, value)
    except:
        return

def try_find_elements_with_fallbacks(by, *values):
    '''
    Attempts to find elements, falling back to multiple values if necessary. If the elements could not be found, returns None.
    '''
    for value in values:
        elements = try_find_elements(by, value)
        if elements is not None and len(elements) > 0:
            return elements
    return

def try_find_element_then_click(by, value):
    '''
    Attempts to find clickable element, then clicks it. Returns True if the element was found, and False if it was not.
    '''
    try:
        _wait.until(EC.element_to_be_clickable((by, value))).click()
        return True
    except:
        return False

def try_find_elements_until(find_elements_fn, until_condition_fn, attempt_limit = 5, second_delay = 1):
    '''
    Attempts to find elements until a condition has been met or the attempt limit has been reached, with a delay between each attempt. If the elements could not be found, returns None.
    '''
    elements = find_elements_fn()
    attempts = 0

    while not until_condition_fn(elements) and attempts < attempt_limit:
        sleep(second_delay)
        elements = find_elements_fn()
        attempts += 1
    
    return elements