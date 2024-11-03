from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import bs4
import time
import csv

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

male_fragrances_urls = [
    'https://www.sephora.com/shop/cologne',
    'https://www.sephora.com/shop/cologne?currentPage=2',
    'https://www.sephora.com/shop/cologne?currentPage=3',
    'https://www.sephora.com/shop/cologne?currentPage=4',
    'https://www.sephora.com/shop/cologne?currentPage=5',
    'https://www.sephora.com/shop/cologne?currentPage=6',
]

female_fragrances_urls = [
    'https://www.sephora.com/shop/perfume',
    'https://www.sephora.com/shop/perfume?currentPage=2',
    'https://www.sephora.com/shop/perfume?currentPage=3',
    'https://www.sephora.com/shop/perfume?currentPage=4',
    'https://www.sephora.com/shop/perfume?currentPage=5',
    'https://www.sephora.com/shop/perfume?currentPage=6',
    'https://www.sephora.com/shop/perfume?currentPage=7',
    'https://www.sephora.com/shop/perfume?currentPage=8',
    'https://www.sephora.com/shop/perfume?currentPage=9',
    'https://www.sephora.com/shop/perfume?currentPage=10',
    'https://www.sephora.com/shop/perfume?currentPage=11',
    'https://www.sephora.com/shop/perfume?currentPage=12',
    'https://www.sephora.com/shop/perfume?currentPage=13',
    'https://www.sephora.com/shop/perfume?currentPage=14',
    'https://www.sephora.com/shop/perfume?currentPage=15',
]


def scrape_fragrances(urls, csv_writer):
    for url in urls:
        driver = webdriver.Firefox()
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'css-klx76'))
        )

        # posto su mnogi elementi namesteni na 'LazyLoad', moramo rucno da skrolujemo stranicu kako bi se svi ucitali...
        scroll_increment = 0.10 # skroluje se 10% visine stranice
        last_height = driver.execute_script("return document.body.scrollHeight")
        current_scroll_position = 0

        while current_scroll_position < last_height:
            current_scroll_position += last_height * scroll_increment
            driver.execute_script(f"window.scrollTo(0, {current_scroll_position});")
            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if current_scroll_position >= new_height:
                break
            last_height = new_height

        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')

        svi_a = soup.find_all('a', class_='css-klx76')

        for a in svi_a:
            brand_name = a.find('span', class_='css-ft3vv3 eanm77i0').get_text()
            product_name = a.find('span', class_='ProductTile-name css-h8cc3p eanm77i0').get_text()
            img_tag = a.find('img', class_='css-1rovmyu eanm77i0')
            if img_tag:
                img_src = img_tag['src']
            else:
                img_src = 'no image'

            print(f'{brand_name} {product_name}, Image: {img_src}')
            csv_writer.writerow([brand_name, product_name, img_src])


if __name__ == "__main__":
    print('Starting to scrape fragrances and write to CSV...')

    with open('sephoraResults.csv', mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow(['Brand', 'Name', 'Image URL'])

        scrape_fragrances(male_fragrances_urls, csv_writer)
        scrape_fragrances(female_fragrances_urls, csv_writer)

    print('Done scraping fragrances and writing to CSV!')