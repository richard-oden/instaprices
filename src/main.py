from models.MenuOption import MenuOption
from models.Store import Store
import helpers.instaprices_helper as instaprices_helper
import helpers.selenium_helper as selenium_helper
import helpers.menu_helper as menu_helper

def main():
    menu_helper.clear()
    shopping_list = menu_helper.shopping_list_menu()

    if shopping_list is None:
        print('Goodbye!')
        return

    stores = instaprices_helper.get_stores(shopping_list)
    analysis_options = menu_helper.analysis_menu()
    
    print(stores)

if __name__ == '__main__':
    main()