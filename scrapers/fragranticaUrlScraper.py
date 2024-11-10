import bs4
import csv
from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://fragrantica.com/search/?dizajner=Perfumer%20H')

driver.implicitly_wait(2)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

html = driver.page_source
soup = bs4.BeautifulSoup(html, 'html.parser')

parent_div = soup.find('div', class_='off-canvas-content content1 has-reveal-left')
grid_parent_div = parent_div.find('div', class_='grid-x grid-padding-x grid-padding-y')
cell_parent_div = grid_parent_div.find('div', class_='cell small-12')
grid_divs = cell_parent_div.find_all('div', class_='grid-x grid-margin-x grid-padding-y')
child_cell_div = grid_divs[2].find('div', class_='cell small-12')
child_div = child_cell_div.find('div', class_='ais-InfiniteHits')

a_tags = child_div.find_all('a')
print('A tagovi pre pisanja: ', a_tags)
print('Duzina: ', len(a_tags))

with open('../datasets/fragranticaUrlOnly.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter='|')

    csv_writer.writerow(['Fragrance URL'])
    for a_tag in a_tags:
        href = a_tag.get('href')
        if href:
            csv_writer.writerow([href])

driver.quit()