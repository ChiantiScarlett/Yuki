import sys


class YukiError(Exception):
    def __init__(self, err_type, **kwargs):
        sys.excepthook = self.Exception_Handler

        self.err_type = err_type
        self.kw = kwargs
        self.msg = None

        self.configure_msg()

    def configure_msg(self):
        ERR_TABLE = [(
            'InvalidStockCode',
            "Invalid stock code `{code}`.".format(**self.kw)
        ), (
            'InvalidStock',
            '`{arg}` is not an appropriate <Stock> data.'.format(**self.kw)
        )]

        for err in ERR_TABLE:
            if self.err_type == err[0]:
                self.msg = err[1]
                return

        # If not found, let the developer know the situation
        self.msg = 'CRITICAL :: Use of invalid YukiError.'

    def Exception_Handler(self, exception_type, exception, tb):
        print('[YukiError] :: {}'.format(self.msg))
