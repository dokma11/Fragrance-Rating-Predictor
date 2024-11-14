import requests
import bs4
from selenium import webdriver
import csv
import re
import random
import time


def scrape_fragrance_info(csv_writer, brand, name, image_url, fragrantica_url):
    # Ovako izbegnemo lakse error 429
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
        'Mozilla/5.0 (X11; Debian; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Mozilla/5.0 (X11; Manjaro Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (X11; openSUSE Tumbleweed; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/605.1.15',
        'Mozilla/5.0 (X11; Gentoo Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (X11; Arch Linux; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Mozilla/5.0 (X11; Linux Mint; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.36',
        'Mozilla/5.0 (X11; Slackware; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
        'Mozilla/5.0 (X11; Kali Linux; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Mageia; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (X11; Red Hat Enterprise Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Mozilla/5.0 (X11; Solus Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'Mozilla/5.0 (X11; elementary OS; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    ]

    user_agent = random.choice(user_agents)

    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
    }

    driver = webdriver.Firefox()
    driver.get(fragrantica_url)
    driver.implicitly_wait(0.5)

    response = requests.get(fragrantica_url, headers=headers)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    h1_gender = soup.find_all('h1', {'itemprop': 'name'})
    if 'for men' in h1_gender:
        gender = 'for men'
    elif 'for women and men' in h1_gender or 'for men and women':
        gender = 'for women and men'
    else:
        gender = 'for women'

    # Prvo mozemo da dobavimo akorde (akordi su pomesane note koje onda formiraju konkretan miris, nije samo sastojak kao sto je nota)
    # Akordi su dobavljeni redom kojim su i napisani, tako da ako nam je redosled bitan, necemo imati problema
    accords_div_cell = soup.find_all('div', class_ = 'cell small-6 text-center')
    if accords_div_cell and len(accords_div_cell) >= 2:
        accords_div_tag = accords_div_cell[1].find('div', class_='grid-x')
        if accords_div_tag:
            accord_boxes = accords_div_tag.find_all('div', class_='cell accord-box')
            if accord_boxes:
                accords = []
                for accord_box in accord_boxes:
                    accord = accord_box.find('div', class_='accord-bar').get_text()
                    accords.append(accord)

                # Cisto radi provere
                print('Accords: ')
                for acc in accords:
                    print(acc)
            else:
                accords = []
        else:
            accords = []
    else:
        accords = []

    # Skrejpovanje nota
    notes_chart = soup.find_all('div', class_='grid-x grid-padding-y')
    if notes_chart:
        cell_div = notes_chart[0].find('div', class_='cell')
        if cell_div:
            div_list = cell_div.find_all('div')

            # Splitujemo string po 'Top Notes', 'Middle Notes' i 'Base Notes'
            sections = re.split(r'Top Notes|Middle Notes|Base Notes', div_list[0].get_text())

            # Potom kreiramo kljuceve za mapu/recnik i stripujemo kako bismo izbegli nepotrebne razmake
            notes = {
                "Top Notes": sections[1].strip() if len(sections) > 1 else "",
                "Middle Notes": sections[2].strip() if len(sections) > 2 else "",
                "Base Notes": sections[3].strip() if len(sections) > 3 else ""
            }

            # S obrzirom na to kakav string dobijemo, razdvajamo ga ana mestima gde je malo slovo proed velikog, tu bi trebalo da je pocetak naziva nove note
            for key in notes:
                notes[key] = re.sub(r'([a-z])([A-Z])', r'\1| \2', notes[key]).split('| ')
                notes[key] = [note.strip() for note in notes[key] if note.strip()]

            print('Notes: ', notes)
        else:
            notes = []
    else:
        notes = []

    # Skrejpovanje karakteristika poput: LONGEVITY, SILLAGE - ne znam da li mi se skale svidjaju iskreno al videcemo u sustini je prosecna ocena kao
    bottom_voting_charts = soup.find_all('div', class_='cell small-12 medium-6')
    if bottom_voting_charts:
        for chart in bottom_voting_charts:
            if 'longevity' in chart.get_text():
                # longevity scale: eternal: 4.5 - 5.0, long-lasting: 4.0 - 4.49, moderate: 3.5 - 3.9, weak: 3.0 - 3.49, very weak: 0.0 - 2.99
                print(chart.get_text())
                longevity_number = chart.get_text().split(":")[1].split()[0]
                print(longevity_number)
            elif 'sillage' in chart.get_text():
                # sillage scale: enormous: 3.4 - 4.0, strong: 2.8 - 3.39, moderate: 2.2 - 2.79, intimate: 0.0 - 2.19
                print(chart.get_text())
                sillage_number = chart.get_text().split(":")[1].split()[0]
                print(sillage_number)
    else:
        longevity_number = ''
        sillage_number = ''

    # Dobavljanje rejtinga
    rating = soup.find_all('p', class_='info-note')
    rating_dict = {}
    if rating:
        print(rating[0].get_text())
        match = re.search(r'rating\s+([\d.]+)\s+out of\s+5 with\s+([\d,]+)\s+votes', rating[0].get_text())

        if match:
            rating_dict['rating'] = float(match.group(1))
            rating_dict['votes'] = int(match.group(2).replace(',', ''))
        else:
            rating_dict['rating'] = 0
            rating_dict['votes'] = 0
    else:
        rating_dict['rating'] = 0
        rating_dict['votes'] = 0

    # Dobavljanje opisa
    description = soup.find_all('div', {"itemprop": "description"})
    if description:
        stripped_description = description[0].get_text().split('Read about this perfume in other languages')[0]
        print(stripped_description)
    else:
        stripped_description = 'No description provided'

    # Dobavljanje dizajnera koji su kreirali parfem
    perfumers_div = soup.find('div', class_='grid-x grid-padding-x grid-padding-y small-up-2 medium-up-2')
    if perfumers_div:
        perfumer_names = perfumers_div.find_all('a')
        perfumers = []
        for perfumer in perfumer_names: # Samo proveriti da li ce raditi ako postoji iskljucivo jedan samo dizajner???
            # Mozemo videti da bude neka lista recimo ili sta cemo vec videcemo, msm da nije lose da ih imamo pa ako su potrebni jos bolje
            print(perfumer.get_text())
            perfumers.append(perfumer.get_text())
    else:
        perfumers = ['None']

    # Dobavljanje godisnjih doba i toga
    html = driver.page_source
    selenium_soup = bs4.BeautifulSoup(html, 'html.parser')

    parent_div = selenium_soup.find('div', class_='grid-x bg-white grid-padding-x grid-padding-y')
    if parent_div:
        parent_divs = parent_div.find_all('div', class_='cell small-12')
        if parent_divs and len(parent_divs) >= 2:
            child_grid_divs = parent_divs[1].find_all('div', class_='grid-x grid-margin-x grid-margin-y')
            if child_grid_divs and len(child_grid_divs) >= 4:
                seasons_div = child_grid_divs[3].find_all('div', class_='voting-small-chart-size')
                if seasons_div:
                    season_labels = ['winter', 'spring', 'summer', 'fall', 'day', 'night']
                    season_values = []

                    for i, season in enumerate(seasons_div[5:]):
                        child_season = season.find('div').find('div')

                        style = child_season.get('style')

                        for attr in style.split(';'):
                            if 'width' in attr:
                                width = attr.split(':')[1].strip()
                                print(f"{season_labels[i]} width: {width}")
                                season_values.append(width)

                    winter = season_values[0]
                    spring = season_values[1]
                    summer = season_values[2]
                    fall = season_values[3]
                    day = season_values[4]
                    night = season_values[5]

                    print(f"Winter: {winter}, Spring: {spring}, Summer: {summer}, Fall: {fall}, Day: {day}, Night: {night}")

                    season_ratings = f"Winter: {winter}, Spring: {spring}, Summer: {summer}, Fall: {fall}"
                    day_ratings = f"Day: {day}, Night: {night}"
                else:
                    season_ratings, day_ratings = 'No rating provided'
            else:
                season_ratings, day_ratings = 'No rating provided'
        else:
            season_ratings, day_ratings = 'No rating provided'
    else:
        season_ratings, day_ratings = 'No rating provided'
    # Pisanje u CSV fajl
    # Ovde se moram samo vratiti hardkodovao sam naziv parfema, brend i image url, kada se bude ucitavalo iz glavnog csv fajla bice drukcije
    csv_writer.writerow([brand, name, accords, notes, gender, longevity_number, sillage_number, rating_dict, season_ratings, day_ratings, perfumers, stripped_description, image_url])
    driver.quit()

