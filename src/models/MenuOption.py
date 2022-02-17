class MenuOption:
    def __init__(self, desc, fn, validator_fn = None):
        self.desc = desc
        self.fn = fn
        self.validator_fn = validator_fn
    