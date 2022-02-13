import os

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = [f'┌{"─" * width}┐']
    for s in lines:
        res.append(f'│{(s + " " * width)[:width]}│')
    res.append(f'└{"─" * width}┘')
    return '\n'.join(res)

def print_menu(prompt, menu_options):
    print(bordered('\n'.join([prompt, *[f'  [{menu_options.index(mu)}] {mu.desc}' for mu in menu_options]])))