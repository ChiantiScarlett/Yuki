from urllib.request import urlopen, URLError
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


class Error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Stock:
    """
    name : name of the corporation
    code : stock code of the corporation
    timestamp : Parsed date/time
    price : current price
    open : open price
    high : highest price
    low : lowest price
    volume : trade volume
    market : market area (KOSPI or KOSDAQ)
    rank : rank of the stock in the market
    PER : PER (WISEfn)
    foreign_rate : Foreign Consumption Rate
    """

    def __init__(self):
        self.name = None
        self.code = None
        self.price = None
        self.timestamp = None
        self.open = None
        self.high = None
        self.low = None
        self.volume = None
        self.market = None
        self.rank = None
        self.PER = None
        self.foreign_rate = None
        self.history = []

    def __str__(self):

        return_str = "[{name}] ({market}, {code})\n" +\
                     "<{timestamp}>\n" +\
                     "Price:        {price:,}\n" +\
                     "High:         {high:,}\n" +\
                     "Low:          {low:,}\n" +\
                     "Open:         {open:,}\n" +\
                     "Trade Volume: {volume:,}"

        return return_str.format(name=self.name, market=self.market,
                                 timestamp=self.timestamp, price=self.price,
                                 high=self.high, low=self.low, code=self.code,
                                 open=self.open, volume=self.volume)


def get_stock(stock_code, history=None):
    url = "http://finance.naver.com/item/sise.nhn?code={}".format(stock_code)
    html = BeautifulSoup(urlopen(url).read().decode('euc-kr'), 'html.parser')

    stock = Stock()
    # parse stock code
    src = html.find('span', {'class': 'code'})
    stock.code = src.text
    # parse market and rank
    src = html.find('div', {'class': 'first'}).find_all('tr')[1]
    src = src.find('td').text
    m_name = {'코스피': 'KOSPI', '코스닥': 'KOSDAQ'}
    stock.market = m_name[src.split()[0]]
    stock.rank = int(src.split()[1][:-1])
    # parse timestamp
    src = html.find('em', {'class': 'date'}).text.strip().split()
    stock.timestamp = " ".join(src[:2])
    # parse open, high, volume, low, price, name
    src = html.find('table').find_all('span', {'class': 'blind'})
    stock.open = int(src[4].text.strip().replace(',', ''))
    stock.high = int(src[1].text.strip().replace(',', ''))
    stock.volume = int(src[3].text.strip().replace(',', ''))
    stock.low = int(src[5].text.strip().replace(',', ''))
    src = html.find('div', {'class': 'rate_info'})
    stock.name = src.find('dt').text.strip().replace(';', '')
    src = src.find('span', {'class': 'blind'}).text
    stock.price = int(src.strip().replace(',', ''))
    # parse PER (WISEfn)
    src = html.find('table', {'class': 'per_table'})
    stock.PER = float(src.find_all('tbody')[0].find('td').find('em').text)
    # parse Foreign Consumption Rate
    src = html.find('table', {'class': 'lwidth'}).find_all('td')[2].text
    stock.foreign_rate = src

    # if History is not set return data
    if history is None:
        return stock
    # else if History is tuple, parse date
    if type(history) == tuple:
        # convert start_date, end_date into comparable string
        START_DATE, END_DATE = map(
            lambda x: datetime.strptime(str(x), '%Y%m%d').strftime('%Y.%m.%d'),
            history)

    if type(history) == int:
        COUNTER = history

    # start_parsing
    url = "http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}"
    for page in range(1, 100000):
        try:
            html = urlopen(url.format(code=stock_code, page=page))
            html = BeautifulSoup(html.read().decode('euc-kr'), 'html.parser')
        # if data page is out of range, stop and return stock class
        except URLError:
            return stock
        # parse each row
        for row in html.find_all('tr')[3:]:
            src = row.find_all('span')
            # if invalid span(including horizon border, etc), skip.
            if len(src) == 0:
                continue

            if type(history) == tuple:
                # if date is out of range, skip.
                if src[0].text.strip() > END_DATE:
                    continue
                # if date is out of range, stop and return stock
                if src[0].text.strip() < START_DATE:
                    return stock
            elif type(history) == int:
                if COUNTER <= 0:
                    return stock
                else:
                    COUNTER -= 1

            # else parse data
            data = {}
            data['date'] = src[0].text.strip()
            data['end'] = int(src[1].text.strip().replace(',', ''))
            data['start'] = int(src[3].text.strip().replace(',', ''))
            data['high'] = int(src[4].text.strip().replace(',', ''))
            data['low'] = int(src[5].text.strip().replace(',', ''))
            data['volume'] = int(src[6].text.strip().replace(',', ''))
            # append to the 'stock' class
            stock.history.append(data)


def read_KOSPI():

    url = "http://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page={}"
    data = []
    for page in range(1, 1000):
        html = urlopen(url.format(page))
        html = BeautifulSoup(html.read().decode('euc-kr'), 'html.parser')
        html = html.find('tbody')
        if len(html) == 3:
            break

        for src in html.find_all('tr'):
            # ignore border rows
            if len(src) == 1:
                continue

            item = {}
            item['Rank'] = int(src.find('td', {'class': 'no'}).text)
            item['Name'] = str(src.find('a').text.strip().replace(';', ''))
            item['Code'] = src.find('a')['href'].split('=')[1].strip()
            nums = src.find_all('td', {'class': 'number'})
            item['Price'] = int(nums[0].text.strip().replace(',', ''))
            item['Change'] = nums[2].text.strip()
            item['Volume'] = int(nums[4].text.strip().replace(',', ''))
            item['Market Cap'] = int(nums[4].text.strip().replace(',', ''))
            per = nums[8].text.strip().replace(',', '')
            item['PER'] = float(per) if per != 'N/A' else None
            roe = nums[9].text.strip().replace(',', '')
            item['ROE'] = float(roe) if roe != 'N/A' else None

            data.append(item)
        print('[*] page {} complete.'.format(page))

    df = pd.DataFrame(data, columns=['Rank',
                                     'Name',
                                     # 'Code',
                                     'Price',
                                     'Change',
                                     'Market Cap',
                                     'Volume',
                                     'PER',
                                     'ROE'])

    return df

    # df.to_csv('KOSPI_{}.csv'.format(
    #     datetime.now().strftime("%y-%m-%d-%H-%M")), index=False)
