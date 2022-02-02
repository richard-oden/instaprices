import helpers.selenium_helper as selenium_helper
import helpers.instaprices_helper as instaprices_helper
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

shopping_list = ['strawberries']

selenium_helper.driver.get('https://www.instacart.com/')

was_address_input_clicked = selenium_helper.try_find_element_then_click(By.ID, 'address_input1')
if not was_address_input_clicked:
    raise ValueError('Unable to find address input element.')

was_use_location_button_clicked = selenium_helper.try_find_element_then_click(By.CSS_SELECTOR, 'button[data-testid="address-results-use-current-location"]')
if not was_use_location_button_clicked:
    raise ValueError('Unable to find use location button element.')

sleep(1)

stores = instaprices_helper.get_stores()
for store in stores:
    retailer_card = next(filter(lambda rc: store.name in rc.text, instaprices_helper.get_retailer_cards()), None)

    if (retailer_card is None):
        continue

    retailer_card.click()

    for item in shopping_list:
        search_input = selenium_helper.try_find_visible_element(By.CSS_SELECTOR, 'input[aria-label="search"]')
        search_input.send_keys(Keys.CONTROL, 'a')
        search_input.send_keys(Keys.DELETE)
        search_input.send_keys(item, Keys.ENTER)

        store.items[item] = list(
            map(lambda fc: instaprices_helper.get_items(fc, item), 
            filter(lambda ic: item in ic.text.lower(), instaprices_helper.get_item_cards()))
        )

    selenium_helper.driver.get('https://www.instacart.com/store')

print(stores)