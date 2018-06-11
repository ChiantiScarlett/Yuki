from urllib.request import urlopen, URLError
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import numpy as np
import logging


class Stock:
    """ Class for parsing basic stock data.

    This class parses finance data from finance.naver.com, based on the code
    of a stock. Since this module highly relies on parsing web languages,
    be aware of its fragility regarding any structual updates on the web page.


    """

    def __init__(self, code):
        """

        Args:
            code (str): A code that represents the stock item.

        """

        self.code = code          # (str):   Code of the company
        self.name = None          # (str):   Name of the company
        self.market = None        # (str):   Which market it belongs to
        self.rank = None          # (int):   Rank within the market
        self.PER = None           # (float): PER of the company (WISEfn)
        self.foreign_rate = None  # (float): Foreign consumption rate of stock

        self.timestamp = None     # (str):   When the data was parsed
        self.price = None         # (int):   Current / End price of the day
        self.open = None          # (int):   Open price of the day
        self.high = None          # (int):   Highest price of the day
        self.low = None           # (int):   Lowest price of the day
        self.volume = None        # (int):   Trade volume of the day

        self.get_stock(code=self.code)

    def __str__(self):
        """ Custom defined member for printing out general data of the stock.

        This is typically defined for printing out current class data in an
        interactive Python shell or iPython.

        """

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
        """ Parse stock data from finance.naver.com

        This method is executed on class initialization. It updates the
        following attributes:

        self.name         (str):   Name of the company
        self.market       (str):   Which market it belongs to (KOSPI / KOSDAQ)
        self.rank         (int):   Rank within the market (KOSPI / KOSDAQ)
        self.PER          (float): PER of the company (WISEfn)
        self.foreign_rate (float): Foreign consumption rate of stock

        self.timestamp    (str):   Timestamp of time the data was parsed
        self.price        (int):   Current price / End price of the day
        self.open         (int):   Open price of the day
        self.high         (int):   Highest price of the day
        self.low          (int):   Lowest price of the day
        self.volume       (int):   Trade volume of the day


        Args:
            code          (str):   A code that represents the stock item.

        """

        # Prepare parsed html form from `finance.naver.com`
        url = "http://finance.naver.com/item/sise.nhn?code={}"
        html = urlopen(url.format(code)).read().decode('euc-kr')
        html = BeautifulSoup(html, 'html.parser')

        # Trim down to the core source of data
        src = html.find('div', {'class': 'first'}).find_all('tr')[1]
        src = src.find('td').text
        try:
            # Find market, rank, and timestamp
            self.market = {'코스피': 'KOSPI', '코스닥': 'KOSDAQ'}[src.split()[0]]
            self.rank = int(src.split()[1][:-1])
            src = html.find('em', {'class': 'date'}).text.strip().split()
            self.timestamp = " ".join(src[:2])

            # Find open, high, volume, low, name, and current price
            src = html.find('table').find_all('span', {'class': 'blind'})
            self.open = int(src[4].text.strip().replace(',', ''))
            self.high = int(src[1].text.strip().replace(',', ''))
            self.volume = int(src[3].text.strip().replace(',', ''))
            self.low = int(src[5].text.strip().replace(',', ''))
            src = html.find('div', {'class': 'rate_info'})
            self.name = src.find('dt').text.strip().replace(';', '')
            src = src.find('span', {'class': 'blind'}).text
            self.price = int(src.strip().replace(',', ''))

            # parse PER (WISEfn) and foreign consumption rate
            src = html.find('table', {'class': 'per_table'})
            self.PER = src.find_all('tbody')[0].find('td').find('em').text
            self.PER = float(self.PER.replace(',', ''))
            src = html.find('table', {'class': 'lwidth'})
            self.foreign_rate = src.find_all('td')[2].text
            message = "Successfully parsed the data of {} ({})."
            logging.debug(message.format(self.name, self.code))

        except Exception:
            # In case if the stock data is corrupted, stop parsing and escape
            message = "The stock data of [{}] seems to be incomplete."
            logging.critical(message.format(code))

    def history(self, start_date, end_date):
        """ Parse stock historical data from finance.naver.com

        This method parses historical data based on a range of date.


        Args:
            start_date  (str):      YYYYDDMM | The first day of the output
            end_date    (str):      YYYYDDMM | The last day of the output


        Returns:
            pandas.DataFrame object with the following columns:

            Date        (object):   Date of each history data
            Open        (int64):    Open price of the day
            High        (int64):    Highest price of the day
            Low         (int64):    Lowest price of the day
            End         (int64):    End price of the day
            HL_Gap      (float64):  (High - Low) / Open
            Change      (float64):  (End - Open) / Open
            Volume      (int64):    Trade volume of the day
        """

        # Validate start_date, end_date, and convert into comparable format
        try:
            dates = [start_date, end_date]
            for index in range(len(dates)):
                dates[index] = datetime.strptime(str(dates[index]), "%Y%m%d")
                dates[index] = dates[index].strftime('%Y.%m.%d')
        except IndexError:
            msg = "start_date, end_date parameters must be YYYYMMDD format."
            raise TypeError(msg)
        start_date, end_date = dates

        # Create history_list, which will include histories within iterations
        history_list = []

        # If today is included in the date range and market has been opened,
        # manually append today's stock data
        today = datetime.now().strftime("%Y.%m.%d")
        if today <= end_date and self.open is not None:
            data = {}
            data['Date'] = today
            data['End'] = self.price
            data['Open'] = self.open
            data['High'] = self.high
            data['Low'] = self.low
            data['Volume'] = self.volume
            data['HL_Gap'] = \
                100 * (self.high - self.low) / self.open if self.open else 0
            data['Change'] = \
                100 * (self.price - self.open) / self.open if self.open else 0
            history_list.append(data)

        # Prepare html form parser.
        url = "http://finance.naver.com/item/sise_day.nhn?code={}&page={}"
        page = 1
        break_flag = False
        while not break_flag:
            try:
                html = urlopen(url.format(self.code, page)).read()
                html = BeautifulSoup(html.decode('euc-kr'), 'html.parser')
            except URLError:
                # If page no longer exists, break the while loop
                break_flag = True
                break

            # Trim down to specific data chunk
            for row in html.find_all('tr')[3:]:
                src = row.find_all('span')
                # Skip unnecessary span(horizon border, etc)
                if len(src) == 0:
                    continue
                # Skip data until it goes below the end_date
                if src[0].text.strip() > end_date:
                    continue
                # If the date goes below the start_date, break the while loop
                if src[0].text.strip() < start_date:
                    break_flag = True
                    break

                # Else, parse and add data
                data = {}
                data['Date'] = src[0].text.strip().replace('.', '-')
                data['End'] = int(src[1].text.strip().replace(',', ''))
                data['Open'] = int(src[3].text.strip().replace(',', ''))
                data['High'] = int(src[4].text.strip().replace(',', ''))
                data['Low'] = int(src[5].text.strip().replace(',', ''))
                data['Volume'] = int(src[6].text.strip().replace(',', ''))
                data['Change'] = \
                    100 * (data['End'] - data['Open']) / data['Open'] \
                    if data['Open'] else 0
                data['HL_Gap'] = \
                    100 * (data['High'] - data['Low']) / data['Open'] \
                    if data['Open'] else 0

                history_list.append(data)

            page += 1

        message = 'Parsing stock history of {} ({}) :: {} item(s) added.'
        logging.debug(message.format(self.name, self.code, len(history_list)))

        # Return data
        return pd.DataFrame(history_list, columns=['Date',
                                                   'Open',
                                                   'High',
                                                   'Low',
                                                   'End',
                                                   'HL_Gap',
                                                   'Change',
                                                   'Volume'])


