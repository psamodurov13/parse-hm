import xml.etree.ElementTree as ET
import pickle
import functions as fn


def rewrite():
    tree = ET.parse('hm_products.xml')
    root = tree.getroot()
    for row in root.iter('row'):
        categories = row.find('cats').text.split(', ')
        for cat in categories:
            category_id = ET.Element("category_id")
            category_id.text = cat
            category_id.tail = '\n'
            row.append(category_id)
        try:
            sizes = row.find('sizes').text.split(', ')
            for s in sizes:
                size = ET.Element("size")
                size.text = s
                size.tail = '\n'
                row.append(size)
        except Exception:
            fn.logger.exception('No sizes')


    with open('categories.pickle', 'rb') as file:
        categories_list = pickle.load(file)

    categories_tag = ET.Element('categories')
    categories_tag.tail = '\n'
    category = ET.SubElement(categories_tag, 'category')
    category.tail = '\n'
    category.text = 'HM'
    category.set('eng_name', 'HM')
    category.set('id', 'HM')
    for item in categories_list:
        category = ET.SubElement(categories_tag, 'category')
        category.tail = '\n'
        category.text = categories_list[item]['name'].replace('&', 'and')
        category.set('parent', categories_list[item]['parent'].replace('&', 'and'))
        category.set('eng_name', categories_list[item]['eng_name'].replace('&', 'and'))
        category.set('id', item.replace('&', 'and'))

    root.insert(0, categories_tag)

    ET.dump(root)
    tree = ET.ElementTree(root)
    tree.write(open(fn.path_to_site + 'hm_test_big.xml', 'w'), encoding='unicode')
    fn.logger.info('Done')


if __name__ == '__main__':
    rewrite()
