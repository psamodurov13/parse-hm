import datetime
from bs4 import BeautifulSoup as bs
import requests as rq
import re
import json
from loguru import logger
import ast

logger.add('/home/user/python/parse-hm/debug.log', format='{time} {level} {message}', level="INFO", rotation="15 MB", compression="zip")

s = rq.Session()
headers = {
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
path_to_programm = '/home/user/python/parse-hm/'
path_to_site = '/home/user/web/sweethomedress.ru/public_html/'
head_url = 'https://sweethomedress.ru/'


def progress(text, m, file_name):
    with open(file_name, m) as file:
        file.write(text)


def get_prod_params(soup_prod):
    # Get script with parameters
    script = soup_prod.find_all('script')
    count = 0
    for i in script:
        count += 1
        if 'var productArticleDetails' in i.text:
            script_params = i.text
        else:
            continue
    # Get dict with parameters
    start = "isDesktop ?"
    end = ":"
    data = re.sub(start + r"\s.*\s" + end, '', script_params)
    start_index = data.find('var productArticleDetails = ') + len('var productArticleDetails = ')
    data = data[start_index:-1].strip()
    data = re.sub("'deliveryDetails':[^}]+},", '', data)
    # params = json.loads(data[:-1].replace("'", '"'))
    params = ast.literal_eval(data[:-1].replace("null", "'None'").replace('true', "'True'").replace('false', "'False'"))
    return params
