# Project Yuki
# Designed to run on iPython3 environment
# from yuki import *

import logging
import pandas as pd

# Set logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s :: %(message)s]',
                    datefmt='%Y/%m/%d %H:%M:%S')

# Prevent DataFrame from splitting into multiple lines
pd.set_option('display.expand_frame_repr', False)

logging.basicConfig(level=logging.DEBUG)


def init_yuki():
    from importlib import import_module
    # Necessary pre-installed modules are as follows:
    modules = ['setuptools',
               'matplotlib',
               'scipy',
               'numpy',
               'tabulate']
    operatable = True
    missing_modules = []
    for module in modules:
        try:
            import_module(module)
        except ImportError:
            operatable = False
            missing_modules.append(module)

    if not operatable:
        missing_modules = ", ".join(missing_modules)
        logging.critical("Please install following module(s): {}"
                         .format(missing_modules))
    if operatable:
        from yuki.parse import Stock
        from yuki.tools import past, today, dprint

        # Make them as global classes and functions
        global Stock, past, today, dprint


init_yuki()
