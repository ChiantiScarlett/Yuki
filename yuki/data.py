import pandas as pd
from urllib.request import urlopen
# from bs4 import BeautifulSoup as Soup
import json
base_url = 'https://finance.naver.com'


class DataObject:
    name = None
    code = None
    market = None

    def __str__(self):
        return ("""
            <{name}> ({code}, {market})
            """.strip().format(name=self.name,
                               code=self.code,
                               market=self.market))

    def get(self, number):
        """
        Set URL.
        """
        self._parse_data(number)

    def _parse_data(self, page):
        pass


class KOREAN_MARKET(DataObject):
    def __init__(self, MARKET):
        self.name = MARKET
        self.code = MARKET
        self.market = MARKET
        self.df = pd.DataFrame()

    def _parse_data(self, size, page):
        # REFERENCE
        # https://m.stock.naver.com/api/item/getPriceDayList.nhn?code=028260&pageSize=2000&page=1
        # https://m.stock.naver.com/api/json/world/worldIndexDay.nhn?symbol=NAS@IXIC&pageSize=400&page=1
        pass


KOSPI = KOREAN_MARKET('KOSPI')
KOSDAQ = KOREAN_MARKET('KOSDAQ')
