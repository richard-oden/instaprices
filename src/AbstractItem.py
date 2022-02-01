from abc import ABC

class AbstractItem(ABC):
    def __init__(self, name, price_total):
        super().__init__()
        self.name = name,
        self.price_total = price_total