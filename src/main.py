from multiprocessing.pool import ThreadPool
from clients.SeleniumClient import SeleniumClient
from models.Store import Store
import helpers.instaprices_helper as instaprices_helper
from concurrent.futures import ThreadPoolExecutor

shopping_list = ['banana']

def get_store(store_name):
    selenium_client = SeleniumClient()
    instaprices_helper.navigate_to_stores(selenium_client)

    retailer_card = next(filter(lambda rc: store_name in rc.text, instaprices_helper.get_retailer_cards(selenium_client)), None)

    if (retailer_card is None):
        selenium_client.driver.quit()
        return None

    retailer_card.click()

    items = {}
    for search_term in shopping_list:
        if not instaprices_helper.search_items(selenium_client, search_term):
            selenium_client.driver.quit()
            continue

        items[search_term] = instaprices_helper.get_items(search_term, selenium_client)

    selenium_client.driver.quit()

    return Store(store_name, items)

if __name__ == '__main__':
    initial_selenium_client = SeleniumClient()
    instaprices_helper.navigate_to_stores(initial_selenium_client)
    store_names = instaprices_helper.get_store_names(initial_selenium_client)
    initial_selenium_client.driver.quit()

    with ThreadPoolExecutor(max_workers=3) as executor:
        stores = list(executor.map(get_store, store_names))

    print(store_names)