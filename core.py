from urllib.request import urlopen
import json

API = {
    'summary': "",
    'realtime': "{code}"
}


def _parse_data(url, isJSON=False):
    html = urlopen(API[route].format(code=code)).read().decode('euc-kr')
    return json.loads(html) if url else html
