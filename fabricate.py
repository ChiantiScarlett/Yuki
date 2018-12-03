import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
# from scipy.interpolate import spline  # for making graph smoother
# import numpy as np
from cycler import cycler  # for updating mpl.rcParams
from datetime import datetime
from yuki.error import YukiError


def plot_stock(stock_name, df, index, start_date, end_date):

    font = {'family': 'NanumGothic'}
    mpl.rc('font', **font)

    # If index is single string, convert it to list
    if type(index) == str:
        index = [index]

    # Capitalize : Make index case-insensitive
    index = [x.title() for x in index]

    # If index are not found on column names, raise error
    possible_indexes = list(df)
    possible_indexes.remove('Date')
    if not set(index) < set(possible_indexes):
        raise YukiError('InvalidArgument', arg='index',
                        description='Possible indices are {}'
                        .format(str(possible_indexes)))

    # If start,end dates are not set yet, set their default value
    if start_date is None:
        start_date = df['Date'].values[-1]
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_date = datetime.strftime(start_date, '%Y-%m-%d')
    else:
        # Check if start_date is an actual date
        try:
            # Make YYYY-MM-DD format
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date = datetime.strftime(start_date, '%Y-%m-%d')
        except Exception:
            raise YukiError('InvalidDate', date=start_date)

    if end_date is None:
        end_date = df['Date'].values[0]
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = datetime.strftime(end_date, '%Y-%m-%d')
    else:
        # Check if end_date is an actual date
        try:
            # Make YYYY-MM-DD format
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = datetime.strftime(end_date, '%Y-%m-%d')
        except Exception:
            raise YukiError('InvalidDate', date=end_date)

    # Set date range within start_date and end_date
    s_idx = 0
    e_idx = 0
    for date in df['Date'].values:
        if start_date < date:
            s_idx += 1

        if end_date < date:
            e_idx += 1
    df = df[e_idx:s_idx]
    print(df)

    # print(df)
    # Conver Date into datetime obj
    # df['Date'] = pd.to_datetime(df['Date'][e_idx:s_idx], format='%Y-%m-%d')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

    # Plot stock

    # https://learnui.design/tools/data-color-picker.html#palette
    # Change color map
    cyc = cycler('color', ['#7a5195', '#003f5c', '#ef5675', '#ffa600'])
    mpl.rcParams['axes.prop_cycle'] = cyc

    # smoother_data = []
    # for index in index:
    ax = df.plot('Date', index)
    ax.get_yaxis().set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.legend(loc='best', fancybox=True, framealpha=0.5)
    plt.title(stock_name.encode('utf-8').decode('utf-8'))

    print(stock_name)
    plt.show()
