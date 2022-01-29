class Item:
    def __init__(self, name, price_total, weight_grams):
        self.name = name
        self.weight_g = round(weight_grams, 1)
        self.weight_oz = round(weight_grams / 28.349, 1)
        self.price_total = price_total
        self.price_per_100g = round((price_total / weight_grams) * 100, 2)
        self.price_per_oz = round((price_total / weight_grams) * 28.349, 2)