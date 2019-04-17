from bs4 import BeautifulSoup as Soup
from urllib.request import urlopen
from core import _parse_data as parse_data
from datetime import datetime, timedelta
import json


def summary(code):
    URL = 'https://api.finance.naver.com/' + \
        'service/itemSummary.nhn?itemcode={}'.format(code)
    return parse_data(URL, isJSON=True)


def realtime(code):
    URL = 'https://polling.finance.naver.com/' + \
        'api/realtime.nhn?query=SERVICE_ITEM:{}'.format(code)
    return parse_data(URL, isJSON=True)
