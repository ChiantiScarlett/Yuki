from urllib.request import urlopen, URLError
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from tabulate import tabulate

pd.set_option('display.expand_frame_repr', False)


class Error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[*] {}".format(self.message)


class _Stock:
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

    def __init__(self, code):
        self.name = None
        self.code = code
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

        self.get_stock(code=self.code)

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

    def get_stock(self, code):
        url = \
            "http://finance.naver.com/item/sise.nhn?" +\
            "code={}".format(code)
        html = BeautifulSoup(
            urlopen(url).read().decode('euc-kr'), 'html.parser')

        # parse market and rank
        src = html.find('div', {'class': 'first'}).find_all('tr')[1]
        src = src.find('td').text
        m_name = {'코스피': 'KOSPI', '코스닥': 'KOSDAQ'}
        self.market = m_name[src.split()[0]]
        self.rank = int(src.split()[1][:-1])
        # parse timestamp
        src = html.find('em', {'class': 'date'}).text.strip().split()
        self.timestamp = " ".join(src[:2])
        # parse open, high, volume, low, price, name
        src = html.find('table').find_all('span', {'class': 'blind'})
        self.open = int(src[4].text.strip().replace(',', ''))
        self.high = int(src[1].text.strip().replace(',', ''))
        self.volume = int(src[3].text.strip().replace(',', ''))
        self.low = int(src[5].text.strip().replace(',', ''))
        src = html.find('div', {'class': 'rate_info'})
        self.name = src.find('dt').text.strip().replace(';', '')
        src = src.find('span', {'class': 'blind'}).text
        self.price = int(src.strip().replace(',', ''))
        # parse PER (WISEfn)
        src = html.find('table', {'class': 'per_table'})
        self.PER = float(src.find_all('tbody')[0].find('td').find('em').text)
        # parse Foreign Consumption Rate
        src = html.find('table', {'class': 'lwidth'}).find_all('td')[2].text
        self.foreign_rate = src

    def _history(self, *args):
        """
        get history of the stock.

        """

        # if arg == int, parse history by the amount of arg
        if len(args) == 1 and type(args[0]) == int:
            COUNTER = args[0]
        # else if arg == tuple, parse date from it
        elif len(args) == 2:
            # convert start_date, end_date into comparable string
            try:
                START_DATE, END_DATE = map(
                    lambda x: datetime.strptime(
                        str(x), '%Y%m%d').strftime('%Y.%m.%d'), args)
            except IndexError:
                raise Error("tuple arg must be (YYYYMMDD,YYYYMMDD) format.")
        else:
            raise Error("arg must be either int() or tuple().")

        # parse start.
        # start_parsing
        url = \
            "http://finance.naver.com/item/sise_day.nhn?" +\
            "code={code}&page={page}"
        history_list = []
        page = 1
        while True:
            try:
                html = urlopen(url.format(code=self.code, page=page))
                html = BeautifulSoup(
                    html.read().decode('euc-kr'), 'html.parser')
            # if data page is out of range, stop and return stock class
            except URLError:
                return history_list
            # parse each row
            for row in html.find_all('tr')[3:]:
                src = row.find_all('span')
                # if invalid span(including horizon border, etc), skip.
                if len(src) == 0:
                    continue

                if len(args) == 2:
                    # if date is out of range, skip.
                    if src[0].text.strip() > END_DATE:
                        continue
                    # if date is out of range, stop and return stock
                    if src[0].text.strip() < START_DATE:
                        return history_list
                elif len(args) == 1:
                    if COUNTER <= 0:
                        return history_list
                    else:
                        COUNTER -= 1

                # else parse data
                data = {}
                data['Date'] = src[0].text.strip()
                data['End'] = int(src[1].text.strip().replace(',', ''))
                data['Start'] = int(src[3].text.strip().replace(',', ''))
                data['High'] = int(src[4].text.strip().replace(',', ''))
                data['Low'] = int(src[5].text.strip().replace(',', ''))
                data['Volume'] = int(src[6].text.strip().replace(',', ''))
                data['HL_Gap'] = (data['High'] - data['Low']) / data['Start']
                data['HL_Gap'] = 100 * data['HL_Gap']
                data['SE_Gap'] = (data['Start'] - data['End']) / data['Start']
                data['SE_Gap'] = 100 * data['SE_Gap']
                # append to the 'stock' class
                history_list.append(data)
            page += 1

    def history(self, *args):
        return DataObject(pd.DataFrame(self._history(*args),
                                       columns=['Date',
                                                'Start',
                                                'High',
                                                'Low',
                                                'End',
                                                'HL_Gap',
                                                'SE_Gap',
                                                'Volume']))

    def compare(self, *args):
        # args = (DATE1, DATE2)
        # DATE1 must be prior to DATE2
        history_list = self.history(*args)
        print(history_list[0])
        print(history_list[-1])


