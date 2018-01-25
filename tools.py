import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import tabulate


def _TODAY():
    return datetime.now().strftime("%Y%m%d")


TODAY = _TODAY()


def PAST(**kwargs):
    if len(kwargs.keys()) != 1:
        raise TypeError("Must have one keyword as param: days, months, years")

    if type(kwargs[list(kwargs.keys())[0]]) != int:
        raise TypeError("Parameter must be <int> type number.")

    if list(kwargs.keys())[0] not in ['days', 'weeks', 'months', 'years']:
        raise ValueError("Invalid parameter.")

    now = datetime.now()

    if 'days' in kwargs.keys():
        now -= relativedelta(days=kwargs['days'])
    elif 'weeks' in kwargs.keys():
        now -= relativedelta(weeks=kwargs['weeks'])
    elif 'months' in kwargs.keys():
        now -= relativedelta(months=kwargs['months'])
    elif 'years' in kwargs.keys():
        now -= relativedelta(years=kwargs['years'])

    return now.strftime("%Y%m%d")


def reject_outliers(data, m=2):
    """ Filter out [(Median(data) - m * σ(data), (Median(data) - m * σ(data)].

    This function drops `outliers`, which are the data does not meet the
    specific criteria given as the parameter `m`.

    Args:
            data (pandas.DataFrame):  DataFrame object
            m    (int):               index for the criteria (default is 2)

    Returns:
            data (pandas.DataFrame):  DataFrame without the outliers


    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0
    return data[s < m]


def dprint(df):
    """ Prints out pandas.DataFrame to the console.

    Unlike the original print(), this function can print the data in a more
    fancy way, using the module `tabulate`. Besides, this adds comma to the
    <int64> type data for its readability. Although this process converts
    <int64> type into <object> type, it does not affects the original
    DataFrame.

    Args:
            df (pandas.DataFrame):  DataFrame object you want to print out
    
    Returns:
            None
    """

    df.is_copy = False  # so as to avoid SettingWithCopyWarning
    for column in df.columns.values:
        if df[column].dtype == 'int64':
            # Add comma to the int64 type column
            df[column] = df[column].map('{:,}'.format)
            # Add whitespaces so as to align numbers to the right
            max_len = df[column].map(len).max()
            format_string = '{:>' + str(max_len) + '}'
            df[column] = df[column].map(format_string.format)

    tabulate.PRESERVE_WHITESPACE = True
    print(tabulate.tabulate(df, headers='keys'))
    tabulate.PRESERVE_WHITESPACE = False
