import pandas as pd


df = pd.read_excel('/Users/psamodurov13/PycharmProjects/parse-hm/products_rus.xlsx')

df = df.drop('Unnamed: 0', axis=1)
df.columns = [
    'name', 'desc', 'bread', 'careInstructions', 'composition', 'description', 'detailed_desc', 'measurement',
    'height_model', 'made_in', 'sleeves', 'link', 'prod_id', 'price', 'red_price',
    'images', 'color_code', 'coming_soon', 'concept', 'in_store', 'product_key', 'related_products', 'sizes',
    'style_articles', 'year', 'cats', 'site'
]

to_strip = ['name', 'desc', 'careInstructions', 'composition', 'description', 'detailed_desc', 'measurement',
            'height_model', 'made_in', 'sleeves']

for i in to_strip:
    df[i] = df[i].apply(lambda x: x.strip() if type(x) == str else x)

df['price'] = df['price'].apply(lambda x: int(x * 3.5 * 2))
df.loc[df['red_price'].notna(), 'red_price'] = df['red_price'] * 3.5 * 2
df['name'] = df['name'] + ' H&M'
df['name'] = df['name'].apply(lambda x: x[1].upper() + x[2:] if x[0] == ' ' else x[0].upper() + x[1:])
df['sizes'] = df['sizes'].apply(lambda x: x.replace('½', '.5'))

def fulldesc(row):
    desc = '<p>' + row['desc'] + '</p>'
    if type(row['careInstructions']) == str:
        care_text = '<ul><li>' + row['careInstructions'].replace(', ', '</li><li>') + '</li></ul>'
        care = '<div class="h4">Инструкция по уходу</div>' + care_text
    else:
        care = ''

    if type(row['height_model']) == str:
        m_height = '<p><strong>Рост модели: </strong>' + row['height_model'] + '</p>'
    else:
        m_height = ''

    if type(row['composition']) == str:
        sost = '<p><strong>Состав: </strong>' + row['composition'] + '</p>'
    else:
        sost = ''

    if type(row['measurement']) == str:
        meas = '<p>' + row['measurement'] + '</p>'
    else:
        meas = ''

    if type(row['made_in']) == str:
        made = '<p><strong>Страна: </strong>' + row['made_in'] + '</p>'
    else:
        made = ''

    return desc + m_height + meas + made + care + sost


df['full_desc'] = df.apply(fulldesc, axis=1)

df_xml = df[['name', 'desc', 'bread', 'prod_id', 'price', 'red_price', 'images',
             'careInstructions', 'color_code', 'composition',
             'concept', 'detailed_desc', 'sizes',
             'style_articles', 'height_model', 'made_in', 'sleeves',
             'year', 'full_desc', 'cats', 'site', 'related_products', 'link']]

df_xml['cats'] = df_xml['cats'].apply(lambda x: x[1:-1])
df_xml['cats'] = df_xml['cats'].apply(lambda x: x.replace("'", ''))

with open('hm_products.xml', 'w', encoding='utf-8') as file:
    file.write(df_xml.to_xml())
print('XML-файл создан')