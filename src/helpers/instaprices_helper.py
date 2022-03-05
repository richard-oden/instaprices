import inflect
import re
import helpers.selenium_helper as selenium_helper
from colorama import Fore
from models.CountedItem import CountedItem
from models.Store import Store
from models.WeighedItem import WeighedItem
from selenium.common.exceptions import WebDriverException

inflect_engine = inflect.engine()

def get_store_names():
    '''
    Returns a list of store names listed on Instacart's stores page.
    '''
    return list(set(map(lambda rc: rc.text.split('\n')[0], selenium_helper.get_retailer_cards())))

def get_search_term_variations(search_term):
    '''
    Returns an array of tuples representing singular/plural variants of each word in the search term.
    '''
    variations = []
    for word in search_term.split():
        singular = inflect_engine.singular_noun(search_term)
        if not singular:
            variations.append((word, inflect_engine.plural_noun(word)))
            continue
        
        variations.append((singular, word))
    return variations

def contains_search_term(text_to_search, search_term_variations):
    '''
    Returns true if the text contains at least one variation of each word in the search term as a whole word.
    '''
    return all(any(re.search(fr'\b{v}\b', text_to_search, re.IGNORECASE) for v in vs) for vs in search_term_variations)

def filter_items(item_texts, search_term_variations):      
    '''
    Returns item texts that contain the search term.
    '''  
    return filter(
        lambda it: contains_search_term(it, search_term_variations), 
        item_texts
    )

def get_item_texts(attempts = 0):
    '''
    Returns a list of item texts from an Instacart item search page. If a WebDriverException occurs, reattempts a maximum of 3 times before returning an empty list.
    '''
    try:
        item_cards = selenium_helper.get_item_cards()
        return [] if item_cards is None else [ic.text for ic in item_cards]
    except WebDriverException:
        return [] if attempts > 3 else get_item_texts(attempts + 1)

def get_items(search_term):
    '''
    Searches Instacart and returns a list of Item objects that match the search term.
    '''
    print(f'  Searching for {search_term}...', end='\r')
    search_term_variations = get_search_term_variations(search_term)

    return list(filter(lambda i: i is not None, # filter out Items that are None
        map(lambda i: get_item(i, search_term_variations), # create an Item from each item text
            filter_items(get_item_texts(), search_term_variations) # get item texts that match the search term
        )))

def get_total_price(price_nodes):
    '''
    Returns the total price of an item. Returns None if the total price could not be found.
    '''
    total_price_node = next(filter(lambda _: not 'express' in _.lower() and not 'each' in _.lower(), price_nodes), None)
    if total_price_node is None:
        return

    match = re.search(r'\$ ?(\d+.\d{2})', total_price_node)

    if match is None:
        return

    return float(match.group(1))

def get_weight_in_grams(quantity_node):
    '''
    Returns the weight of an item in grams. If only a volumetric measurement was found, assumes the density of water. Returns None if a measurement could not be found.
    '''
    unit_match = re.search(r'\b(lb|oz|fl oz|gal|g|l|ml)\b', quantity_node, re.IGNORECASE)
    if (unit_match is None):
        return

    unit = unit_match.group(1).lower()

    if '$' in quantity_node and unit == 'lb':
        return 453.592

    quantity = None
    # Sometimes measurements are listed with a quantity mutliplier. For example, "6 x 12 fl oz". When this happens, 
    # we multiply the found values to get the total weight/volume.
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
    '''
    Returns the count of an item. If a count could not be found, returns None.
    '''
    count_match = re.search(r'\b([\d.]+) (?:ct|ea)\b', count_node, re.IGNORECASE)
    if (count_match is None):
        return

    return float(count_match.group(1))

def get_item(item_text, search_term_variations):
    '''
    Returns an Item object using the item text. The returned Item may be a WeighedItem or a CountedItem depending on whether or not a weight/volume measurement could be found. If an item name, price, or quantity was not found, returns None.
    '''
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
    '''
    Searches an Instacart store for each item in the shopping list and returns a Store object that contains a populated list of items. Navigates the browser back to the stores page upon finishing. If the store could not be found, returns None.
    '''
    print(f'\nRetrieving data from {store_name}...')
    retailer_card = next(filter(lambda rc: rc.text.split('\n')[0] == store_name, selenium_helper.get_retailer_cards()), None)

    if (retailer_card is None):
        return

    retailer_card.click()

    items = {}
    for search_term in shopping_list:
        if not selenium_helper.search_items(search_term):
            continue

        found_items = get_items(search_term)
        if len(found_items) == 0:
            print(Fore.YELLOW + f'  No items were found while searching for {search_term}.' + Fore.RESET)
        else:
            print(f'  Found {len(found_items)} item(s) while searching for {search_term}.')

        items[search_term] = found_items

    selenium_helper.return_to_stores()

    return Store(store_name, items)

def get_stores(shopping_list):
    '''
    Returns a list of populated Store objects by searching each Instacart store's page for each item on the shopping list.
    '''
    selenium_helper.start_driver()
    selenium_helper.navigate_to_stores()
    store_names = get_store_names()
    print(f'Found the following {len(store_names)} store(s): {store_names}')

    stores = list(filter(lambda s: s is not None, [get_store(sn, shopping_list) for sn in store_names]))
    selenium_helper.driver.quit()

    return stores