def capture(market, top=None):
    """ Returns a snapshot of current KOSPI / KOSDAQ market data.

        This function parses current market data, based on its arguments.

        Note:
            This function will return empty data during 08:00 KST ~ 09:00 KST.


        Args:
            market      (str):      The market you want to get the data from.
                                    'KOSPI' and 'KOSDAQ' (case insensitive)
                                    are the only possible options.
            top         (int):      Number of items you want to get from the
                                    top. By default, this function will get all
                                    data.


        Returns:
            pandas.DataFrame object with the following columns:

            Rank        (int64):    Rank within KOSPI / KOSDAQ market
            Code        (object):   Code of the stock
            Name        (object):   Name of the company
            Price       (int64):    Current / End price of the day
            Change      (float64):  Price difference from the prev data
            Market Cap  (int64):    Market Cap of the stock
            Volume      (int64):    Trade volume of the day
            PER         (float64):  PER of the stock
            ROE         (float64):  ROE of the stock

    """

    # Raise error if market is not KOSPI nor KOSDAQ
    market_keys = {'KOSPI': '0', 'KOSDAQ': '1'}
    if market.upper() not in market_keys:
        raise ValueError("Market should be either 'KOSPI' or 'KOSDAQ'.")

    # Validate arguments
    if top is not None and type(top) != int:
        raise TypeError("'top' should be an <int> type number.")
    if top is None:
        top = -1  # So as to parse all stock data
    elif top < 1:
        raise ValueError("'top' should be greater than 0.")

    # Start parsing
    url = "http://finance.naver.com/sise/sise_market_sum.nhn?sosok="
    url += market_keys[market.upper()]
    page = 1
    data = []  # A variable that holds every stock data chunks
    break_flag = False  # Flag used for escaping loop

    while not break_flag:
        html = urlopen(url + '&page={}'.format(page))
        html = BeautifulSoup(html.read().decode('euc-kr'), 'html.parser')
        html = html.find('tbody')

        # When meets the last page of stock list, escape while-loop
        if len(html) == 3:
            break_flag = True
            break

        # Else parse data from each line, and save them into 'data'.
        for src in html.find_all('tr'):
            # Skip border rows
            if len(src) == 1:
                continue

            # Parse data
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

            # Store data. If sufficient, escape the loop
            data.append(item)
            top -= 1
            if not top:
                break_flag = True
                break
        page += 1

    # Return pd.DataFrame object
    return pd.DataFrame(data, columns=['Rank',
                                       'Code',
                                       'Name',
                                       'Price',
                                       'Change',
                                       'Market Cap',
                                       'Volume',
                                       'PER',
                                       'ROE'])


