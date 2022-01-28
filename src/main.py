import selenium_helper
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

selenium_helper.driver.get('https://www.instacart.com/')

address_input = selenium_helper.try_find_element_then_click(By.ID, 'address_input1')

use_location_button = selenium_helper.try_find_element_then_click(By.CSS_SELECTOR, 'button[data-testid="address-results-use-current-location"]')

retailer_cards = selenium_helper.try_find_elements_until(
    lambda: selenium_helper.try_find_elements_with_fallbacks(By.CSS_SELECTOR, 'button[class*="RetailerCard"]', 'span[class*="StoreCompactCard"]'),
    lambda elements: elements is not None and len(elements) > 0
)

aldi_card = next(filter(lambda rc: 'ALDI' in rc.text, retailer_cards), None)

aldi_card.click()

search_input = selenium_helper.try_find_visible_element(By.CSS_SELECTOR, 'input[aria-label="search"]')
search_input.send_keys('bananas', Keys.ENTER)

item_cards = selenium_helper.try_find_elements_until(
    lambda: selenium_helper.try_find_visible_elements(By.CSS_SELECTOR, 'div[class*="ItemBCard"]'),
    lambda elements: elements is not None and any('$' in e.text.lower() for e in elements)
)

raw_results = list(
    map(lambda fc: selenium_helper.get_item_values(fc, 'bananas'), 
    filter(lambda ic: 'bananas' in ic.text.lower(), item_cards))
)

print(raw_results)