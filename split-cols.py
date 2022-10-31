import pandas as pd

data = pd.read_excel('products.xlsx')
translate_cols = ['name', 'desc', 'bread', 'careInstructions', 'composition', 'description',
                          'detailed_desc', 'measurement', 'height_model', 'made_in', 'sleeves']
nontranslate_cols = [i for i in data.columns if i not in translate_cols]
xlsx_to_translate = data[translate_cols]
xlsx_not_translate = data[nontranslate_cols]
with pd.ExcelWriter('to_translate.xlsx', engine='xlsxwriter',
                    engine_kwargs={'options': {'strings_to_urls': False}}) as writer:
    xlsx_to_translate.to_excel(writer, sheet_name='Sheet1')
with pd.ExcelWriter('not_translate.xlsx', engine='xlsxwriter',
                    engine_kwargs={'options': {'strings_to_urls': False}}) as writer:
    xlsx_not_translate.to_excel(writer, sheet_name='Sheet1')