class DataObject:
    def __init__(self, df):
        self.df = df

    def show(self, **kwargs):
        # print item
        # check parameter
        df = None
        try:
            # if no option, show pure dataframe
            if len(kwargs.keys()) == 0:
                df = self.df
            # if multiple options are set, raise Error
            elif len(kwargs.keys()) > 1:
                raise Error("Only one paramter is allowed in this method.")
            # top
            elif 'top' in kwargs.keys():
                df = self.df[:kwargs['top']]
            # bottom
            elif 'bottom' in kwargs.keys():
                df = self.df[-kwargs['bottom']:]
            # date
            elif 'date' in kwargs.keys():
                try:
                    START_DATE, END_DATE = map(
                        lambda x: datetime.strptime(
                            str(x), '%Y%m%d').strftime('%Y.%m.%d'),
                        kwargs['date'])
                except IndexError:
                    raise Error(
                        "tuple arg must be (YYYYMMDD,YYYYMMDD) format.")

                df = self.df[START_DATE < self.df['Date']]
                df = df[df['Date'] < END_DATE]
            else:
                raise Error("Invalid key '{}'".format(kwargs[0]))
        except IndexError:
            raise Error("Invalid parameter.")

        print(tabulate(df, headers='keys'))

    def sort(self, key, ascending=False):
        self.df = self.df.sort_values(by=key, ascending=ascending)

    def ndarray(self, key):
        return self.df[key].values


class _Market:

    def __init__(self):
        pass

    def KOSPI(self, top=None):
        return self._read_KOSPI_KOSDAQ(index=1, top=top)

    def KOSDAQ(self, top=None):
        return self._read_KOSPI_KOSDAQ(index=0, top=top)

    def _read_KOSPI_KOSDAQ(self, index, top):
        url = \
            "http://finance.naver.com/sise/sise_market_sum.nhn?" +\
            "sosok={}&page={}"
        data = []
        page = 1
        counter = 0
        if top is None:
            top = 999999
        while True:
            html = urlopen(url.format(index, page))
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
                item['Code'] = str(src.find('a')['href'].split('=')[1])
                nums = src.find_all('td', {'class': 'number'})
                item['Price'] = int(nums[0].text.strip().replace(',', ''))
                item['Change'] = float(nums[2].text.strip()[:-1])
                item['Volume'] = int(nums[4].text.strip().replace(',', ''))
                item['Market Cap'] = int(nums[4].text.strip().replace(',', ''))
                per = nums[8].text.strip().replace(',', '')
                item['PER'] = float(per) if per != 'N/A' else None
                roe = nums[9].text.strip().replace(',', '')
                item['ROE'] = float(roe) if roe != 'N/A' else None

                data.append(item)
                counter += 1
                # break if counter meets top
                if counter == top:
                    df = pd.DataFrame(data, columns=['Rank',
                                                     'Code',
                                                     'Name',
                                                     'Price',
                                                     'Change',
                                                     'Market Cap',
                                                     'Volume',
                                                     'PER',
                                                     'ROE'])
                    return DataObject(df)

            print('[*] page {} complete.'.format(page))
            page += 1

        df = pd.DataFrame(data, columns=['Rank',
                                         'Code',
                                         'Name',
                                         'Price',
                                         'Change',
                                         'Market Cap',
                                         'Volume',
                                         'PER',
                                         'ROE'])

        return DataObject(df)

        # df.to_csv('KOSPI_{}.csv'.format(
        #     datetime.now().strftime("%y-%m-%d-%H-%M")), index=False)
