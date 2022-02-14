import os

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def try_int(string):
    try:
        return int(string), True
    except ValueError:
        return None, False

def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = [f'┌{"─" * width}┐']

    for s in lines:
        res.append(f'│{(s + " " * width)[:width]}│')
    res.append(f'└{"─" * width}┘')

    return '\n'.join(res)

def input_loop(prompt, validator_fn):
    valid_input = False

    while not valid_input:
        res = input(prompt + "\n").lower()
        valid_input = validator_fn(res)

    return res

def valid_menu_choice(res, menu_options):
    int_tuple = try_int(res)
    return res == 'q' or (int_tuple[1] and -1 < int_tuple[0] < len(menu_options))

def print_menu(prompt, menu_options):
    print(bordered('\n'.join([prompt, *[f'  [{menu_options.index(mu)}] {mu.desc}' for mu in menu_options]])))
    choice = input_loop('Enter the number for your selection or "Q" to quit.', lambda res: valid_menu_choice(res, menu_options))

    if choice == 'q':
        return
    
    menu_options[int(choice)].execute()
