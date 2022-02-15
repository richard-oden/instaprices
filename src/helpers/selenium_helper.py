import os
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# hide webdriver_manager logs:
os.environ['WDM_LOG_LEVEL'] = '0'

# create service object:
_service = Service(ChromeDriverManager().install())

# disable image loading for better performance:
_chrome_options = webdriver.ChromeOptions()
_chrome_options.experimental_options["prefs"] = {
    "profile.default_content_settings": {"images": 2},
    "profile.managed_default_content_settings": {"images": 2}
}

# hide selenium logs:
_chrome_options.add_argument("--log-level=3")

# create WebDriver
driver = webdriver.Chrome(service=_service, chrome_options=_chrome_options)
_wait = WebDriverWait(driver, 5, ignored_exceptions=(NoSuchElementException,StaleElementReferenceException))
    

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

def navigate_to_stores():
    '''
    Navigates the browser to Instacart's website and submits the user location if necessary, bringing up local stores.
    '''
    driver.get('https://www.instacart.com/')

    was_address_input_clicked = try_find_element_then_click(By.CSS_SELECTOR, 'input[id*="address_input"]')
    if not was_address_input_clicked:
        # Sometimes the location has already been populated. In this case, we exit early.
        print('Unable to find address input element. Attempting to target retailer card...')
        return

    was_use_location_button_clicked = try_find_element_then_click(By.CSS_SELECTOR, 'button[data-testid="address-results-use-current-location"]')
    if not was_use_location_button_clicked:
        raise ValueError('Unable to find use location button element.')

    # Sometimes the locations dropdown covers the retailer cards, preventing them from being clicked. Pressing the escape key closes this dropdown.
    try_find_visible_element(By.CSS_SELECTOR, 'input[id*="address_input"]').send_keys(Keys.ESCAPE)

    sleep(2)

def return_to_stores():
    '''
    Navigates the browser from the item search page back to the stores page.
    '''
    if not try_find_element_then_click(By.CSS_SELECTOR, 'span[class*="Logo"]'):
        raise ValueError('Unable to find return to stores button element.')

def get_retailer_cards():
    '''
    Gets WebElements representing each store that is listed in the stores page.
    '''
    return filter(lambda e: e.text != '', try_find_elements_until(
        lambda: try_find_elements_with_fallbacks(By.CSS_SELECTOR, 'button[class*="RetailerCard"]', 'span[class*="StoreCompactCard"]'),
        lambda elements: elements is not None and len(elements) > 0
    ))

def search_items(search_term):
    '''
    Searches a store's items, then clears the search input. If the search input could not be found, returns False. Otherwise, returns True.
    '''
    search_input = try_find_visible_element(By.CSS_SELECTOR, 'input[aria-label="search"]')
    if search_input is None:
        print('Unable to find search input element.')
        return False

    search_input.send_keys(Keys.CONTROL, 'a')
    search_input.send_keys(Keys.DELETE)
    search_input.send_keys(search_term, Keys.ENTER)
    return True

def get_item_cards():
    '''
    Gets WebElements representing each item on the item search page.
    '''
    return try_find_elements_until(
        lambda: try_find_visible_elements(By.CSS_SELECTOR, 'div[class*="ItemBCard"]'),
        lambda elements: elements is not None and any('$' in e.text.lower() for e in elements)
    )