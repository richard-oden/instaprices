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
        with open(os.path.join('import', file_name), 'r') as file:
            return file.read()
    except FileNotFoundError:
        return

def export_file(file_name, contents):
    try:
        with open(os.path.join('export', file_name), 'w') as file:
            file.write(contents)
        return True
    except FileNotFoundError:
        return False

def parse_item(item_dict):
    if 'price_per_count' in item_dict:
        return CountedItem(item_dict['name'], float(item_dict['price_total']), float(item_dict['count']))

    return WeighedItem(item_dict['name'], float(item_dict['price_total']), float(item_dict['weight_g']))

def deserialize_stores(json_string):
    store_dicts = json.loads(json_string)
    return [Store(s['name'], {k:[parse_item(i) for i in v] for (k,v) in s['items'].items()}) for s in store_dicts]

def serialize_stores(stores):
    return json.dumps(stores, default=lambda o: o.__dict__, indent=4)