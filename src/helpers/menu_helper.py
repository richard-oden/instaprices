import os

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = [f'┌{"─" * width}┐']
    for s in lines:
        res += f'│{(s + " " * width)[:width]}│'
    res += f'└{"─" * width}┘'
    return '\n'.join(res)