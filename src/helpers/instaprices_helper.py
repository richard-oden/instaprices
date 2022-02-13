import inflect
import nltk
import re
from time import sleep
import helpers.selenium_helper as selenium_helper
from models.CountedItem import CountedItem
from models.WeighedItem import WeighedItem
from nltk.corpus import wordnet
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

nltk.download('wordnet')
nltk.download('omw-1.4')

inflect_engine = inflect.engine()
nouns = {s.name().split('.', 1)[0] for s in wordnet.all_synsets('n')}

def navigate_to_stores():
    selenium_helper.driver.get('https://www.instacart.com/')

    was_address_input_clicked = selenium_helper.try_find_element_then_click(By.CSS_SELECTOR, 'input[id*="address_input"]')
    if not was_address_input_clicked:
        print('Unable to find address input element. Attempting to target retailer card...')
        return

    was_use_location_button_clicked = selenium_helper.try_find_element_then_click(By.CSS_SELECTOR, 'button[data-testid="address-results-use-current-location"]')
    if not was_use_location_button_clicked:
        raise ValueError('Unable to find use location button element.')

    selenium_helper.try_find_visible_element(By.CSS_SELECTOR, 'input[id*="address_input"]').send_keys(Keys.ESCAPE)

    sleep(2)

def return_to_stores():
    if not selenium_helper.try_find_element_then_click(By.CSS_SELECTOR, 'span[class*="Logo"]'):
        raise ValueError('Unable to find return to stores button element.')

def get_retailer_cards():
    return selenium_helper.try_find_elements_until(
        lambda: selenium_helper.try_find_elements_with_fallbacks(By.CSS_SELECTOR, 'button[class*="RetailerCard"]', 'span[class*="StoreCompactCard"]'),
        lambda elements: elements is not None and len(elements) > 0
    )

def get_store_names():
    return list(map(lambda rc: rc.text.split('\n')[0], get_retailer_cards()))

def search_items(search_term):
    search_input = selenium_helper.try_find_visible_element(By.CSS_SELECTOR, 'input[aria-label="search"]')
    if search_input is None:
        print('Unable to find search input element.')
        return False

    search_input.send_keys(Keys.CONTROL, 'a')
    search_input.send_keys(Keys.DELETE)
    search_input.send_keys(search_term, Keys.ENTER)
    return True

def get_word_variations(search_term):
    variations = []
    for word in search_term.split():
        if not word.lower() in nouns:
            variations.append((word))
            continue

        singular = inflect_engine.singular_noun(search_term)
        if not singular:
            variations.append((word, inflect_engine.plural_noun(word)))
            continue
        
        variations.append((singular, word))
    return variations

def get_item_cards():
    return selenium_helper.try_find_elements_until(
        lambda: selenium_helper.try_find_visible_elements(By.CSS_SELECTOR, 'div[class*="ItemBCard"]'),
        lambda elements: elements is not None and any('$' in e.text.lower() for e in elements)
    )

def filter_item_cards(item_cards, search_term):        
    return filter(
        lambda ic: all(any(re.search(fr'\b{v}\b', ic.text, re.IGNORECASE) for v in vs) for vs in get_word_variations(search_term)), 
        item_cards
    )

def get_items(search_term):
    return list(
        map(
            lambda fc: get_item(fc, search_term), 
            filter_item_cards(get_item_cards(), search_term)
        )
    )

def get_total_price(price_nodes):
    total_price_node = next(filter(lambda _: not 'express' in _.lower() and not 'each' in _.lower(), price_nodes), None)
    if total_price_node is None:
        return None

    match = re.search(r'\$ ?(\d+.\d{2})', total_price_node)

    if match is None:
        return None

    return float(match.group(1))

def get_weight_in_grams(quantity_node):
    unit_match = re.search(r'\b(lb|oz|fl oz|gal|g|l|ml)\b', quantity_node, re.IGNORECASE)
    if (unit_match is None):
        return None

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
            return None
    
        quantity = float(quantity_match.group(1))
    
    if quantity is None:
        return None

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
    count_match = re.search(r'\b([\d.]+) (?:ct|each|ea)\b', count_node, re.IGNORECASE)
    if (count_match is None):
        return None

    return int(count_match.group(1))

def get_item(item_card, search_term):
    text_nodes = list(map(lambda _: _.strip(), item_card.text.split('\n')))
    if len(text_nodes) == 0:
        return None

    price_nodes = list(filter(lambda _: '$' in _, text_nodes))
    if len(price_nodes) == 0:
        return None

    item_name = next(filter(lambda _: search_term.lower() in _.lower(), text_nodes), None)
    if item_name is None:
        return None

    price_total = get_total_price(price_nodes)
    if price_total is None:
        return None

    weight_or_volume_node = next(filter(lambda _: re.search(r'\b(?:lb|oz|g|fl oz|gal|ml|l)\b', _, re.IGNORECASE), text_nodes), None)
    if weight_or_volume_node is not None:
        weight_grams = get_weight_in_grams(weight_or_volume_node)
        if weight_grams is None:
            return None
        
        return WeighedItem(item_name, price_total, weight_grams)

    count_node = next(filter(lambda _: re.search(r'\b(?:ct|each|ea)\b', _, re.IGNORECASE), text_nodes), None)
    if count_node is not None:
        count = get_count(count_node)
        if count is None:
            return None
        
        return CountedItem(item_name, price_total, count)

    return None