if __name__ == "__main__":
    # Verovatno je neka ideja da se cita iz fajla svaki parfem pojedinacno i da na osnovu toga formiramo search (taj search vrlo verovatno mora preko selenijuma da se uradi i da se rucno prati da li nalazi dobar parfem, nekada zeljeni parfem nije prvi na listi)
    # na fragrantici.
    print('Scraping fragrance information from fragrantica...')

    with open('../datasets/togetherUniqueForInput.csv', 'r', encoding='utf-8') as fragrance_file:
        csv_reader = csv.reader(fragrance_file)
        next(csv_reader)
        with open('../datasets/fragranticaTemp.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter='|')

            csv_writer.writerow(['Brand', 'Name', 'Accords', 'Notes', 'Gender', 'Longevity', 'Sillage', 'Rating', 'Season ratings', 'Day ratings', 'Designers', 'Description', 'Image URL'])

            timeout_counter = 1 # namerno pocinjem od 1 jer msm da na 5 vec pukne
            for row in csv_reader:
                timeout_counter += 1
                if timeout_counter % 5 == 0:
                    time.sleep(360) # ceka sest minuta
                brand, name, image_url, fragrantica_url = row
                print(f'Scraping {brand} - {name} from {fragrantica_url}...')
                scrape_fragrance_info(csv_writer, brand, name, image_url, fragrantica_url)

    print('Done scraping fragrance info from fragrantica!')
