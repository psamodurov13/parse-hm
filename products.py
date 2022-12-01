import pickle
from bs4 import BeautifulSoup as bs
import requests as rq
import re
from pprint import pprint
import functions as fn
import datetime
import proxies as px

with open('categories.pickle', 'rb') as file:
    all_cats = pickle.load(file)


def collect_products():
    progress_file = 'progress-products.txt'
    fn.progress(f'Start collection products {datetime.datetime.now()}\n{"-"*40}\n', 'w', progress_file)
    fn.logger.info(f'Start collection products {datetime.datetime.now()}')

    try:
        proxies = px.choise_proxy()
        fn.logger.info(f'Selected proxy - {proxies}')
        s = rq.Session()
        products = {}
        resp = 200
        for cat in all_cats:
            links = []
            offset = 0
            last_show = 0
            fn.progress(f'Category {cat}\n', 'a', progress_file)
            fn.logger.info(f'Category {cat}')
            while True:
                try:
                    response = s.get(f'{cat}?sort=stock&image-size=small&image=model&offset={offset}&page-size=500',
                                     headers=px.headers, proxies=proxies)
                    resp = response.status_code
                    try:
                        soup = bs(response.text, 'html.parser')
                        show = soup.find('h2', class_='load-more-heading').get('data-items-shown')
                        all = soup.find('h2', class_='load-more-heading').get('data-total')
                        if show == last_show:
                            fn.progress(f'Added from category: ALL - {all}, LINKS - {len(links)}', 'a', progress_file)
                            fn.logger.info(f'Added from category: ALL - {all}, LINKS - {len(links)}')
                            break
                        last_show = show
                        new_links = [i.get('href') for i in soup.find_all('a', class_='item-link')]
                        links.extend(new_links)
                        if show == all:
                            fn.progress(f'Added from category: ALL - {all}, LINKS - {len(links)}', 'a', progress_file)
                            fn.logger.info(f'Added from category: ALL - {all}, LINKS - {len(links)}')
                            break
                    except AttributeError:
                        break
                except Exception:
                    fn.logger.info(f'Skip - {cat}')
                    break
                offset += 500
            created = 0
            updated = 0
            for link in links:
                if link in products:
                    products[link]['categories'].append(cat)
                    updated += 1
                else:
                    products[link] = {'categories': [cat]}
                    created += 1
            writed_text = f'Added products: {created}, Update products: {updated}, Total products: {len(products)}'
            fn.progress(writed_text, 'a', progress_file)
            fn.logger.info(writed_text)

        if resp == 200:
            with open('products.pickle', 'wb') as file:
                pickle.dump(products, file)
        writed_text2 = f'Saved products: {progress_file}, Total products: {len(products)}'
        fn.progress(writed_text2, 'a', progress_file)
        fn.logger.info(writed_text2)
        fn.logger.info(f'Total products - {len(products)}')

    except Exception:
        fn.logger.info('All proxies banned')
        fn.progress(f'All proxies banned', 'a', progress_file)


if __name__ == '__main__':
    collect_products()
