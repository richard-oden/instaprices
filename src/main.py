from models.MenuOption import MenuOption
from models.Store import Store
import helpers.instaprices_helper as instaprices_helper
import helpers.selenium_helper as selenium_helper
import helpers.menu_helper as menu_helper

if __name__ == '__main__':
    menu_helper.clear()
    shopping_list = menu_helper.shopping_list_menu()
    stores = instaprices_helper.get_stores(shopping_list)
    print(stores)