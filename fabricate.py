import matplotlib.pyplot as plt
import matplotlib as mpl
# from scipy.interpolate import spline  # for making graph smoother
# import numpy as np
from cycler import cycler  # for updating mpl.rcParams


def plot_stock(df, indexes):
    # https://learnui.design/tools/data-color-picker.html#palette
    # Change color map
    cyc = cycler('color', ['#7a5195', '#003f5c', '#ef5675', '#ffa600'])
    mpl.rcParams['axes.prop_cycle'] = cyc

    # smoother_data = []
    # for index in indexes:
    df.plot('Date', indexes)

    plt.legend(loc='best', fancybox=True, framealpha=0.5)
    plt.title('Plot Testing')
    plt.show()
