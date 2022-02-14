import os
from helpers import instaprices_helper

from models.MenuOption import MenuOption

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def try_int(string):
    try:
        return int(string), True
    except ValueError:
        return None, False

def try_list(string):
    try:
        return [s.strip() for s in string.split(',')], True
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
    return user_input == 'q' or (int_tuple[1] and -1 < int_tuple[0] < len(menu_options))

def print_menu(prompt, menu_options):
    print(bordered('\n'.join([prompt, *[f'  [{menu_options.index(mu)}] {mu.desc}' for mu in menu_options]])))
    choice = input_loop(
        'Enter the number for your selection or "Q" to quit: ', 
        lambda user_input: valid_menu_choice(user_input, menu_options)
    )

    if choice == 'q':
        return
    
    clear()
    return menu_options[int(choice)].execute()

def print_main_menu():
    return print_menu(
        'Enter shopping list manually or import from CSV?',
        [
            MenuOption('Enter manually', lambda: instaprices_helper.get_stores(input_shopping_list())),
            MenuOption('Import from CSV', lambda: print('CSV import goes here')),
        ]
    )

def valid_shopping_list(user_input):
    list_tuple = try_list(user_input)
    return list_tuple[1] and len(list_tuple[0]) > 0

def input_shopping_list():
    return input_loop(
        'Enter a comma-separated shopping list (e.g., "peanut butter, eggs, organic bananas, potatoes"), or "Q" to quit.\n',
        valid_shopping_list,
        lambda user_input: [s.strip() for s in user_input.split(',')]
    )