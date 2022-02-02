from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
wait = WebDriverWait(driver, 5)

def try_find_visible_element(by, value):
    try:
        return wait.until(EC.visibility_of_element_located((by, value)))
    except:
        return None

def try_find_visible_elements(by, value):
    try:
        return wait.until(EC.visibility_of_all_elements_located((by, value)))
    except:
        return None

def try_find_elements(by, value):
    try:
        return driver.find_elements(by, value)
    except:
        return None

def try_find_elements_with_fallbacks(by, *values):
    for value in values:
        elements = try_find_elements(by, value)
        if elements is not None and len(elements) > 0:
            return elements
    return None

def try_find_element_then_click(by, value):
    try:
        wait.until(EC.element_to_be_clickable((by, value))).click()
        return True
    except:
        return False

def try_find_elements_until(find_elements_fn, until_condition_fn, attempt_limit = 5, second_delay = 1):
    elements = find_elements_fn()
    attempts = 0

    while not until_condition_fn(elements) and attempts < attempt_limit:
        sleep(second_delay)
        elements = find_elements_fn()
        attempts += 1
    
    return elements