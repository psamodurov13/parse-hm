# Parse products from H&M

## The program performs tasks:

- Collection of categories from the site
- Collection of goods from the site
- Parsing of collected goods
- Preparing a file for uploading to google translate
- creating an xml file with products
- uploading images to the server
- appointment of related products
- collection of current sizes and prices

## For the correct operation of the program, it is necessary
- python 3.8,
- install packages from requirements.txt (command pip install -r requirements.txt)
- fill in the path to the site on the server (path_to_site), site address (head_url), and also specify your path to the log file (line 8) in the functions.py file
- specify your proxies in the proxies.py file

## Instruction:

### Collection of categories
In the terminal, go to the folder with the program, run the categories.py file. We will get the categories.pickle file with the category dictionary

### Parsing of goods
In the terminal, go to the folder with the program, run the main.py file. The question and answer options are displayed. Enter 1 and press RETURN. We will receive two Excel files. One for uploading to google translate, the second with the rest of the parameters that do not require translation.

### Creating an XML file and uploading images to the server
First you need to replace the to_translate.xlsx file with the translated version of this file. Next, run the main.py file, enter 2 and press the RETURN button. We will receive the final XML file with products and uploaded pictures.

### Handling related_ids values (For uploading products to Opencart)
Unload goods from the site using the Import/Export Tool. Place the file in the folder with the program. Next, run the main.py file, enter 3 and press the RETURN button. We get an upload file with id values of related products in the related_ids column. You can upload a file to the site in the Import/Export Tool

### Size and price updates
Run the collect-sizes.py file. We get the actual_sizes.xml file in the site folder with up-to-date information about sizes and prices. To collect up-to-date information on a daily basis, you can add the following entry to crontab on the server (/home/user/python/parse-hm/ - path to the folder with the program)

0 12 * * * python3 /home/user/python/parse-hm/collect_sizes.py

