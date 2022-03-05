import os
import re
import sys
from helpers import instaprices_helper, io_helper
from models.AnalysisOptions import AnalysisOptions, PriceAggregate, PriceType

from models.MenuOption import MenuOption

def clear():
    '''
    Clears the console.
    '''
    os.system('cls' if os.name=='nt' else 'clear')

def try_int(string):
    '''
    Attempts to parse the supplied string to an int. Returns a tuple where the first value is the parsed int on 
    a success, or None on a failure, and the second value is a bool, indicating whether or not the attempt was successful.
    '''
    try:
        return int(string), True
    except ValueError:
        return None, False

def parse_list(string):
    '''
    Parses the supplied comma-separated list string to a list object and returns the result.
    '''
    return [s.strip() for s in string.split(',') if s.strip()]

def try_list(string):
    '''
    Attempts to parse the supplied string to a list. Returns a tuple where the first value is the parsed list on 
    a success, or None on a failure, and the second value is a bool, indicating whether or not the attempt was successful.
    '''
    try:
        return parse_list(string), True
    except:
        return None, False

def bordered(text):
    '''
    Returns the supplied text with an ASCII border.
    '''
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    result = [f'┌{"─" * width}┐']

    for s in lines:
        result.append(f'│{(s + " " * width)[:width]}│')
    result.append(f'└{"─" * width}┘')

    return '\n'.join(result)

def input_loop(prompt, validator_fn, transform_fn = None):
    '''
    Prompts the user for input while the supplied validator function returns False, then returns the result.
    If a transform function is provided, returns the result of the transform function when called with the user's
    input as an argument.
    '''
    valid_input = False

    while not valid_input:
        user_input = input(prompt).lower()
        valid_input = validator_fn(user_input)
        if not valid_input:
            print("Invalid input.")

    return user_input if transform_fn is None else transform_fn(user_input)

def valid_menu_choice(user_input, menu_options):
    '''
    Returns True if user_input is a valid menu choice given the list of MenuOptions. Otherwise returns False.
    '''
    int_tuple = try_int(user_input)
    return (user_input == 'q' or 
        int_tuple[1] and -1 < int_tuple[0] < len(menu_options) and 
        (menu_options[int(user_input)].validator_fn is None or menu_options[int(user_input)].validator_fn()))

def print_menu(prompt, menu_options):
    '''
    Prints a menu given the supplied prompt and menu_options arguments.
    '''
    print(bordered('\n'.join([prompt, *[f'  [{menu_options.index(mu)}] {mu.desc}' for mu in menu_options]])))
    choice = input_loop(
        'Enter the number for your selection or "Q" to quit: ', 
        lambda user_input: valid_menu_choice(user_input, menu_options)
    )

    if choice == 'q':
        sys.exit()
    
    clear()
    return menu_options[int(choice)].fn()

def main_menu():
    '''
    The main menu for Instaprices. Returns a tuple containing the shopping list and a list of Store objects 
    either by scraping data via Selenium or importing from a JSON file.
    '''
    return print_menu('Scrape data using Selenium or import data from JSON?',
        [
            MenuOption('Use Selenium', get_shopping_list_and_stores),
            MenuOption('Import from JSON file', import_stores_menu)
        ])

def shopping_list_menu():
    '''
    Prompts the user to either input the shopping list in the console or import it from a text file.
    Returns a list of strings representing the shopping list.
    '''
    return print_menu('Enter shopping list manually or import from text file?',
        [
            MenuOption('Enter manually', input_shopping_list),
            MenuOption('Import from text file', import_shopping_list_menu),
        ])

def import_shopping_list_menu():
    '''
    Prompts the user to select a text file from which to import the shopping list. Returns a list of strings representing the shopping list.
    '''
    menu_options = list(map(
        lambda f: MenuOption(f, lambda: import_shopping_list(f), lambda: valid_shopping_list(io_helper.import_file(f))), 
        io_helper.get_import_txt_files()))

    return print_menu('Select the file to import from the import directory.', 
        menu_options)

def valid_shopping_list(user_input):
    '''
    Returns True if the supplied string is a valid shopping list. Otherwise returns False.
    '''
    list_tuple = try_list(user_input.replace('\n', ''))
    return list_tuple[1] and len(list_tuple[0]) > 0

def input_shopping_list():
    '''
    Prompts the user to input a shopping list. Returns a list of strings representing the shopping list.
    '''
    return input_loop(
        'Enter a comma-separated shopping list (e.g., "peanut butter, eggs, organic bananas, potatoes"), or "Q" to quit.\n',
        valid_shopping_list,
        parse_list
    )

def import_shopping_list(file_name):
    '''
    Returns the contents of the text file with the supplied name parsed to a list object.
    '''
    return parse_list(io_helper.import_file(file_name))

def get_shopping_list_and_stores():
    '''
    Prompts the user for a shopping list and starts scraping data using Selenium. 
    Returns a tuple containing the shopping list and a list of Store objects.
    '''
    shopping_list = shopping_list_menu()
    stores = instaprices_helper.get_stores(shopping_list)
    return shopping_list, stores

def import_stores_menu():
    '''
    Prompts the user to import stores from a json file. Returns a tuple 
    containing the shopping list and a list of Store objects. 
    '''
    menu_options = list(map(
        lambda f: MenuOption(f, lambda: import_shopping_list_and_stores(f)), 
        io_helper.get_import_json_files()))

    return print_menu('Select the file to import from the import directory.', 
        menu_options)

def import_shopping_list_and_stores(file_name):
    '''
    Reads the contents of the JSON file with the supplied name and returns a tuple 
    containing a shopping list and a list of Store objects. 
    '''
    stores = io_helper.deserialize_stores(io_helper.import_file(file_name))
    shopping_list = []
    
    for s in stores:
        for i in s.items:
            if i not in shopping_list:
                shopping_list.append(i)

    return shopping_list, stores

def export_stores_menu(stores):
    '''
    Asks the user whether or not they would like to export the supplied list of Store objects. 
    If the user selects Yes, exports the stores as a new JSON file.
    '''
    return print_menu('Export stores before proceding to analysis?', 
        [
            MenuOption('Yes', lambda: export_stores(stores)),
            MenuOption('No', lambda: None)
        ])

def export_stores(stores):
    '''
    Prompts the user for a file name, then exports the supplied list of Store objects
    as a new JSON file.
    '''
    file_name = input_loop('Enter a file name: ', 
        lambda user_input: not re.match('[\/\\?%*:|"<>]', user_input),
        lambda user_input: user_input + '.json')
    stores_json = io_helper.serialize_stores(stores)

    if io_helper.export_file(file_name, stores_json):
        print(f'Successfully exported stores to /export/{file_name}.')
        return
    
    print('Failed to export stores.')
    
def analysis_menu():
    '''
    Prompts the user for analysis options. Returns an AnalysisOptions object.
    '''
    price_type = print_menu('Compare items by unit price or total price? Note that items which are counted, \nsuch as eggs, may be compared by count if a unit price is selected.', 
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
    '''
    Asks the user whether or not they would like to run the analysis again. 
    Returns True if the user selects Yes, or False if the user selects No.
    '''
    return print_menu('Retry analysis using different options?', 
        [
            MenuOption('Yes', lambda: True),
            MenuOption('No', lambda: False)
        ])