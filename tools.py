import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from suzaku.error import Error


def _TODAY():
    return datetime.now().strftime("%Y%m%d")


TODAY = _TODAY()


def PAST(**kwargs):
    if len(kwargs.keys()) != 1:
        raise Error("Must have one keyword as param: days, months, years")

    if type(kwargs[list(kwargs.keys())[0]]) != int:
        raise Error("Parameter must be <int> type number.")

    if list(kwargs.keys())[0] not in ['days', 'weeks', 'months', 'years']:
        raise Error("Invalid parameter.")

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
    """
    return values that belongs to [ m < Z < m ] boundaries
    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0
    return data[s < m]