class Group:
    """ Class for grouping and handling multiple Stock data

    This class is designed to group and handle multiple stock data at once. It
    provides various methods which can parse or view data altogether.

    """

    def __init__(self, *args):
        """
            Note:
                This class is designed to accept multi-type arguments as its
                parameters. You can use <str>, <numpy.ndarray>, or <list> in
                order to input stock codes. You can also use multiple types
                of data at once.


            Args:
                code (str):           A code that represents the stock item
                code (numpy.ndarray): A list that contains stock codes
                code (list):          A list that contains stock codes


        """
        self.stocks = []
        self.histories = []

        # Validate multi-type arguments
        input_codes = []
        for arg in args:
            if type(arg) == str:
                input_codes.append(arg)
            elif type(arg) == list:
                for item in arg:
                    if type(item) != str:
                        raise TypeError("Invalid datatype.")
                input_codes += arg
            elif type(arg) == np.ndarray:
                input_codes += arg.tolist()

        # Get stock data for each stock and create empty DataFrame
        self.stocks = [Stock(code) for code in input_codes]
        empty_df = pd.DataFrame([], columns=[
            'Rank', 'Code', 'Name', 'Price', 'Change', 'Market Cap',
            'Volume', 'PER', 'ROE'])
        self.histories = [empty_df] * len(input_codes)

        # Write debug-level log
        msg = 'Successfully initialized new <Group> with {} item(s) ({})'
        logging.debug(msg.format(len(self.stocks), input_codes))

    def __add__(self, other):
        """ Concatenate two <Group> class objects

            This class allows addition operators between two different
            <Group> objects.

        """

        # Add data
        other.stocks = self.stocks + other.stocks
        other.histories = self.histories + other.histories

        # Write debug-level log
        msg = 'Successfully merged two <Group> objects with {} item(s) ({})'
        codes = [stock.code for stock in other.stocks]
        logging.debug(msg.format(len(other.stocks), codes))
        return other

    def update_history(self, start_date, end_date):
        """ Get historical data for every stock in this group

        This method parses historical data of every stock stored in this group
        based on a range of date.

        Args:
            start_date  (str):      YYYYDDMM | The first day of the output
            end_date    (str):      YYYYDDMM | The last day of the output

        """

        for stock in self.stocks:
            index = self.stocks.index(stock)
            self.histories[index] = stock.history(start_date, end_date)

    def snapshot(self, date):
        """ Return snapshot of specific date

            Args:
                date    (str):      YYYYDDMM | The day you want to look at

            Returns:
                pandas.DataFrame object with the following columns:

            Date        (object):   Date of each history data
            Name        (object):   Name of a company
            Code        (object):   Code of a company
            Open        (int64):    Open price of the day
            High        (int64):    Highest price of the day
            Low         (int64):    Lowest price of the day
            End         (int64):    End price of the day
            HL_Gap      (float64):  (High - Low) / Open
            Change      (float64):  (End - Open) / Open
            Volume      (int64):    Trade volume of the day

        """

        # Change date format into YYYY-MM-DD
        try:
            date = datetime.strptime(str(date), "%Y%m%d")
            date = date.strftime('%Y-%m-%d')
        except Exception:
            raise TypeError('`date` argument must be YYYYDDMM <str>.')

        # Search rows which have the same date
        df = []
        for idx in range(len(self.histories)):
            history = self.histories[idx]
            history = history[history['Date'] == date]
            history.insert(1, 'Name', self.stocks[idx].name)
            history.insert(2, 'Code', self.stocks[idx].code)
            df.append(history)

        # Return Concatenated DataFrame
        return pd.concat(df)
