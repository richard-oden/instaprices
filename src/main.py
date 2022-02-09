from multiprocessing.dummy import freeze_support
from clients.SeleniumClient import SeleniumClient
from models.Store import Store
import helpers.instaprices_helper as instaprices_helper
import multiprocessing

def get_store(store_name, shopping_list):
    selenium_client = SeleniumClient()
    instaprices_helper.navigate_to_stores(selenium_client)

    retailer_card = next(filter(lambda rc: store_name in rc.text, instaprices_helper.get_retailer_cards(selenium_client)), None)

    if (retailer_card is None):
        selenium_client.driver.quit()
        return

    retailer_card.click()

    items = {}
    for search_term in shopping_list:
        instaprices_helper.search_items(selenium_client, search_term)
        items[search_term] = list(
            map(lambda fc: instaprices_helper.get_item(fc, search_term), 
            filter(lambda ic: search_term in ic.text.lower(), instaprices_helper.get_item_cards(selenium_client)))
        )

    selenium_client.driver.quit()

    return Store(store_name, items)

if __name__ == '__main__':
    shopping_list = ['strawberries']

    initial_selenium_client = SeleniumClient()
    instaprices_helper.navigate_to_stores(initial_selenium_client)
    store_names = instaprices_helper.get_store_names(initial_selenium_client)
    initial_selenium_client.driver.quit()

    pool = multiprocessing.Pool()
    stores = pool.starmap(get_store, map(lambda sn: (sn, shopping_list), store_names))
    pool.close()

    print(store_names)