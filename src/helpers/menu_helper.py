import os
import re
from helpers import instaprices_helper, io_helper
from models.AnalysisOptions import AnalysisOptions, PriceAggregate, PriceType

from models.MenuOption import MenuOption

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def try_int(string):
    try:
        return int(string), True
    except ValueError:
        return None, False

def parse_list(string):
    return [s.strip() for s in string.split(',') if s.strip()]

def try_list(string):
    try:
        return parse_list(string), True
    except:
        return None, False

def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    result = [f'┌{"─" * width}┐']

    for s in lines:
        result.append(f'│{(s + " " * width)[:width]}│')
    result.append(f'└{"─" * width}┘')

    return '\n'.join(result)

def input_loop(prompt, validator_fn, transform_fn = None):
    valid_input = False

    while not valid_input:
        user_input = input(prompt).lower()
        valid_input = validator_fn(user_input)
        if not valid_input:
            print("Invalid input.")

    return user_input if transform_fn is None else transform_fn(user_input)

def valid_menu_choice(user_input, menu_options):
    int_tuple = try_int(user_input)
    return (user_input == 'q' or 
        int_tuple[1] and -1 < int_tuple[0] < len(menu_options) and 
        (menu_options[int(user_input)].validator_fn is None or menu_options[int(user_input)].validator_fn()))

def print_menu(prompt, menu_options):
    print(bordered('\n'.join([prompt, *[f'  [{menu_options.index(mu)}] {mu.desc}' for mu in menu_options]])))
    choice = input_loop(
        'Enter the number for your selection or "Q" to quit: ', 
        lambda user_input: valid_menu_choice(user_input, menu_options)
    )

    if choice == 'q':
        return
    
    clear()
    return menu_options[int(choice)].fn()

def main_menu():
    '''
    The main menu for Instaprices. Returns a tuple containing the shopping list and a list of Store objects either by scraping data via Selenium or importing from a JSON file.
    '''
    return print_menu('Scrape data using Selenium or import data from JSON?',
        [
            MenuOption('Use Selenium', get_shopping_list_and_stores),
            MenuOption('Import from JSON file', import_stores_menu)
        ])

def shopping_list_menu():
    return print_menu('Enter shopping list manually or import from text file?',
        [
            MenuOption('Enter manually', input_shopping_list),
            MenuOption('Import from text file', import_shopping_list_menu),
        ])

def import_shopping_list_menu():
    menu_options = list(map(
        lambda f: MenuOption(f, lambda: import_shopping_list(f), lambda: valid_shopping_list(io_helper.import_file(f))), 
        io_helper.get_import_txt_files()))

    return print_menu('Select the file to import from the import directory.', 
        menu_options)

def valid_shopping_list(user_input):
    list_tuple = try_list(user_input.replace('\n', ''))
    return list_tuple[1] and len(list_tuple[0]) > 0

def input_shopping_list():
    return input_loop(
        'Enter a comma-separated shopping list (e.g., "peanut butter, eggs, organic bananas, potatoes"), or "Q" to quit.\n',
        valid_shopping_list,
        parse_list
    )

def import_shopping_list(file_name):
    return parse_list(io_helper.import_file(file_name))

def get_shopping_list_and_stores():
    shopping_list = shopping_list_menu()
    stores = instaprices_helper.get_stores(shopping_list)
    return shopping_list, stores

def import_stores_menu():
    menu_options = list(map(
        lambda f: MenuOption(f, lambda: import_shopping_list_and_stores(f)), 
        io_helper.get_import_json_files()))

    return print_menu('Select the file to import from the import directory.', 
        menu_options)

def import_shopping_list_and_stores(file_name):
    stores = io_helper.deserialize_stores(io_helper.import_file(file_name))
    shopping_list = []
    
    for s in stores:
        for i in s.items:
            if i not in shopping_list:
                shopping_list.append(i)

    return shopping_list, stores

def export_stores_menu(stores):
    return print_menu('Export stores before proceding to analysis?', 
        [
            MenuOption('Yes', lambda: export_stores(stores)),
            MenuOption('No', lambda: None)
        ])

def export_stores(stores):
    file_name = input_loop('Enter a file name: ', 
        lambda user_input: not re.match('[\/\\?%*:|"<>]', user_input),
        lambda user_input: user_input + '.json')
    stores_json = io_helper.serialize_stores(stores)

    if io_helper.export_file(file_name, stores_json):
        print(f'Successfully exported stores to /export/{file_name}.')
        return
    
    print('Failed to export stores.')
    
def analysis_menu():
    price_type = print_menu('Compare items by unit price or total price? Note that items which are counted, such as eggs, may be compared by count if a unit price is selected.', 
        [
            MenuOption('unit price (per oz)', lambda: PriceType.PER_OZ),
            MenuOption('unit price (per 100g)', lambda: PriceType.PER_100G),
            MenuOption('total price', lambda: PriceType.TOTAL)
        ])
    
    if price_type is None:
        return
    
    price_aggregate = print_menu('Compare items by cheapest, mean, or median price?', 
        [
            MenuOption('cheapest price', lambda: PriceAggregate.CHEAPEST),
            MenuOption('mean price', lambda: PriceAggregate.MEAN),
            MenuOption('median price', lambda: PriceAggregate.MEDIAN)
        ])

    if price_aggregate is None:
        return
    
    omit_incomplete_stores = print_menu('Omit stores that do not contain all items?', 
        [
            MenuOption('yes', lambda: True),
            MenuOption('no', lambda: False)
        ])

    if omit_incomplete_stores is None:
        return
    
    return AnalysisOptions(price_type, price_aggregate, omit_incomplete_stores)

def retry_analysis_menu():
    return print_menu('Retry analysis using different options?', 
        [
            MenuOption('yes', lambda: True),
            MenuOption('no', lambda: False)
        ])