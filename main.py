import requests as rq
from bs4 import BeautifulSoup as bs
import re
import json
import html
import time
import xlsxwriter
import datetime
from pprint import pprint
import pickle
import functions as fn


progress_file = 'progress.txt'

def main():
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    s = rq.Session()
    fn.progress(f'Запущен {datetime.datetime.now()}', 'w', progress_file)

    with open('products.pickle', 'rb') as file:
        links_set = pickle.load(file)
    print('Всего ссылок (set): ', len(links_set))
    fn.progress(
        f'''
        Всего ссылок (set): {len(links_set)}
        {"-"*40}
        ''', 'a', progress_file
    )
    parametrs = set()
    parametrs_detail = set()
    all_products = [[
    'link', 'name', 'desc', 'bread', 'prod_id', 'price', 'red_price', 'images', 'careInstructions', 'color_code',
    'coming_soon', 'composition', 'concept', 'description', 'detailed_desc', 'in_store', 'product_key',
    'related_products', 'sizes', 'style_articles', 'measurement', 'height_model', 'made_in', 'sleeves', 'year', 'cats',
    'site'
    ]]
    exceptions = []
    eng = 0
    turk = 0

    # Пробегаемся по товарам
    count_prod = 0
    for link in links_set:
        try:
            start_time = time.time()
            try:
                # Загружаем страницу товара с английского сайта для сбора описательных данных
                resp_prod = s.get(f'https://www2.hm.com{link.replace("tr_tr", "en_gb")}', headers=headers, timeout=60)
                site = 'en'
                eng += 1
            except Exception:
                # Загружаем страницу товара с турецкого сайта, если на ангрлийском данной страницы нет
                resp_prod = s.get(f'https://www2.hm.com{link}', headers=headers, timeout=60)
                site = 'tr'
                turk += 1
            soup_prod = bs(resp_prod.text, 'html.parser')
            prod_id = re.search('\d+', link)[0]
            name = soup_prod.find('h1').text
            desc = soup_prod.find('p', class_='pdp-description-text').text
            cats = links_set[link]['categories']
            # ПРОВЕРИТЬ СБОР КАТЕГОРИЙ БЕЗ ГЛАВНОЙ И НАЗВАНИЯ ТОВАРА И ЗАМЕНУ АМПЕРСАНДА
            bread = ', '.join([i.get_text().replace('&', '').strip() for i in soup_prod.select('.breadcrumbs-placeholder li')][1:-1])
            params = fn.get_prod_params(soup_prod)
            # Вытаскиваем параметры
            images = ', '.join(['https:' + i['zoom'].replace('mobilefullscreen', 'fullscreen') for i in params[prod_id].get('images', '')])
            careInstructions = ', '.join(params[prod_id].get('careInstructions', ''))
            color_code = params[prod_id].get('colorCode', '')
            coming_soon = params[prod_id].get('comingSoon', '')
            composition = ', '.join(params[prod_id].get('compositions', ''))
            concept = ', '.join(params[prod_id].get('concept', ''))
            description = params[prod_id].get('description', '')
            detailed_desc = ', '.join(params[prod_id].get('detailedDescriptions', ''))
            in_store = params[prod_id].get('inStore', '')
            product_key = params[prod_id].get('productKey', '')
            related_products = params[prod_id].get('productsWithStyleWith', '')
            style_articles = params[prod_id].get('styleWithDefaultArticles', '')
            measurement = ', '.join(params[prod_id]['productAttributes']['values'].get('measurement', ''))
            height_model = html.unescape(params[prod_id]['productAttributes']['values'].get('modelHeightGarmentSize', ''))
            made_in = params[prod_id]['productAttributes']['values'].get('productCountryOfProduction', '')
            sleeves = ', '.join(params[prod_id]['productAttributes']['values'].get('sleeveLength', ''))
            year = params[prod_id]['productAttributes']['values'].get('yearOfProduction', '')

            if site == 'en':
                resp_prod = s.get(f'https://www2.hm.com{link}', headers=headers, timeout=60)
                soup_prod = bs(resp_prod.text, 'html.parser')
                params = fn.get_prod_params(soup_prod)
            price = params[prod_id].get('whitePriceValue', '')
            red_price = params[prod_id].get('redPriceValue', '')
            sizes = ', '.join([p['name'] for p in params[prod_id].get('sizes', '')])

            # Обновляем переменные с параметрами для отслеживания всех параметров на сайте
            parametrs.update([p for p in params[prod_id].keys() if p[0].isalpha()])
            parametrs_detail.update([p for p in params[prod_id]['productAttributes']['values'].keys() if p[0].isalpha()])
            all_parametrs = [link, name, desc, bread, prod_id, price, red_price, images, careInstructions, color_code,
                             coming_soon, composition, concept, description, detailed_desc, in_store, product_key,
                             related_products, sizes, style_articles, measurement, height_model, made_in,
                             sleeves, year, cats, site]
            all_products.append(
                [str(p) for p in all_parametrs]
            )
            print('TIME: ', time.time() - start_time)
            pprint(all_products[-1])
            # time.sleep(1.5)
            count_prod += 1
            fn.progress(
                f'''
                PROD_ID: {prod_id} / ДОБАВЛЕН / TIME: {time.time() - start_time}
                ОБРАБОТАНО: {count_prod}/{len(links_set)}
                ОШИБОК: {len(exceptions)}
                ENG: {eng}
                TURK: {turk}
                {"-"*40}
                ''', 'a', progress_file
            )
        except Exception:
            exceptions.append(link)
            count_prod += 1
            print('Ошибка: ', link)
            fn.progress(
                f'''
                LINK: {link} / НЕ ДОБАВЛЕН
                ОБРАБОТАНО: {count_prod}/{len(links_set)}
                ОШИБОК: {len(exceptions)}
                {"-"*40}
                ''', 'a', progress_file
            )
        print(f'ОБРАБОТАНО: {count_prod}/{len(links_set)}')
        if count_prod == 50:
            break

    file_name = f'products.xlsx'
    workbook = xlsxwriter.Workbook(file_name, options={'strings_to_urls': False})
    worksheet = workbook.add_worksheet()
    for row, line in enumerate(all_products):
        for col, cell in enumerate(line):
            worksheet.write(row, col, cell)
    workbook.close()
    fn.progress(
        f'''
        ЗАГРУЖЕНО ТОВАРОВ: {len(all_products)}
        ОШИБОК: {len(exceptions)}
        PARAMETRS: {parametrs}
        PARAMETRS_DETAIL: {parametrs_detail}
        ''', 'a', progress_file
    )


if __name__ == '__main__':
    main()
