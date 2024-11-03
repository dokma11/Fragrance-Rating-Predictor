import requests
import bs4
import csv

def scrape_fragrances(csv_writer):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    for i in range(1, 92):
        print(i)
        url = f'https://www.metropoliten.rs/proizvodi/mirisi/parfemi/page/{i}/'
        response = requests.get(url, headers=headers)

        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        ul_tag = soup.find('ul', class_='products')
        li_tags = ul_tag.find_all('li')

        for li in li_tags:
            if li.find('h4'):
                brand_name = li.find('h4').get_text()
            else:
                brand_name = 'No brand name provided'

            if li.find('h3'):
                fragrance_name = li.find('h3').get_text()
            else:
                fragrance_name = 'No fragrance name provided'

            image_div = li.find('div', class_='product-image')
            image_tag = image_div.find('img')
            image_url = image_tag['src']

            print(f'{brand_name} {fragrance_name}, Image: {image_url}')
            csv_writer.writerow([brand_name, fragrance_name, image_url])

        i +=1

if __name__ == "__main__":
    print('Scraping fragrances from metrolopiten.rs...')

    with open('metropolitenResults.csv', mode ='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow(['Brand', 'Name', 'Image URL'])

        scrape_fragrances(csv_writer)

    print('Done scraping fragrances!')
