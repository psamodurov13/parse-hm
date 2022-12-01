import requests as rq
from bs4 import BeautifulSoup as bs
import functions as fn
from pprint import pprint
import pickle
import proxies as px
import datetime

# List with main categories
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


def collect_categories():
    all_cats = {}
    skip_categories = []
    fn.logger.info(f'Start collecting categories: {datetime.datetime.now()}')
    # Collect categories to dict
    for head in head_cats:
        proxies = px.choise_proxy()
        fn.logger.info(f'Selected proxy - {proxies}')
        s = rq.Session()
        head_rq = s.get(head, headers=px.headers, timeout=60, proxies=proxies)
        head_soup = bs(head_rq.text, 'html.parser')
        try:
            head_name = head.replace('https://www2.hm.com/tr_tr/', '').replace('.html', '')
            all_cats[head_name] = {'name': head_name, 'parent': 'HM', 'eng_name': head_name}
            fn.logger.info(f'Head category: {all_cats[head_name]}')
            sub_heads = [i for i in head_soup.select('li.list-group')]
            for sub_head in sub_heads:
                try:
                    sub_head_name = head_name + '     ' + sub_head.find('strong', class_='list-group-title').text
                    eng_name = sub_head.find('strong', class_='list-group-title').get('data-tracking-label')
                    all_cats[sub_head_name] = {'name': sub_head_name, 'parent': head_name, 'eng_name': eng_name}
                    cats = ['https://www2.hm.com' + i.get('href') for i in sub_head.select('ul.menu li a')]
                    for cat in cats:
                        cat_rq = s.get(cat, headers=px.headers, timeout=60, proxies=proxies)
                        cat_soup = bs(cat_rq.text, 'html.parser')
                        repl = ['/>', '<meta ', 'property="og:url"', 'content=', '"']
                        og_url = str(cat_soup.find('meta', {'property': 'og:url'})).split('\n')[0]
                        for i in repl:
                            og_url = og_url.replace(i, '')
                        og_url = og_url.strip()
                        if og_url == cat:
                            try:
                                name = cat_soup.find('h1').text.replace('\r\n    ', '')
                                eng_name = cat_soup.find('a', class_='link current').get('data-tracking-label')
                                all_cats[cat] = {'name': name, 'parent': sub_head_name, 'eng_name': eng_name}
                                fn.logger.info(f'Category - {all_cats[cat]}')
                            except AttributeError:
                                fn.logger.info('Skip category - ', cat)
                                skip_categories.append(cat)
                            subcats = ['https://www2.hm.com' + i.get('href') for i in
                                       cat_soup.select('.secondary-nav .list-group .list-group ul li a')]
                            fn.logger.info(f'Quantity subcategories - {len(subcats)}')
                            if subcats:
                                for subcat in subcats:
                                    subcat_rq = s.get(subcat, headers=px.headers, timeout=60, proxies=proxies)
                                    subcat_soup = bs(subcat_rq.text, 'html.parser')
                                    try:
                                        name = subcat_soup.find('h1').text.replace('\r\n    ', '')
                                        eng_name = subcat_soup.find('a', class_='link current').get(
                                            'data-tracking-label')
                                        all_cats[subcat] = {'name': name, 'parent': cat, 'eng_name': eng_name}
                                        fn.logger.info(f'Subcategory - {all_cats[subcat]}')
                                    except AttributeError:
                                        fn.logger.info('Skip subcategory - ', subcat)
                                        skip_categories.append(subcat)
                except AttributeError:
                    fn.logger.info('Skip sub_head category - ', sub_head)
                    skip_categories.append(sub_head)
        except AttributeError:
            fn.logger.info('Skip head category - ', head)
            skip_categories.append(head)

    with open('categories.pickle', 'wb') as file:
        pickle.dump(all_cats, file)

    pprint(all_cats)
    fn.logger.info(f'Total categories - {len(all_cats)}')
    fn.logger.info(f'Total skiped - {len(skip_categories)} : {skip_categories}')


if __name__ == '__main__':
    collect_categories()
