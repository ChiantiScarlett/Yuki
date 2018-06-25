import pandas as pd

from yuki.error import YukiError
from yuki.parse import *
from yuki.fabricate import plot_stock
import logging


class Stock:
    def __init__(self, keyword=None):
        # Raise Error if keyword is none
        if not keyword:
            raise YukiError('NotEnoughArgument', arg='keyword', type='<str>')

        # Validate code
        self.name, self.code, self.market = parse_stock_meta(keyword)
        self.stat = parse_stock_stat(self.code)
        self.hist = pd.DataFrame()  # empty dataframe
        logging.debug('<Stock> initialized :: {}({})'.
                      format(self.name, self.code))

    def load_hist(self, start_date=None, end_date=None, top=10):
        # Validate Option
        if type(top) != int:
            raise YukiError('InvalidArgType',
                            arg=top,
                            arg_type=str(type(int)))

        # if start_date == None, raise error
        if not start_date:
            raise YukiError('InvalidDate', date=start_date)

        # if end_date is None, define end_date as of today
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except Exception:
                raise YukiError('InvalidDate', date=start_date)
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except Exception:
                raise YukiError('InvalidDate', date=end_date)

        # Load data
        self.hist = parse_hist_data(self.code, start_date, end_date)

    def __str__(self):
        return ("""
            <{name}> ({code}, {market})
            """.strip().format(name=self.name,
                               code=self.code,
                               market=self.market))

    def hist_to_xlsx(self, path):
        print('to_xlsx -> {}'.format(path))

    def hist_to_csv(self, path):
        print('to_csv -> {}'.format(path))

    def __add__(self, other):
        return Stocks(self, other)

    def plot(self, index=['High', 'End', 'Start', 'Low'],
             start=None, end=None):
        plot_stock(self.name, self.hist, index, start, end)


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
