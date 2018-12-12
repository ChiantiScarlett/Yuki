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
        self.df = pd.DataFrame()  # empty dataframe
        logging.debug('<Stock> initialized :: {}({})'.
                      format(self.name, self.code))

    def load(self, start=None, end=None, top=10):
        """
        This method loads data, based on the following parameters:
        -----------------------------------------------------------------------
        Argument | Type  | Description
        -----------------------------------------------------------------------
        start    | <str> | 'YYYY-MM-DD' : Starting date ('Optional')
        end      | <str> | 'YYYY-MM-DD' : End date
        top      | <int> | Number of items
        """
        # Validate Option
        if type(top) != int:
            raise YukiError('InvalidArgType',
                            arg=top,
                            arg_type=str(type(int)))

        # if start == None, raise error
        if not start:
            raise YukiError('InvalidDate', date=start)

        # if end is None, define end as of today
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")

        if start:
            try:
                start = datetime.strptime(start, '%Y-%m-%d')
            except Exception:
                raise YukiError('InvalidDate', date=start)
        if end:
            try:
                end = datetime.strptime(end, '%Y-%m-%d')
            except Exception:
                raise YukiError('InvalidDate', date=end)

        # Load data
        self.df = parse_hist_data(self.code, start, end)

    def __str__(self):
        return ("""
            <{name}> ({code}, {market})
            """.strip().format(name=self.name,
                               code=self.code,
                               market=self.market))

    def plot(self, index=['High', 'End', 'Start', 'Low'],
             start=None, end=None):
        plot_stock(self.name, self.df, index, start, end)
