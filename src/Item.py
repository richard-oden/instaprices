class Item:
    def __init__(self, name, price_total, weight_grams):
        self.name = name
        self.weight_g = weight_grams
        self.weight_oz = weight_grams / 28.349
        self.price_total = price_total
        self.price_per_100g = (price_total / weight_grams) * 100
        self.price_per_oz = (price_total / weight_grams) * 28.349