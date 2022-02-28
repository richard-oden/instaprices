import helpers.instaprices_helper as instaprices_helper
import helpers.menu_helper as menu_helper
import helpers.analysis_helper as analysis_helper

def main():
    try:
        menu_helper.clear()
        shopping_list, stores = menu_helper.main_menu()

        menu_helper.clear()
        menu_helper.export_stores_menu(stores)
        
        while True:
            menu_helper.clear()
            analysis_options = menu_helper.analysis_menu()
            analysis_helper.build_chart(stores, shopping_list, analysis_options)
            if not menu_helper.retry_analysis_menu():
                break

        print('Goodbye!')
    except SystemExit:
        print('Goodbye!')

if __name__ == '__main__':
    main()