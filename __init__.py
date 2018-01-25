import logging
import pandas as pd

# Set logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s :: %(message)s]',
                    datefmt='%Y/%m/%d %H:%M:%S')

# Prevent DataFrame from splitting into multiple lines
pd.set_option('display.expand_frame_repr', False)
