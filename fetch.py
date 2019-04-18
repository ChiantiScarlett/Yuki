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


def weekly(code):
    """
    Dirty Parsing
    """

    URL = 'https://finance.naver.com/item/sise_time.nhn?' + \
        'code={code}'.format(code=code)
    date_cursor = datetime.today()
    data = []

    for day in range(1):
        URL += '&thistime={}'.format(
            (date_cursor - timedelta(days=day)).strftime('%Y%m%d1600000'))
        URL += '&page={page}'

        page = 1
        prev_html = None

        while True:
            html = Soup(urlopen(URL.format(page=page)).read().decode('euc-kr'),
                        'html.parser')

            if (html == prev_html):
                break
            else:
                prev_html = html

            for row in html.find_all('tr')[1:]:
                if len(row.find_all('td')) == 7:
                    td = row.find_all('td')
                    time = list(map(int, td[0].text.split(":")))
                    date = date_cursor - timedelta(days=day)
                    date = datetime(date.year, date.month,
                                    date.day, time[0], time[1])

                    target = int(td[1].text.replace(',', ''))
                    ask = int(td[3].text.replace(',', ''))
                    bid = int(td[4].text.replace(',', ''))
                    volume = int(td[5].text.replace(',', ''))
                    data.append(
                        {'체결시각': date,
                         '체결가': target,
                         '매도': ask,
                         '매수': bid,
                         '거래량': volume
                         }
                    )
            print('page: ', page)
            page += 1

    return data
