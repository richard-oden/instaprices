from models.MenuOption import MenuOption
from models.Store import Store
import helpers.instaprices_helper as instaprices_helper
import helpers.menu_helper as menu_helper

shopping_list = ['eggs']

def get_store(store_name):
    retailer_card = next(filter(lambda rc: store_name in rc.text, instaprices_helper.get_retailer_cards()), None)

    if (retailer_card is None):
        instaprices_helper.return_to_stores()
        return

    retailer_card.click()

    items = {}
    for search_term in shopping_list:
        if not instaprices_helper.search_items(search_term):
            continue

        items[search_term] = instaprices_helper.get_items(search_term)

    instaprices_helper.return_to_stores()

    return Store(store_name, items)

if __name__ == '__main__':
    menu_helper.print_menu(
        'Enter shopping list manually or import from CSV?',
        [
            MenuOption('Enter manually', print('')),
            MenuOption('Import from CSV', print('')),
        ]
    )

    instaprices_helper.navigate_to_stores()
    store_names = instaprices_helper.get_store_names()

    stores = list(map(get_store, store_names))

    print(store_names)