import inflect
import re
import helpers.selenium_helper as selenium_helper
from models.CountedItem import CountedItem
from models.Store import Store
from models.WeighedItem import WeighedItem

inflect_engine = inflect.engine()

def get_store_names():
    return list(map(lambda rc: rc.text.split('\n')[0], selenium_helper.get_retailer_cards()))

def get_search_term_variations(search_term):
    variations = []
    for word in search_term.split():
        singular = inflect_engine.singular_noun(search_term)
        if not singular:
            variations.append((word, inflect_engine.plural_noun(word)))
            continue
        
        variations.append((singular, word))
    return variations

def contains_search_term(text_to_search, search_term_variations):
    return all(any(re.search(fr'\b{v}\b', text_to_search, re.IGNORECASE) for v in vs) for vs in search_term_variations)

def filter_items(item_texts, search_term_variations):        
    return filter(
        lambda it: contains_search_term(it, search_term_variations), 
        item_texts
    )

def get_items(search_term):
    print(f'  Searching for {search_term}')
    search_term_variations = get_search_term_variations(search_term)

    item_cards = selenium_helper.get_item_cards()
    if item_cards is None:
        return []

    return list(
        map(
            lambda fi: get_item(fi, search_term_variations), 
            filter_items([ic.text for ic in item_cards], search_term_variations)
        )
    )

def get_total_price(price_nodes):
    total_price_node = next(filter(lambda _: not 'express' in _.lower() and not 'each' in _.lower(), price_nodes), None)
    if total_price_node is None:
        return

    match = re.search(r'\$ ?(\d+.\d{2})', total_price_node)

    if match is None:
        return

    return float(match.group(1))

def get_weight_in_grams(quantity_node):
    unit_match = re.search(r'\b(lb|oz|fl oz|gal|g|l|ml)\b', quantity_node, re.IGNORECASE)
    if (unit_match is None):
        return

    unit = unit_match.group(1).lower()

    if '$' in quantity_node and unit == 'lb':
        return 453.592

    quantity = None
    multiple_quantity_match = re.search(r'\b([\d.]+) x ([\d.]+)\b', quantity_node, re.IGNORECASE)
    if multiple_quantity_match is not None:    
        quantity = float(multiple_quantity_match.group(1)) * float(multiple_quantity_match.group(2))
    else:
        quantity_match = re.search(r'\b([\d.]+)\b', quantity_node, re.IGNORECASE)
        if quantity_match is None:
            return
    
        quantity = float(quantity_match.group(1))
    
    if quantity is None:
        return

    return {
        'lb': quantity * 453.592,
        'oz': quantity * 28.349,
        'fl oz': quantity * 29.573, #water
        'gal': quantity * 3785.41, #water
        'g': quantity,
        'ml': quantity, #water
        'l': quantity * 1000 #water
    }[unit]

def get_count(count_node):
    count_match = re.search(r'\b([\d.]+) (?:ct|ea)\b', count_node, re.IGNORECASE)
    if (count_match is None):
        return

    return int(count_match.group(1))

def get_item(item_text, search_term_variations):
    text_nodes = list(map(lambda _: _.strip(), item_text.split('\n')))
    if len(text_nodes) == 0:
        return

    price_nodes = list(filter(lambda _: '$' in _, text_nodes))
    if len(price_nodes) == 0:
        return

    item_name = next(filter(lambda t: contains_search_term(t, search_term_variations), text_nodes), None)
    text_nodes.remove(item_name)
    if item_name is None:
        return

    price_total = get_total_price(price_nodes)
    if price_total is None:
        return

    weight_or_volume_node = next(filter(lambda _: re.search(r'\b(?:lb|oz|g|fl oz|gal|ml|l)\b', _, re.IGNORECASE), text_nodes), None)
    if weight_or_volume_node is not None:
        weight_grams = get_weight_in_grams(weight_or_volume_node)
        if weight_grams is None:
            return
        
        return WeighedItem(item_name, price_total, weight_grams)

    count_node = next(filter(lambda _: re.search(r'\b(?:ct|each|ea)\b', _, re.IGNORECASE), text_nodes), None)
    if count_node is not None:
        count = get_count(count_node)
        if count is None:
            return
        
        return CountedItem(item_name, price_total, count)

    return

def get_store(store_name, shopping_list):
    print(f'Retrieving data for {store_name}.')
    retailer_card = next(filter(lambda rc: store_name in rc.text, selenium_helper.get_retailer_cards()), None)

    if (retailer_card is None):
        return

    retailer_card.click()

    items = {}
    for search_term in shopping_list:
        if not selenium_helper.search_items(search_term):
            continue

        items[search_term] = get_items(search_term)

    selenium_helper.return_to_stores()

    return Store(store_name, items)

def get_stores(shopping_list):
    selenium_helper.navigate_to_stores()
    store_names = get_store_names()

    return [get_store(sn, shopping_list) for sn in store_names]