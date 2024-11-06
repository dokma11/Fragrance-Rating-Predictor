import requests
import bs4
from selenium import webdriver
import csv
import re

def scrape_fragrance_info(csv_writer):
    driver = webdriver.Firefox()
    driver.get('https://www.fragrantica.com/perfume/Valentino/Valentino-Uomo-Born-In-Roma-Coral-Fantasy-71761.html')

    driver.implicitly_wait(0.5)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    # test url
    url = 'https://www.fragrantica.com/perfume/Valentino/Valentino-Uomo-Born-In-Roma-Coral-Fantasy-71761.html'
    response = requests.get(url, headers=headers)

    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # Prvo mozemo da dobavimo akorde (akordi su pomesane note koje onda formiraju konkretan miris, nije samo sastojak kao sto je nota)
    # Akordi su dobavljeni redom kojim su i napisani, tako da ako nam je redosled bitan, necemo imati problema
    accords_div_cell = soup.find_all('div', class_ = 'cell small-6 text-center')
    accords_div_tag = accords_div_cell[1].find('div', class_='grid-x')
    accord_boxes = accords_div_tag.find_all('div', class_='cell accord-box')
    accords = []
    for accord_box in accord_boxes:
        accord = accord_box.find('div', class_='accord-bar').get_text()
        accords.append(accord)

    # Cisto radi provere
    print('Accords: ')
    for acc in accords:
        print(acc)

    # Skrejpovanje nota
    notes_chart = soup.find_all('div', class_='grid-x grid-padding-y')
    cell_div = notes_chart[0].find('div', class_='cell')

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

    # Skrejpovanje karakteristika poput: LONGEVITY, SILLAGE - ne znam da li mi se skale svidjaju iskreno al videcemo u sustini je prosecna ocena kao
    bottom_voting_charts = soup.find_all('div', class_='cell small-12 medium-6')
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

    # Dobavljanje rejtinga
    rating = soup.find_all('p', class_='info-note')
    print(rating[0].get_text())
    match = re.search(r'rating\s+([\d.]+)\s+out of\s+5 with\s+([\d,]+)\s+votes', rating[0].get_text())

    rating_dict = {}
    if match:
        rating_dict['rating'] = float(match.group(1))
        rating_dict['votes'] = int(match.group(2).replace(',', ''))
    else:
        rating_dict['rating'] = 0
        rating_dict['votes'] = 0

    # Dobavljanje opisa
    description = soup.find_all('div', {"itemprop": "description"})
    stripped_description = description[0].get_text().split('Read about this perfume in other languages')[0]
    print(stripped_description)

    # Dobavljanje dizajnera koji su kreirali parfem
    perfumers_div = soup.find('div', class_='grid-x grid-padding-x grid-padding-y small-up-2 medium-up-2')
    perfumer_names = perfumers_div.find_all('a')
    perfumers = []
    for perfumer in perfumer_names: # Samo proveriti da li ce raditi ako postoji iskljucivo jedan samo dizajner???
        # Mozemo videti da bude neka lista recimo ili sta cemo vec videcemo, msm da nije lose da ih imamo pa ako su potrebni jos bolje
        print(perfumer.get_text())
        perfumers.append(perfumer.get_text())

    # Dobavljanje godisnjih doba i toga
    html = driver.page_source
    selenium_soup = bs4.BeautifulSoup(html, 'html.parser')

    parent_div = selenium_soup.find('div', class_='grid-x bg-white grid-padding-x grid-padding-y')
    parent_divs = parent_div.find_all('div', class_='cell small-12')
    child_grid_divs = parent_divs[1].find_all('div', class_='grid-x grid-margin-x grid-margin-y')
    seasons_div = child_grid_divs[3].find_all('div', class_='voting-small-chart-size')

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

    # Pisanje u CSV fajl
    # Ovde se moram samo vratiti hardkodovao sam naziv parfema, brend i image url, kada se bude ucitavalo iz glavnog csv fajla bice drukcije
    csv_writer.writerow(['BREND PARFEMA', 'IME PARFEMA', accords, notes, longevity_number, sillage_number, rating_dict, season_ratings, day_ratings, perfumers, stripped_description, 'IMAGE URL'])


if __name__ == "__main__":
    # Verovatno je neka ideja da se cita iz fajla svaki parfem pojedinacno i da na osnovu toga formiramo search (taj search vrlo verovatno mora preko selenijuma da se uradi i da se rucno prati da li nalazi dobar parfem, nekada zeljeni parfem nije prvi na listi)
    # na fragrantici.
    print('Scraping fragrance information from fragrantica...')

    with open('../datasets/fragranticaProba.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='|')

        csv_writer.writerow(['Brand', 'Name', 'Accords', 'Notes', 'Longevity', 'Sillage', 'Rating', 'Season ratings', 'Day ratings', 'Designers', 'Description', 'Image URL'])

        scrape_fragrance_info(csv_writer)

    print('Done scraping fragrance info from fragrantica!')
