import requests as rq
from bs4 import BeautifulSoup as bs
import functions as fn
from pprint import pprint
import pickle

head_cats = [
    'https://www2.hm.com/tr_tr/kadin.html',
    'https://www2.hm.com/tr_tr/erkek.html',
    'https://www2.hm.com/tr_tr/divided.html',
    'https://www2.hm.com/tr_tr/bebek.html',
    'https://www2.hm.com/tr_tr/cocuk.html',
    'https://www2.hm.com/tr_tr/home.html',
    'https://www2.hm.com/tr_tr/spor-dallari.html',
    'https://www2.hm.com/tr_tr/indirim.html'
]

s = rq.Session()
headers = {
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }

all_cats = {}
skip_categories = []

for head in head_cats:
    head_rq = s.get(head, headers=headers, timeout=60)
    print(head_rq)
    head_soup = bs(head_rq.text, 'html.parser')
    # print(head_soup)
    cats = ['https://www2.hm.com' + i.get('href') for i in head_soup.select('dd a')]
    # all_cats.extend(cats)
    for cat in cats:
        cat_rq = s.get(cat, headers=headers, timeout=60)
        print(cat, ' - ', cat_rq)
        cat_soup = bs(cat_rq.text, 'html.parser')
        try:
            name = cat_soup.find('h1').text.replace('\r\n    ', '')
            all_cats[cat] = {'name': name, 'parent': head}
            pprint(all_cats[cat])
        except AttributeError:
            print('Пропуск', cat)
            skip_categories.append(cat)
        subcats = ['https://www2.hm.com' + i.get('href') for i in
                   cat_soup.select('.secondary-nav .list-group .list-group ul li a')]
        print('subcats - ', len(subcats))
        if subcats:
            for subcat in subcats:
                subcat_rq = s.get(subcat, headers=headers, timeout=60)
                subcat_soup = bs(subcat_rq.text, 'html.parser')
                try:
                    name = subcat_soup.find('h1').text.replace('\r\n    ', '')
                    all_cats[subcat] = {'name': name, 'parent': cat}
                    pprint(all_cats[subcat])
                except AttributeError:
                    print('Пропуск', subcat)
                    skip_categories.append(subcat)


        # all_cats.extend(subcats)

with open('categories.pickle', 'wb') as file:
    pickle.dump(all_cats, file)

pprint(all_cats)
print('Всего категорий - ', len(all_cats))
print('Пропущены - ', len(skip_categories), ' : ', skip_categories)

