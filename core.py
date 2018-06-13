import pandas as pd
from yuki.error import YukiError
from yuki.parse import *


class Stock:
    def __init__(self, code):
        # Validate code
        self.name = parse_name(code)
        self.stat = parse_current_stat(code)
        self.code = code
        self.hist = pd.DataFrame()  # empty dataframe

    def hist_to_xlsx(self, path):
        print('to_xlsx -> {}'.format(path))

    def hist_to_csv(self, path):
        print('to_csv -> {}'.format(path))

    def __add__(self, other):
        return Stocks(self, other)


class Stocks:
    def __init__(self, *args):
        self.names = []
        self.codes = []
        self.items = []

        self.add_stock(args)

    def add_stock(self, args):
        for item in args:
            # Raise error if not valid
            if type(item) != Stock:
                raise YukiError('InvalidStock', arg=item)

            # Add item
            self.names.append(item.name)
            self.codes.append(item.code)
            self.items.append(item)

    def append(self):
        pass

    def pop(self):
        pass

    def index(self):
        pass
