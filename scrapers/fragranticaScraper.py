import requests
import bs4
from selenium import webdriver
import csv

def scrape_fragrance_info(csv_writer):
    driver = webdriver.Firefox()
    driver.get('https://www.fragrantica.com/perfume/Valentino/Valentino-Uomo-Born-In-Roma-Coral-Fantasy-71761.html')

    driver.implicitly_wait(0.5)  # Ceka se pola sekunde

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    # Kao test cu raditi sa svojim Valentino parfemom
    url = 'https://www.fragrantica.com/perfume/Valentino/Valentino-Uomo-Born-In-Roma-Coral-Fantasy-71761.html'
    # url = 'https://www.punmiris.com/parfem/Valentino/Valentino-Uomo-Born-In-Roma-Coral-Fantasy-71761.html'
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

    # Ovo cu ovde ostaviti cisto ako se odlucimo da rasporedimo note kao top, middle i base
    note_headers = cell_div.find_all('h4')
    #print(note_headers)

    div_list = cell_div.find_all('div')
    notes = set()
    for div in reversed(div_list):
        if div.get_text() != '' and div.get_text() != 'Perfume Pyramid':
            can_add = True
            for note in notes:
                if note in div.get_text():
                    can_add = False
            if can_add:
                notes.add(div.get_text())

    print('Notes: ')
    for note in notes:
        print(note)

    # Skrejpovanje karakteristika poput: LONGEVITY, SILLAGE - ne znam da li mi se skale svidjaju iskreno al videcemo u sustini je prosecna ocena kao
    bottom_voting_charts = soup.find_all('div', class_='cell small-12 medium-6')
    for chart in bottom_voting_charts:
        #print(chart)
        #print(chart.get_text())
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

    # Dobavljanje rejtinga (za sada je to samo recenica u kojoj su izlistani i glasovi i ocena, mozemo to podeliti pa posle napisati neki algoritam za bolje racunanje)
    rating = soup.find_all('p', class_='info-note')
    print(rating[0].get_text())
    rating_number = rating[0].prettify().get_text()
    #rating_map = {}
    #rating_map["rating"] = "4"
    #rating_map["votes"] = "4000"

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

    parent_div = selenium_soup.find('div', class_='grid-x bg-white grid-padding-x grid-padding-y')  # Ovaj postoji samo jedan na sajtu
    parent_divs = parent_div.find_all('div', class_='cell small-12')  # Ovih ima 35
    child_grid_divs = parent_divs[1].find_all('div',
                                              class_='grid-x grid-margin-x grid-margin-y')  # njih ima 5 i to se poklapa
    child_cell_divs = child_grid_divs[3].find_all('div', class_='cell small-6')

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
    csv_writer.writerow(['BREND PARFEMA', 'IME PARFEMA', accords, notes, longevity_number, sillage_number, rating_number, season_ratings, day_ratings, perfumers, stripped_description, 'IMAGE URL'])


if __name__ == "__main__":
    # Verovatno je neka ideja da se cita iz fajla svaki parfem pojedinacno i da na osnovu toga formiramo search (taj search vrlo verovatno mora preko selenijuma da se uradi i da se rucno prati da li nalazi dobar parfem, nekada zeljeni parfem nije prvi na listi)
    # na fragrantici. E sad nije to bilo bas naivno tako da videcemo koliko ce moci tako da se radi. Mozda bude moralo i rucno ili semi-rucno sve...
    print('Scraping fragrance info from fragrantica...')

    with open('jPlusMFragranticaProba.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='|')

        csv_writer.writerow(['Brand', 'Name', 'Accords', 'Notes', 'Longevity', 'Sillage', 'Rating', 'Season ratings', 'Day ratings', 'Designers', 'Description', 'Image URL'])

        scrape_fragrance_info(csv_writer)

    print('Done scraping fragrance info from fragrantica!')
