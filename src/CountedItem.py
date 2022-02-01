from AbstractItem import AbstractItem

class CountedItem(AbstractItem):
    def __init__(self, name, price_total, count):
        super().__init__(name, price_total)
        self.count = count
        self.price_per_count = round(price_total / count, 2)