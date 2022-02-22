import os
import json
from models.CountedItem import CountedItem
from models.Store import Store
from models.WeighedItem import WeighedItem

def get_import_txt_files():
    return [f for f in os.listdir('import') if f.endswith('.txt')]

def get_import_json_files():
    return [f for f in os.listdir('import') if f.endswith('.json')]

def import_file(file_name):
    try:
        with open(f'import/{file_name}', 'r') as file:
            contents = file.read()
            file.close()
        
        return contents
    except:
        return

def parse_item(item_dict):
    if 'price_per_count' in item_dict:
        return CountedItem(item_dict['name'], item_dict['price_total'], item_dict['count'])

    return WeighedItem(item_dict['name'], item_dict['price_total'], item_dict['weight_g'])

def parse_stores(json_string):
    store_dicts = json.loads(json_string)
    stores = [Store(s['name'], [parse_item(i) for i in s['items']]) for s in store_dicts]