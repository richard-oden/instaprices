from CountedItem import CountedItem 
from WeighedItem import WeighedItem
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
wait = WebDriverWait(driver, 10)

def try_find_visible_element(by, value):
    try:
        return wait.until(EC.visibility_of_element_located((by, value)))
    except:
        return None

def try_find_visible_elements(by, value):
    try:
        return wait.until(EC.visibility_of_all_elements_located((by, value)))
    except:
        return None

def try_find_elements(by, value):
    try:
        return driver.find_elements(by, value)
    except:
        return None

def try_find_elements_with_fallbacks(by, *values):
    for value in values:
        elements = try_find_elements(by, value)
        if elements is not None and len(elements) > 0:
            return elements
    return None

def try_find_element_then_click(by, value):
    try:
        wait.until(EC.element_to_be_clickable((by, value))).click()
        return True
    except:
        return False

def try_find_elements_until(find_elements_fn, until_condition_fn, attempt_limit = 5, second_delay = 1):
    elements = find_elements_fn()
    attempts = 0

    while not until_condition_fn(elements) and attempts < attempt_limit:
        sleep(second_delay)
        elements = find_elements_fn()
        attempts += 1
    
    return elements

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

def get_items(item_card, search_term):
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