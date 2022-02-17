import enum

class AnalysisOptions():
    def __init__(self, price_type, price_aggregate, omit_incomplete_stores):
        self.price_type = price_type
        self.price_aggregate = price_aggregate
        self.omit_incomplete_stores = omit_incomplete_stores

class PriceType(enum.Enum):
    PER_100G = 0
    PER_OZ = 1
    TOTAL = 2

class PriceAggregate(enum.Enum):
    CHEAPEST = 0
    MEAN = 1
    MEDIAN = 2