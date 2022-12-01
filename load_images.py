import requests as rq
import pandas as pd
import functions as fn
from datetime import datetime
import pickle
import proxies as px


def load_img():
    fn.progress(f'Start load images {datetime.now()}\n', 'w', 'progress_load_images.txt')
    fn.logger.info(f'Start load images {datetime.now()}')
    proxies = px.choise_proxy()
    fn.logger.info(f'Selected proxy - {proxies}')
    s = rq.Session()
    df = pd.read_excel('products_rus.xlsx', converters={'prod_id':str})
    df_prod_img = df[['prod_id', 'images']]
    count_prod = 0
    try:
        with open('loaded_photos.pickle', 'rb') as file:
            loaded_photo = pickle.load(file)
    except Exception:
        fn.logger.exception('no previously uploaded photos')
        fn.progress('no previously uploaded photos', 'a', 'progress_load_images.txt')
        loaded_photo = []
    for i in df['prod_id']:
        if i not in loaded_photo:
            count_prod += 1
            images = df['images'][df['prod_id'] == i].values[0].split(', ')
            count = 1
            for url in images:
                image = s.get(url, headers=px.headers, proxies=proxies)
                fn.progress(f'Status code - {image.status_code}. ', 'a', 'progress_load_images.txt')
                filename = fn.path_to_site + 'load_images/' + str(i) + '-' + str(count) + '.jpg'
                with open(filename, 'wb') as file:
                    file.write(image.content)
                fn.progress(f'Processed {count}/{len(images)}\n', 'a', 'progress_load_images.txt')
                fn.logger.info(f'Processed {count}/{len(images)}')
                count += 1
            loaded_photo.append(i)
            fn.progress(f'Processed products: {count_prod}\n{"-"*40}\n', 'a', 'progress_load_images.txt')
            fn.logger.info(f'Processed products: {count_prod}')

    with open('loaded_photos.pickle', 'wb') as file:
        pickle.dump(loaded_photo, file)

    fn.logger.info('Done')


if __name__ == '__main__':
    load_img()
