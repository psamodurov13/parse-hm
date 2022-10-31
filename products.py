import pickle
from bs4 import BeautifulSoup as bs
import requests as rq
import re
from pprint import pprint
import functions as fn
import datetime

with open('categories.pickle', 'rb') as file:
    all_cats = pickle.load(file)

pprint(all_cats)

s = rq.Session()
headers = {
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }

progress_file = 'progress-products.txt'
fn.progress(f'Запущено {datetime.datetime.now()}\n{"-"*40}\n', 'w', progress_file)

products = {}
iterat = 0
for cat in all_cats:
    links = []
    offset = 0
    last_show = 0
    fn.progress(f'Категория {cat}\n', 'a', progress_file)
    while True:
        response = s.get(f'{cat}?sort=stock&image-size=small&image=model&offset={offset}&page-size=500',
                         headers=headers)
        print(f'{response} {offset}')
        try:
            soup = bs(response.text, 'html.parser')
            show = soup.find('h2', class_='load-more-heading').get('data-items-shown')
            all = soup.find('h2', class_='load-more-heading').get('data-total')
            if show == last_show:
                fn.progress(f'Добавлено из категории: ALL - {all}, LINKS - {len(links)}', 'a', progress_file)
                break
            last_show = show
            new_links = [i.get('href') for i in soup.find_all('a', class_='item-link')]
            links.extend(new_links)
            print('show - ', show, ', all - ', all)
            if show == all:
                fn.progress(f'Добавлено из категории: ALL - {all}, LINKS - {len(links)}', 'a', progress_file)
                break
        except AttributeError:
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
    fn.progress(
        f'''
        Добавлено товаров: {created}, 
        Обновлено товаров: {updated},
        Всего товаров: {len(products)}
        {"-"*40}
        ''', 'a', progress_file)




with open('products.pickle', 'wb') as file:
    pickle.dump(products, file)
fn.progress(
        f'''
        Товары сохранены: {progress_file},
        Всего товаров: {len(products)}
        {"-"*40}
        ''', 'a', progress_file)
print('Всего товаров - ', len(products))


