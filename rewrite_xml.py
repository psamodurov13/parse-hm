import xml.etree.ElementTree as ET

tree = ET.parse('hm_products.xml')
root = tree.getroot()
for row in root.iter('row'):
    categories = row.find('cats').text.split(', ')
    print(categories)
    for cat in categories:
        category_id = ET.Element("category_id")
        category_id.text = cat
        row.append(category_id)

ET.dump(root)
tree = ET.ElementTree(root)
tree.write(open('test.xml', 'w'), encoding='unicode')
print('Готово')


