import pandas as pd
import functions as fn


def join_columns():
    translated_cols = pd.read_excel('to_translate.xlsx')
    other_cols = pd.read_excel('not_translate.xlsx', converters={'prod_id': str, 'style_articles': str})

    products_rus = translated_cols.merge(other_cols, how='inner')
    products_rus = products_rus.drop('Unnamed: 0', axis=1)
    with pd.ExcelWriter('products_rus.xlsx', engine='xlsxwriter',
                        engine_kwargs={'options': {'strings_to_urls': False}}) as writer:
        products_rus.to_excel(writer, sheet_name='Sheet1')

    fn.logger.info('Done, file products_rus.xlsx ready for convert to xml')


if __name__ == '__main__':
    join_columns()
