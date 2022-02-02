import selenium_helper
from Store import Store
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

shopping_list = ['whole milk', 'bread', 'eggs', 'bananas', 'bacon']

def get_retailer_cards():
    return selenium_helper.try_find_elements_until(
        lambda: selenium_helper.try_find_elements_with_fallbacks(By.CSS_SELECTOR, 'button[class*="RetailerCard"]', 'span[class*="StoreCompactCard"]'),
        lambda elements: elements is not None and len(elements) > 0
)

def get_stores():
    return list(map(lambda rc: Store(rc.text.split('\n')[0]), get_retailer_cards()))

selenium_helper.driver.get('https://www.instacart.com/')

address_input = selenium_helper.try_find_element_then_click(By.ID, 'address_input1')

use_location_button = selenium_helper.try_find_element_then_click(By.CSS_SELECTOR, 'button[data-testid="address-results-use-current-location"]')
sleep(1)

stores = get_stores()
for store in stores:
    retailer_cards = get_retailer_cards()
    aldi_card = next(filter(lambda rc: store.name in rc.text, retailer_cards), None)
    aldi_card.click()

    for item in shopping_list:
        search_input = selenium_helper.try_find_visible_element(By.CSS_SELECTOR, 'input[aria-label="search"]')
        search_input.send_keys(Keys.CONTROL, 'a')
        search_input.send_keys(Keys.DELETE)
        search_input.send_keys(item, Keys.ENTER)

        item_cards = selenium_helper.try_find_elements_until(
            lambda: selenium_helper.try_find_visible_elements(By.CSS_SELECTOR, 'div[class*="ItemBCard"]'),
            lambda elements: elements is not None and any('$' in e.text.lower() for e in elements)
        )

        store.items[item] = list(
            map(lambda fc: selenium_helper.get_items(fc, item), 
            filter(lambda ic: item in ic.text.lower(), item_cards))
        )

    selenium_helper.driver.get('https://www.instacart.com/store')

print(stores)