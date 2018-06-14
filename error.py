import sys


class YukiError(Exception):
    def __init__(self, err_type, **kwargs):
        self.err_type = err_type
        self.kw = kwargs
        self.msg = None

        self.configure_msg()

    def configure_msg(self):
        ERR_TABLE = [(
            'InvalidStockCode',
            "Invalid stock code `{code}`."
        ), (
            'InvalidStock',
            '`{arg}` is not an appropriate <Stock> data.'
        ), (
            'InvalidDate',
            "`{date}` is not a valid date. " +
            "Use 'YYYY-MM-DD' format with actual date."
        ), (
            'InvalidArgType',
            "Argument `{arg}` must be {arg_type} type data."
        ), (
            'StockNotFound',
            'No stock was found with `{keyword}`.'
        ), (
            'NotEnoughArgument',
            'Argument for `{arg}`({type} type) is necessary.'
        ), (
            'InvalidArgument',
            'Argument for `{arg}` is invalid. ({description})'
        )
        ]

        for err in ERR_TABLE:
            if self.err_type == err[0]:
                self.msg = err[1].format(**self.kw)
                return
        # If not found, let the developer know the situation
        self.msg = 'CRITICAL :: Use of invalid YukiError.'

    def __str__(self):
        return self.msg
