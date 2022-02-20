from statistics import mean
from statistics import median
import inspect
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import models.AnalysisOptions as AnalysisOptions
from models.CountedItem import CountedItem
from models.WeighedItem import WeighedItem

def none_or_empty(sized):
    return sized is None or len(sized) == 0

def get_all_items(stores, item_name):
    '''
    Returns a list of items from all stores that match an item name.
    '''
    all_items = []
    for store in stores:
        store_items = store.items.get(item_name)
        if none_or_empty(store_items):
            continue
        all_items.extend(store_items)
    return all_items

def get_predominant_item_type(stores, item_name):
    '''
    Returns the predominant type for items from all stores that match an item name.
    '''
    all_items = get_all_items(stores, item_name)
    percent_weighed = sum(isinstance(i, WeighedItem) for i in all_items) / len(all_items)
    return WeighedItem if percent_weighed >= 0.5 else CountedItem

def prep_items(stores, shopping_list):
    '''
    Filters out items that are not of the predominant type to facilitate easier comparison.
    '''
    for item_name in shopping_list:
        item_type = get_predominant_item_type(stores, item_name)
        for store in stores:
            store_items = store.items.get(item_name)
            if none_or_empty(store_items):
                continue
            store.items[item_name] = [i for i in store_items if isinstance(i, item_type)]


def get_data(analysis_options, stores, shopping_list):
    labels = []
    bars = []

    for store in stores:
        if (analysis_options.omit_incomplete_stores and 
            any(none_or_empty(items) for items in iter(store.items.values()))):
            continue

        labels.append(store.name)
        bar = []
        for list_item in shopping_list:
            items = store.items.get(list_item)
            if none_or_empty(items):
                bar.append(0)
                continue

            pass
    pass