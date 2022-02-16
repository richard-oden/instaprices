import os

def get_import_files():
    return [f for f in os.listdir('import') if f.endswith('.txt')]

def import_file(file_name):
    try:
        with open(f'import/{file_name}', 'r') as file:
            contents = file.read()
            file.close()
        
        return contents
    except:
        return