from clients.SeleniumClient import SeleniumClient
import helpers.instaprices_helper as instaprices_helper
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

shopping_list = ['strawberries']
initial_selenium_client = SeleniumClient()
instaprices_helper.navigate_to_stores(initial_selenium_client)

sleep(1)

stores = instaprices_helper.get_stores(initial_selenium_client)
initial_selenium_client.driver.quit()

for store in stores:
    selenium_client = SeleniumClient()
    instaprices_helper.navigate_to_stores(selenium_client)

    retailer_card = next(filter(lambda rc: store.name in rc.text, instaprices_helper.get_retailer_cards(selenium_client)), None)

    if (retailer_card is None):
        continue

    retailer_card.click()

    for search_term in shopping_list:
        search_input = selenium_client.try_find_visible_element(By.CSS_SELECTOR, 'input[aria-label="search"]')
        search_input.send_keys(Keys.CONTROL, 'a')
        search_input.send_keys(Keys.DELETE)
        search_input.send_keys(search_term, Keys.ENTER)

        store.items[search_term] = list(
            map(lambda fc: instaprices_helper.get_items(fc, search_term), 
            filter(lambda ic: search_term in ic.text.lower(), instaprices_helper.get_item_cards()))
        )

    selenium_client.driver.quit()

print(stores)