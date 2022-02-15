from models.MenuOption import MenuOption
from models.Store import Store
import helpers.instaprices_helper as instaprices_helper
import helpers.selenium_helper as selenium_helper
import helpers.menu_helper as menu_helper

if __name__ == '__main__':
    menu_helper.clear()
    stores = menu_helper.print_main_menu()
    print(stores)