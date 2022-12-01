import pandas as pd
import functions as fn


def make_related():
    file = 'products-for-rel.xlsx'
    sn = pd.ExcelFile(file).sheet_names
    all_sheets = {}
    for i in sn:
        if i == 'Products':
            all_sheets[i] = pd.read_excel(file, i, converters={'sku': str, 'model': str})
        else:
            all_sheets[i] = pd.read_excel(file, i)
        fn.logger.info(f'{i} loaded')
    for i in all_sheets:
        for c in all_sheets[i].columns:
            if all_sheets[i][c].dtype == bool:
                all_sheets[i][c] = all_sheets[i][c].astype('str')
                fn.logger.info(f'{i} ==> {c}: replaced by str')


    df_all = all_sheets['Products']
    df = df_all[df_all['manufacturer'] == 'H&amp;M']
    df = df[['product_id', 'sku']]
    df = df.set_index('product_id')
    df_dict = df.to_dict()['sku']

    products_df = pd.read_excel('products_rus.xlsx', converters={'prod_id': str})
    products_df = products_df[['prod_id', 'style_articles']].set_index('prod_id').to_dict()['style_articles']
    df_all.loc[df_all['manufacturer'] == 'H&amp;M', 'store_ids'] = '8'

    for i in df_dict:
        sku = df_dict[i]
        if sku in products_df:
            df_dict[i] = products_df[sku]
        else:
            df_dict[i] = df_all['related_ids'][df_all['product_id'] == i]

    excepts = []
    for i in df_all['product_id']:
        if i in df_dict:
            try:
                related = df_dict[i].split(',')
                related_prods = []
                for rp in related:
                    if rp in df_all['sku'].values:
                        prod_id = str(df_all['product_id'][df_all['sku'] == rp].values[0])
                        fn.logger.info(f'{rp} ==> {prod_id}')
                        related_prods.append(prod_id)
                    else:
                        fn.logger.info(f'{rp} not in file')
                df_all.loc[df_all['product_id'] == i, 'related_ids'] = ','.join(related_prods)
            except Exception:
                fn.logger.exception(f'{i}  skiped')
                excepts.append(i)

    writer = pd.ExcelWriter('products_with_related.xlsx', engine='xlsxwriter')

    for sheet_name in all_sheets.keys():
        all_sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()

    fn.logger.info('Done')


if __name__ == '__main__':
    make_related()