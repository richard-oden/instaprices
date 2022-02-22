from statistics import mean
from statistics import median
import matplotlib.pyplot as plt
import pandas as pd
from models.AnalysisOptions import PriceType
from models.AnalysisOptions import PriceAggregate
from models.CountedItem import CountedItem
from models.WeighedItem import WeighedItem

PRICE_TYPES = {
    PriceType.PER_100G: lambda i: i.price_per_100g,
    PriceType.PER_OZ: lambda i: i.price_per_oz,
    PriceType.TOTAL: lambda i: i.price_total,
}

def none_or_empty(sized):
    '''
    Returns True if a sized container is None or contains no items. Otherwise returns False.
    '''
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
    percent_weighed = sum(type(i) is WeighedItem for i in all_items) / len(all_items)
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

def get_item_price(item, price_type):
    '''
    Returns the item price specified by price_type. If the item is a CountedItem and the price type is a unit price, returns the item's price per count.
    '''
    if (type(item) is CountedItem and
        (price_type == PriceType.PER_100G or price_type == PriceType.PER_OZ)):
        return item.price_per_count

    return {
        PriceType.PER_100G: lambda i: i.price_per_100g,
        PriceType.PER_OZ: lambda i: i.price_per_oz,
        PriceType.TOTAL: lambda i: i.price_total,
    }[price_type](item)

def get_aggregate_price(prices, price_aggregate):
    '''
    Returns the aggregate price specified by price_aggregate.
    '''
    return {
        PriceAggregate.CHEAPEST: lambda ps: min(ps),
        PriceAggregate.MEAN: lambda ps: mean(ps),
        PriceAggregate.MEDIAN: lambda ps: median(ps)
    }[price_aggregate](prices)

def get_store_prices(store, shopping_list, analysis_options):
    '''
    Returns a list of aggregate stores prices for each item name in the shopping list. 
    '''
    prices = []
    for item_name in shopping_list:
        store_items = store.items.get(item_name)
        if none_or_empty(store_items):
            prices.append(0)
            continue

        prices.append(get_aggregate_price(
            [get_item_price(i, analysis_options.price_type) for i in store_items], 
            analysis_options.price_aggregate))
    return prices

def get_data(stores, shopping_list, analysis_options):
    '''
    Returns data for creating a dataframe in pandas, formatted as a 2d list.
    '''
    data = []
    for store in stores:
        # if we are omitting incomplete stores, skip over stores where there are no items for an item name:
        if (analysis_options.omit_incomplete_stores and 
            any(none_or_empty(items) for items in iter(store.items.values()))):
            continue

        data.append([store.name, *get_store_prices(store, shopping_list, analysis_options)])

    # sort data by price, low to high
    data.sort(key=lambda d: sum([d[1], d[-1]]))

    return data

def render_chart(data, shopping_list):
    data_frame = pd.DataFrame(data, columns=['Store', *shopping_list])
    data_frame.plot.bar(x='Store', stacked=True, title='Instaprices Comparison')
    plt.show()

def build_chart(stores, shopping_list, analysis_options):
    prep_items(stores, shopping_list)
    data = get_data(stores, shopping_list, analysis_options)
    render_chart(data, shopping_list)