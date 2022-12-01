import requests as rq
from bs4 import BeautifulSoup as bs
import re
import json
import html
import time
import xlsxwriter
import datetime
import pickle
import functions as fn
import proxies as px
import products, split_cols, join_cols, excel_to_xml, rewrite_xml, load_images, related

progress_file = 'progress.txt'


def main():
    proxies = px.choise_proxy()
    fn.logger.info(f'Selected proxy - {proxies}')
    s = rq.Session()
    fn.progress(f'Start parse products {datetime.datetime.now()}', 'w', progress_file)
    fn.logger.info(f'Start parse products {datetime.datetime.now()}')

    with open('products_old.pickle', 'rb') as file:
        old_prods = pickle.load(file)

    with open('products.pickle', 'rb') as file:
        new_prods = pickle.load(file)

    links_set = {}
    for i in new_prods:
        if i not in old_prods:
            links_set[i] = new_prods[i]

    fn.logger.info(f'Total new products: {len(links_set)}')
    fn.progress(
        f'''
        Total new products: {len(links_set)}
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

    # Iteration products
    count_prod = 0
    for link in reversed(links_set):
        try:
            start_time = time.time()
            try:
                # Load product page from english site for colection description data
                resp_prod = s.get(f'https://www2.hm.com{link.replace("tr_tr", "en_gb")}', headers=px.headers, timeout=60,
                                  proxies=proxies)
                site = 'en'
                eng += 1
            except Exception:
                # Load product page from turkish site, if page is not on english site
                resp_prod = s.get(f'https://www2.hm.com{link}', headers=px.headers, timeout=60, proxies=proxies)
                site = 'tr'
                turk += 1
            soup_prod = bs(resp_prod.text, 'html.parser')
            prod_id = str(re.search('\d+', link)[0])
            name = soup_prod.find('h1').text
            desc = soup_prod.find('p', class_='pdp-description-text').text
            cats = links_set[link]['categories']
            bread = ', '.join([i.get_text().replace('&', '').strip() for i in soup_prod.select('.breadcrumbs-placeholder li')][1:-1])
            params = fn.get_prod_params(soup_prod)
            # Get parametrs
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
            if style_articles == '':
                sa_index = resp_prod.text.find("styleWithDefaultArticles':'")
                sa_text = resp_prod.text[sa_index + 27:]
                sa_end_index = sa_text.find("',")
                style_articles = sa_text[:sa_end_index]
            measurement = ', '.join(params[prod_id]['productAttributes']['values'].get('measurement', ''))
            height_model = html.unescape(params[prod_id]['productAttributes']['values'].get('modelHeightGarmentSize', ''))
            made_in = params[prod_id]['productAttributes']['values'].get('productCountryOfProduction', '')
            sleeves = ', '.join(params[prod_id]['productAttributes']['values'].get('sleeveLength', ''))
            year = params[prod_id]['productAttributes']['values'].get('yearOfProduction', '')

            if site == 'en':
                resp_prod = s.get(f'https://www2.hm.com{link}', headers=px.headers, timeout=60, proxies=proxies)
                soup_prod = bs(resp_prod.text, 'html.parser')
                params = fn.get_prod_params(soup_prod)
            price = params[prod_id].get('whitePriceValue', '')
            red_price = params[prod_id].get('redPriceValue', '')
            all_sizes_dict = params[prod_id]['sizes']
            sizes_rq = s.get(f'https://www2.hm.com/hmwebservices/service/product/tr/availability/{prod_id[:-3]}.json',
                             headers=px.headers, proxies=proxies)
            sizes_dict = json.loads(sizes_rq.text)
            sizes = []
            for i in sizes_dict['availability']:
                for item in all_sizes_dict:
                    if i == item['sizeCode']:
                        sizes.append(item['name'].replace('½', '.5'))
            sizes = ', '.join(sizes)

            # Update variables with parameters to keep track of all parameters on the site
            parametrs.update([p for p in params[prod_id].keys() if p[0].isalpha()])
            parametrs_detail.update([p for p in params[prod_id]['productAttributes']['values'].keys() if p[0].isalpha()])
            all_parametrs = [link, name, desc, bread, prod_id, price, red_price, images, careInstructions, color_code,
                             coming_soon, composition, concept, description, detailed_desc, in_store, product_key,
                             related_products, sizes, style_articles, measurement, height_model, made_in,
                             sleeves, year, cats, site]
            all_products.append(
                [str(p) for p in all_parametrs]
            )
            # time.sleep(1.5)
            count_prod += 1
            fn.logger.info(f'PROD_ID: {prod_id} / ADDED / TIME: {time.time() - start_time} / '
                        f'PROCESSED: {count_prod}/{len(links_set)} / EXCEPTIONS: {len(exceptions)} / '
                        f'ENG: {eng} / TURK: {turk}')
            fn.progress(
                f'''
                PROD_ID: {prod_id} / ADDED / TIME: {time.time() - start_time}
                PROCESSED: {count_prod}/{len(links_set)}
                EXCEPTIONS: {len(exceptions)}
                ENG: {eng}
                TURK: {turk}
                {"-"*40}
                ''', 'a', progress_file
            )
        except Exception:
            exceptions.append(link)
            count_prod += 1
            fn.logger.exception(f'EXCEPTION: {link}')
            fn.progress(
                f'''
                LINK: {link} / NOT ADDED
                PROCESSED: {count_prod}/{len(links_set)}
                EXCEPTIONS: {len(exceptions)}
                {"-"*40}
                ''', 'a', progress_file
            )
        fn.logger.info(f'PROCESSED: {count_prod}/{len(links_set)}')

    file_name = f'products.xlsx'
    workbook = xlsxwriter.Workbook(file_name, options={'strings_to_urls': False})
    worksheet = workbook.add_worksheet()
    for row, line in enumerate(all_products):
        for col, cell in enumerate(line):
            worksheet.write(row, col, cell)
    workbook.close()

    old_prods.update(new_prods)
    with open('products_old.pickle', 'wb') as file:
        pickle.dump(old_prods, file)

    fn.logger.info(f'TOTAL PRODUCTS: {len(all_products)}, EXCEPTIONS: {len(exceptions)}, \nPARAMETRS: {parametrs}, '
                f'\nPARAMETRS_DETAIL: {parametrs_detail}')
    fn.progress(
        f'''
        TOTAL PRODUCTS: {len(all_products)}
        EXCEPTIONS: {len(exceptions)}
        PARAMETRS: {parametrs}
        PARAMETRS_DETAIL: {parametrs_detail}
        ''', 'a', progress_file
    )


if __name__ == '__main__':
    res = int(input('What should be done?\n1. Collect products, parse products from site, split file for translate\n'
                '2. Join files after translate, convert to xml, load images\n3. Make xmlx file with related_ids\n'))
    if res == 1:
        products.collect_products()
        main()
        split_cols.split_columns()
    elif res == 2:
        join_cols.join_columns()
        excel_to_xml.create_xml()
        rewrite_xml.rewrite()
        load_images.load_img()
    elif res == 3:
        related.make_related()
    else:
        print('Selected value is not correct.')

