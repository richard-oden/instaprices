import helpers.instaprices_helper as instaprices_helper
import helpers.menu_helper as menu_helper
import helpers.analysis_helper as analysis_helper

def main():
    menu_helper.clear()
    
    shopping_list, stores = menu_helper.main_menu()
    if shopping_list is None or stores is None:
        print('Goodbye!')
        return

    menu_helper.export_stores_menu(stores)
    
    while True:
        analysis_options = menu_helper.analysis_menu()
        analysis_helper.build_chart(stores, shopping_list, analysis_options)
        if not menu_helper.retry_analysis_menu():
            break

    print('Goodbye!')

if __name__ == '__main__':
    main()