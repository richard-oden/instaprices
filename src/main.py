import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

def try_find_clickable_element(by, value):
    try:
        return wait.until(EC.element_to_be_clickable((by, value)))
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

def get_express_price(price_nodes):
    express_price_node = next(filter(lambda _: 'express' in _.lower(), price_nodes), None)
    if express_price_node is None:
        return None

    match = re.search(r'\$ ?(\d+.\d{2})', express_price_node)
    if match is None:
        return None

    return float(match.group(1))

def get_total_price(price_nodes):
    total_price_node = next(filter(lambda _: not 'express' in _.lower() and not 'each' in _.lower(), price_nodes), None)
    if total_price_node is None:
        return None

    match = re.search(r'\$ ?(\d+.\d{2})', total_price_node)

    if match is None:
        return None

    return float(match.group(1))

def get_weight_in_grams(text_nodes):
    quantity_node = next(filter(lambda _: re.search(r'\b(?:lb|oz|g|fl oz)\b', _, re.IGNORECASE), text_nodes), None)
    if quantity_node is None:
        return None
    
    unit_match = re.search(r'\b(lb|oz|fl oz|g)\b', quantity_node, re.IGNORECASE)
    if (unit_match is None):
        return None

    unit = unit_match.group(1).lower()

    if '$' in quantity_node and unit == 'lb':
        return 453.592

    quantity_match = re.search(r'\b([\d.]+)\b', quantity_node, re.IGNORECASE)
    if quantity_match is None:
        return None
    
    quantity = quantity_match.group(1)

    return {
        'lb': quantity * 453.592,
        'oz': quantity * 28.349,
        'fl oz': quantity * 29.573, #water
        'g': quantity
    }[unit]


def get_price_per_gram(total_price, weight_grams):
    return total_price / weight_grams

def get_item_values(item_card, search_term):
    text_nodes = list(map(lambda _: _.strip(), item_card.text.split('\n')))
    if len(text_nodes) == 0:
        return None

    price_nodes = list(filter(lambda _: '$' in _, text_nodes))
    if len(price_nodes) == 0:
        return None

    item_name = next(filter(lambda _: re.search(fr'\b{search_term}\b', _, re.IGNORECASE), text_nodes), None)
    if item_name is None:
        return None

    weight_grams = get_weight_in_grams(text_nodes)
    if weight_grams is None:
        return None

    price_total = get_total_price(price_nodes)
    if price_total is None:
        return None
    
    price_per_gram = get_price_per_gram(price_total, weight_grams)
    
    return {
        'name': item_name,
        'weight_grams': weight_grams,
        'weight_ounces': weight_grams / 28.349,
        'price_total': price_total,
        'price_express': get_express_price(price_nodes),
        'price_per_gram': price_per_gram,
        'price_per_ounce': price_per_gram * 28.349   
    }

driver.get('https://www.instacart.com/store/aldi/search/bananas')

address_input = try_find_clickable_element(By.ID, 'address_input1')
address_input.click()

use_location_button = try_find_clickable_element(By.CSS_SELECTOR, 'button[data-testid="address-results-use-current-location"]')
use_location_button.click()

sleep(2)
retailer_cards = try_find_elements_with_fallbacks(By.CSS_SELECTOR, 'button[class*="RetailerCard"]', 'span[class*="StoreCompactCard"]')
aldi_card = next(filter(lambda rc: 'ALDI' in rc.text, retailer_cards), None)

aldi_card.click()

search_input = try_find_visible_element(By.CSS_SELECTOR, 'input[aria-label="search"]')
search_input.send_keys('bananas', Keys.ENTER)

item_cards = try_find_visible_elements(By.CSS_SELECTOR, 'div[class*="ItemBCard"]')

raw_results = list(map(lambda fc: get_item_values(fc, 'bananas'), filter(lambda ic: 'bananas' in ic.text.lower(), item_cards)))

print(raw_results)