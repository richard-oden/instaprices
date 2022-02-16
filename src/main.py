from helpers import io_helper
from models.MenuOption import MenuOption
from models.Store import Store
import helpers.instaprices_helper as instaprices_helper
import helpers.selenium_helper as selenium_helper
import helpers.menu_helper as menu_helper

if __name__ == '__main__':
    files = io_helper.get_import_files()
    contents = io_helper.import_file(files[0])

    menu_helper.clear()
    stores = menu_helper.print_main_menu()
    print(stores)