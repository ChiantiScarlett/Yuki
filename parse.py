from yuki.error import YukiError
from urllib.request import urlopen
import json
from bs4 import BeautifulSoup as Soup
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
import logging
from datetime import datetime

THREADPOOL_MAX = 10


def parse_current_stat(code):
    logging.debug('init :: code={}'.format(code))
    url_form = 'http://api.finance.naver.com/service/itemSummary.nhn?' + \
               'itemcode={code}'
    src = urlopen(url_form.format(code=code))
    src = json.loads(src.read().decode('utf-8'))

    logging.debug('return :: {} ').format(str(type(src)))
    return src  # Dict-type


def parse_name(code):
    logging.debug('init :: code={}'.format(code))

    url_form = 'http://finance.naver.com/item/main.nhn?code={code}'
    src = urlopen(url_form.format(code=code))
    src = Soup(src.read().decode('euc-kr'), 'html.parser')
    try:
        title = src.find('title').text.split(':')[0].strip()
    except Exception:
        raise YukiError('InvalidStockCode', code=code)

    logging.debug('return :: <{}> ').format(str(type(title)))
    return title


def parse_hist_data(code, start_date=None, end_date=None):
    logging.debug('init :: code={}, start_date={}, end_date={}'.
                  format(code, start_date, end_date))

    # Parse data from URL
    url_form = 'http://finance.naver.com/item/sise_day.nhn?' + \
               'code={code}&page={page}'

    # Initial parse: validate stock code and get last page number
    src = urlopen(url_form.format(code=code, page=1))
    src = Soup(src.read().decode('euc-kr'), 'html.parser')

    last_page = src.find('td', {'class': 'pgRR'})
    last_page = int(last_page.find('a')['href'].split('=')[-1])

    if not src.find('td', {'class': 'num'}).text.strip():
        raise YukiError('InvalidStockCode', code=code)

    # Calculate date difference and set limiter according to the value
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    tdelta = (datetime.now() - start_date).days

    limiter = int(tdelta * 7 / 5 / 10)  # number of threadpool per loop
    data = []  # data that holds total data
    pool = []  # thread pool
    start_cursor = 1  # page start
    end_cursor = limiter + 1  # page end

    while True:
        # Dynamically changes Thread Pool size, based on the limiter
        partial_data = []  # var that holds data every loop

        # Make sure while loop don't go over last_page
        if last_page < end_cursor - 1:
            end_cursor = last_page + 1

        # Start threading within pool
        with ThreadPoolExecutor(max_workers=limiter) as executor:
            for page in range(start_cursor, end_cursor):
                pool.append(executor.submit(
                    parse_hist_data_by_page, code, page))
        for item in as_completed(pool):
            partial_data += item.result()

        wait(pool)  # wait until current thread pool ends

        # Append `partial_data` to `data`
        partial_data.sort()
        last_date = datetime.strptime(partial_data[0][0], '%Y-%m-%d')
        data = partial_data + data

        # Check if the data meets end
        if last_date < start_date:
            break

        # If not, continue with updated indexes
        start_cursor += limiter
        end_cursor += limiter

    # Drop unnecessary data
    while start_date > datetime.strptime(data[0][0], '%Y-%m-%d'):
        data.pop(0)

    return data
    logging.debug('return :: {}, {} item(s) '.
                  format(str(type(data)), len(data)))


def parse_hist_data_by_page(code, page):
    # Sub-process that is ran from pool
    logging.debug('init :: code={}, page={}'.format(code, page))

    # Parse data from URL
    url_form = 'http://finance.naver.com/item/sise_day.nhn?' + \
               'code={code}&page={page}'

    # Initial parse: validate stock code and get last page number
    src = urlopen(url_form.format(code=code, page=page))
    src = Soup(src.read().decode('euc-kr'), 'html.parser')

    data = []
    for tr in src.find_all('tr'):
        if tr.has_attr('onmouseover'):  # skip header and border line
            td = tr.find_all('td')
            try:
                date = td[0].text.strip().replace('.', '-')
                end = int(td[1].text.strip().replace(',', ''))
                change = int(td[2].text.strip().replace(',', ''))
                start = int(td[3].text.strip().replace(',', ''))
                high = int(td[4].text.strip().replace(',', ''))
                low = int(td[5].text.strip().replace(',', ''))
                trade_vol = int(td[6].text.strip().replace(',', ''))
            except Exception:
                date = td[0].text.strip().replace('.', '-')
                logging.critical("{} :: Detected invalid data on page {}".
                                 format(date, code))
                logging.critical(
                    "Data of {} :: page {} was partially excluded.".
                    format(date, code))
                continue

            # Convert change(+) to change(%)
            change = float('%.2f' % (change / (end - change) * 100))

            if td[2].find('span', {'class': 'nv01'}):
                change *= -1
            elif td[2].find('span', {'class': 'red02'}):
                pass
            elif td[2].find('span').text.strip() == '0':
                pass
            else:
                logging.critical('Found inappropriate value while parsing.')

            data.append((date, end, change, start, high, low, trade_vol))

    logging.debug('return :: {} - code={} page={}'.
                  format(str(type(data)), code, page))
    return data
