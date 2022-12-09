import requests as rq
import pickle
import proxies as px
import re
import functions as fn
import datetime
import json
from bs4 import BeautifulSoup as bs
import xml.etree.ElementTree as ET
from loguru import logger
import time


progress_file = 'progress_sizes.txt'

with open(fn.path_to_programm + 'products_old.pickle', 'rb') as file:
    products = pickle.load(file)

@logger.catch
def main():
    try:
        proxies = px.choise_proxy()
        logger.info(f'Selected proxy - {proxies}')
        s = rq.Session()
        logger.info(f'Start collect sizes {datetime.datetime.now()}')
        products_size = {}
        count = 0
        excepts = []
        for link in products:
            try:
                url = 'https://www2.hm.com' + link
                logger.info(f'{"-"*15} {url}')
                prod_id = str(re.search('\d+', link)[0])
                resp_prod = s.get(f'https://www2.hm.com{link}', headers=px.headers, timeout=60, proxies=proxies)
                if resp_prod.status_code != 200:
                    time.sleep(30)
                    logger.info(f'Status code {resp_prod.status_code}')
                    proxies = px.choise_proxy()
                    logger.info(f'Proxy replaced by - {proxies}')
                    resp_prod = s.get(f'https://www2.hm.com{link}', headers=px.headers, timeout=60, proxies=proxies)
                    if resp_prod.status_code != 200:
                        logger.info(f'All proxies are blocked in the process of work')
                        break
                logger.info(f'Status code {resp_prod.status_code}')
                soup_prod = bs(resp_prod.text, 'html.parser')
                try:
                    params = fn.get_prod_params(soup_prod)
                    sizes_rq = s.get(
                        f'https://www2.hm.com/hmwebservices/service/product/tr/availability/{prod_id[:-3]}.json',
                        headers=px.headers, proxies=proxies)
                    if sizes_rq.status_code != 200:
                        time.sleep(35)
                        logger.info(f'Status code {sizes_rq.status_code}')
                        proxies = px.choise_proxy()
                        sizes_rq = s.get(
                            f'https://www2.hm.com/hmwebservices/service/product/tr/availability/{prod_id[:-3]}.json',
                            headers=px.headers, proxies=proxies)
                        if sizes_rq.status_code != 200:
                            logger.info(f'All proxies are blocked in the process of work')
                            break
                    sizes_dict = json.loads(sizes_rq.text)
                    all_sizes_dict = params[prod_id]['sizes']
                    logger.info(f'Size dict - {all_sizes_dict}')
                    sizes = []
                    for i in sizes_dict['availability']:
                        for item in all_sizes_dict:
                            if i == item['sizeCode']:
                                sizes.append(item['name'].replace('½', '.5'))
                    logger.info(f'Availible sizes - {sizes}')
                    price = int(float(params[prod_id].get('whitePriceValue', '')) * 3.5)
                    red_price = params[prod_id].get('redPriceValue', '')
                    if red_price:
                        red_price = int(float(red_price) * 3.5)
                    products_size[prod_id] = {'url': url, 'sizes': sizes, 'price': str(price), 'red_price': str(red_price)}
                    logger.info(f'Price - {price}, with sale - {red_price}')
                except Exception:
                    logger.exception(f'Exception sizes - {url}')
                    excepts.append(url)
            except Exception:
                logger.exception(f'Exception pages - {link}')
                excepts.append(link)
            count += 1
            logger.info(f'Processed - {count}/{len(products)}')

        xml = ET.Element('data')
        for i in products_size:
            row = ET.SubElement(xml, 'row')
            row.tail = '\n'
            id = ET.SubElement(row, 'prod_id')
            id.text = i
            id.tail = '\n'
            url_in_xml = ET.SubElement(row, 'url')
            url_in_xml.text = products_size[i]['url']
            url_in_xml.tail = '\n'
            for size in products_size[i]['sizes']:
                size_in_xml = ET.SubElement(row, 'sizes')
                size_in_xml.text = size
                size_in_xml.tail = '\n'
            price_in_xml = ET.SubElement(row, 'price')
            price_in_xml.text = products_size[i]['price']
            price_in_xml.tail = '\n'
            red_price_in_xml = ET.SubElement(row, 'red_price')
            red_price_in_xml.text = products_size[i]['red_price']
            red_price_in_xml.tail = '\n'

        tree = ET.ElementTree(xml)
        tree.write(open(fn.path_to_site + 'actual_sizes.xml', 'w'), encoding='unicode')
        logger.info(f'XML created')
        logger.debug(f'exceptions {excepts}')

    except Exception:
        logger.exception('All proxies are blocked')


if __name__ == '__main__':
    main()