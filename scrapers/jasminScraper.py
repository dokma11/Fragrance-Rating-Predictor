import requests
import bs4
import csv

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

male_fragrances_urls = [
    'https://www.jasmin.rs/muski-parfemi/parfemi-i-toaletne-vode.html#206=92187',
    'https://www.jasmin.rs/muski-parfemi/parfemi-i-toaletne-vode.html?p=2#206=91340',
    'https://www.jasmin.rs/muski-parfemi/parfemi-i-toaletne-vode.html?p=3#206=92444',
    'https://www.jasmin.rs/muski-parfemi/parfemi-i-toaletne-vode.html?p=4#206=98442',
    'https://www.jasmin.rs/muski-parfemi/parfemi-i-toaletne-vode.html?p=5#206=99533',
    'https://www.jasmin.rs/muski-parfemi/parfemi-i-toaletne-vode.html?p=6#206=97355',
    'https://www.jasmin.rs/muski-parfemi/parfemi-i-toaletne-vode.html?p=7#206=99901'
]

female_fragrances_urls = [
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html#206=94563',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=2#206=91683',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=3#206=92329',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=4#206=91787',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=5#206=93934',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=6#206=98439',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=7#206=92911',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=8#206=95281',
    'https://www.jasmin.rs/zenski-parfemi/parfemi-i-toaletne-vode.html?p=9#206=100279'
]


def scrape_fragrances(urls, gender, csv_writer):
    page_num = 1
    for url in urls:
        print(f'Scraping {gender} fragrances - Page {page_num}')
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f'Failed to fetch data from {url}: {e}')
            continue

        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        ol_tag = soup.find('ol', class_='products list items product-items')
        if not ol_tag:
            print(f"No products found on page {page_num} for {gender} fragrances.")
            continue

        li_tags = ol_tag.find_all('li')

        for li in li_tags:
            img_tag = li.find('img', class_='product-image-photo')
            img_src = img_tag['src'] if img_tag else 'No image'
            div_tag = li.find('div', class_='product details product-item-details')
            brand_name = div_tag.find('span',
                                      class_='product-item-brand').get_text().strip() if div_tag else 'Unknown Brand'
            strong_tag = div_tag.find('strong', class_='product name product-item-name') if div_tag else None
            item_name = strong_tag.find('a',
                                        class_='product-item-link').get_text().strip() if strong_tag else 'Unknown Item'

            print(f'{brand_name} {item_name}, Image: {img_src}')
            csv_writer.writerow([brand_name, item_name, img_src])

        page_num += 1


if __name__ == "__main__":
    print('Starting to scrape fragrances and write to CSV...')

    with open('jasminResults.csv', mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow(['Brand', 'Name', 'Image URL'])

        scrape_fragrances(male_fragrances_urls, 'male', csv_writer)

        scrape_fragrances(female_fragrances_urls, 'female', csv_writer)

    print('Done scraping fragrances and writing to CSV!')