class MenuOption:
    def __init__(self, desc, fn):
        self.desc = desc
        self.fn = fn

    def execute(self):
        return self.fn()
    