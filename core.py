from urllib.request import urlopen
import json


def _parse_data(url, isJSON=False):
    html = urlopen(url).read().decode('euc-kr')
    return json.loads(html) if url else html
