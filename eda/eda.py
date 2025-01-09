import pandas as pd
from ast import literal_eval
from collections import Counter
import itertools
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np

def parse_season_ratings(rating_str):
    # Koristimo regularne izraze da izdvojimo sezonske podatke
    season_data = {}
    pattern = r'([A-Za-z]+):\s*([0-9.]+)%'
    matches = re.findall(pattern, rating_str)
    for season, percentage in matches:
        season_data[season] = float(percentage)
    return season_data

# Učitavanje podataka
# Pretpostavljamo da je dataset sačuvan u CSV formatu
file_path = "../datasets/mainDataset.csv"
data = pd.read_csv(file_path, delimiter='|')

# Pretvaranje stringova u liste i rečnike gde je potrebno
data['Accords'] = data['Accords'].apply(literal_eval)
data['Notes'] = data['Notes'].apply(literal_eval)
data['Rating'] = data['Rating'].apply(literal_eval)
data['Season ratings'] = data['Season ratings'].apply(parse_season_ratings)
data['Day ratings'] = data['Day ratings'].apply(parse_season_ratings)
data['Designers'] = data['Designers'].apply(literal_eval)

# Pitanje 1: Које су најзаступљеније ноте у 5 најбоље оцењених парфема, препоручених за ноћ, са најмање 5000 рецензија?
def top_notes_night_perfumes(data):
    # Filtriranje podataka: parfemi sa najmanje 5000 glasova i noćnim ocenama iznad 95%
    filtered = data[(data['Day ratings'].apply(lambda x: x['Night'] >= 80 and x['Day'] <= 50)) & 
                    (data['Rating'].apply(lambda x: x['votes'] >= 5000))]
    
    # Sortiranje po oceni
    top_rated = filtered.sort_values(by='Rating', key=lambda x: x.apply(lambda y: y['rating']), ascending=False).head(5)

    notes = []
    perfumes_info = []  # Lista za čuvanje brenda i naziva top 5 parfema
    
    for _, row in top_rated.iterrows():
        # Dobijanje naziva i brenda
        perfume_name = row['Name']
        brand_name = row['Brand']
        rating = row['Rating']['rating']
        votes = row['Rating']['votes']
        # Dodavanje u listu parfema sa nazivima i brendovima
        perfumes_info.append((perfume_name, brand_name, rating, votes))
        
        # Dodavanje nota
        note_dict = row['Notes']
        notes.extend(note_dict.get('Top Notes', []) + 
                     note_dict.get('Middle Notes', []) + 
                     note_dict.get('Base Notes', []))
    
    # Vraćanje 10 najzastupljenijih nota i informacija o top 5 parfema
    most_common_notes = Counter(notes).most_common(10)
    
    return most_common_notes, perfumes_info

# Pitanje 2: Који проценат парфема препоручених за летњу сезону је оцењен испод оцене 3.00?
def summer_perfumes_below_rating(data):
    summer_perfumes = data[data['Season ratings'].apply(lambda x: x['Summer'] > 80 and  x['Winter'] <= 50)]
    below_rating = summer_perfumes[summer_perfumes['Rating'].apply(lambda x: x['rating'] < 4.0)]
    return len(below_rating) / len(summer_perfumes) * 100

# Pitanje 3: Који су најчешћи акорди и ноте у парфемима који се препоручују за зимску сезону?
def winter_perfumes_accords_notes(data):
    winter_perfumes = data[data['Season ratings'].apply(lambda x: x['Winter'] > 80)]
    accords = Counter()
    notes = []
    for _, row in winter_perfumes.iterrows():
        accords.update(row['Accords'])
        # Ako su 'Notes' liste, direktno ih proširujemo
        if isinstance(row['Notes'], list):  # Ako je 'Notes' lista
            notes.extend(row['Notes'])
        else:  # Ako je 'Notes' rečnik, onda proširujemo 'Top', 'Middle' i 'Base' note
            note_dict = row['Notes']
            notes.extend(note_dict.get('Top Notes', []))
            notes.extend(note_dict.get('Middle Notes', []))
            notes.extend(note_dict.get('Base Notes', []))
    return accords.most_common(10), Counter(notes).most_common(10)

# Pitanje 4: Колики је проценат парфемских кућа које су учествовале у креирању 20 најбоље оцењених парфема са више од 10.000 рецензија?
def top_perfume_houses(data):
    # Филтрирање парфема са више од 10.000 рецензија
    filtered = data[data['Rating'].apply(lambda x: x['votes'] > 10000)]

    # Сортирање по рејтингу и узимање топ 20
    top_20 = filtered.sort_values(by='Rating', key=lambda x: x.apply(lambda y: y['rating']), ascending=False).head(20)

    # Узимање имена топ 20 парфема
     # Uzimanje imena top 20 parfema, vrednosti ocena i broja glasova
    top_perfumes = [
        {
            'name': row['Name'],
            'rating': row['Rating']['rating'],
            'votes': row['Rating']['votes']
        }
        for _, row in top_20.iterrows()
    ]

    # Proveravamo i konvertujemo Designers u liste ako su stringovi
    if isinstance(top_20['Brand'].iloc[0], str):
        top_20['Brand'] = top_20['Brand'].apply(lambda x: x.split(', '))

    # Brojanje učestvovanja brendova u top 20
    house_counts = Counter(house for designers in top_20['Brand'] for house in designers)

    # Računanje udeo svakog brenda
    total_top_20 = len(top_20)
    house_percentages = {house: (count / total_top_20) * 100 for house, count in house_counts.items()}


    return {
        'house_percentages': house_percentages,  # Проценти по кућама
        'top_perfumes': top_perfumes  # Имена топ 20 парфема
    }

# Pitanje 5: Која сезона се највише препоручује за парфеме са оценом 4,30 више, који такође имају најмање 5000 рецензија?
# (stavila sam da nadje za svaku sezonu broj parfma koji zadovoljavaju upit, najvece je winter, ali vraca vise informacija)
def most_recommended_season(data):
    filtered = data[(data['Rating'].apply(lambda x: x['rating'] >= 4.3)) & 
                    (data['Rating'].apply(lambda x: x['votes'] >= 5000))]
    
    season_counter = Counter()
    season_perfumes = {"Winter": [], "Spring": [], "Summer": [], "Fall": []}
    
    for _, row in filtered.iterrows():
        # Pronađi sezonu sa najvećim procentom
        season_ratings = row['Season ratings']  # Već je parsiran u dict
        max_season = max(season_ratings, key=season_ratings.get)  # Sezona sa najvećim procentom
        season_counter[max_season] += 1  # Povećaj brojanje za tu sezonu
        
        # Dodaj informacije o parfemu za tu sezonu
        season_perfumes[max_season].append({
            'name': row['Name'],
            'rating': row['Rating']['rating'],
            'votes': row['Rating']['votes']
        })
    
    return {
        'season_counts': season_counter.most_common(4),  # Broj parfema po sezoni
        'season_perfumes': season_perfumes  # Detalji o parfemima po sezoni
    }
# Pitanje 6: Ко су 5 најбољих парфимера на основу оцене њихових парфема?
def top_perfumers(data, min_votes=50000):
    perfumer_scores = Counter()
    perfumer_counts = Counter()
    perfumer_votes = Counter()

    # Prikupljanje podataka o ocenama i glasovima
    for _, row in data.iterrows():
        for perfumer in row['Designers']:
            rating = row['Rating']['rating']
            votes = row['Rating']['votes']  # Pretpostavljamo da postoji broj glasova
            perfumer_scores[perfumer] += rating * votes
            perfumer_counts[perfumer] += 1
            perfumer_votes[perfumer] += votes
    
    # Računanje ponderisanih prosek ocena za svakog parfumer
    avg_scores = {}
    for perfumer in perfumer_scores:
        total_votes = perfumer_votes[perfumer]
        
        # Samo parfumeri sa dovoljnim brojem glasova
        if total_votes >= min_votes:
            avg_scores[perfumer] = perfumer_scores[perfumer] / total_votes
        else:
            # Ako parfumer ima manje glasova od min_votes, ne uzimamo ga u obzir
            continue
    
    # Sortiranje po ponderisanoj oceni
    sorted_perfumers = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Ispis rezultata
    print("Top 5 parfumeri po ponderisanoj oceni i broju glasova:")
    for perfumer, score in sorted_perfumers:
        total_votes = perfumer_votes[perfumer]
        print(f"{perfumer}: Ponderisana ocena = {score:.2f}, Ukupno glasova = {total_votes}")
    
    return sorted_perfumers, perfumer_votes

# Pitanje 7: Која комбинација од 3 ноте је најчешћа међу парфемима са оценом 4,50 и више, који такође имају најмање 5000 рецензија?
def most_common_note_combinations(data):
    filtered = data[(data['Rating'].apply(lambda x: x['rating'] >= 3.5)) & #promenila sam da bude 4, jer ima jako malo parfmeema preko 4.5, svakako se moze podesaavati, 
                    (data['Rating'].apply(lambda x: x['votes'] >= 5000))] #MOZE SE PODESAVATI SVE OD VREDNOSTI I U DRUGIM UPITIMA
    """
    Funkcija koja računa najčešće triplete nota u 'Base Notes'
    iz kolone 'Notes' u DataFrame-u.
    """
    triplets = []  # Lista za triplete
    print(len(filtered))
    # Iteracija kroz svaki zapis u koloni 'Notes'
    for notes in filtered['Notes']:
        base_notes = notes.get('Base Notes', [])  # Uzmi Base Notes ako postoje
        if len(base_notes) >= 3:  # Samo ako ima najmanje 3 note u Base Notes
            sorted_base_notes = sorted(base_notes)  # Sortiranje nota po abecedi

            # Generisanje tripleta kombinacijom 3 note
            for triplet in itertools.combinations(sorted_base_notes, 3):
                triplets.append(triplet)

    # Brojanje frekvencije svakog tripleta
    triplet_counts = Counter(triplets)

    # Vraćanje top 1 tripleta (najčešći)
    top_triplet = triplet_counts.most_common(5)

    return top_triplet

def visualize_top_notes_and_perfumes(most_common_notes, perfumes_info):
    # Vizualizacija najzastupljenijih nota (bar chart)
    notes, counts = zip(*most_common_notes)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(counts), y=list(notes), palette='viridis')
    plt.title('Top 10 najzastupljenijih nota u top 5 parfema za noć')
    plt.xlabel('Broj pojava')
    plt.ylabel('Note')
    plt.show()

    # Vizualizacija top 5 parfema sa njihovim rejtingom i brojem ocena (bar chart)
    perfumes, brands, ratings, votes = zip(*perfumes_info)

    fig, ax = plt.subplots(1, 2, figsize=(16, 6))

    # Bar chart za rejtinge parfema
    sns.barplot(x=perfumes, y=ratings, ax=ax[0], palette='Blues')
    ax[0].set_title('Rejting top 5 parfema')
    ax[0].set_ylabel('Rejting')
    ax[0].set_xticklabels(perfumes, rotation=45, ha='right')

    # Bar chart za broj ocena
    sns.barplot(x=perfumes, y=votes, ax=ax[1], palette='Oranges')
    ax[1].set_title('Broj ocena top 5 parfema')
    ax[1].set_ylabel('Broj ocena')
    ax[1].set_xticklabels(perfumes, rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

def visualize_summer_perfumes_below_rating(data):
    # Pozivanje funkcije koja vraća procenat parfema sa ocenama ispod 4.0
    below_rating_percentage = summer_perfumes_below_rating(data)
    above_rating_percentage = 100 - below_rating_percentage
    
    # Prikazivanje pie chart-a
    labels = ['Ispod 4.0', '4.0 i više']
    sizes = [below_rating_percentage, above_rating_percentage]
    colors = ['#ff9999','#66b3ff']  # Prilagođene boje za pie chart
    
    plt.figure(figsize=(7, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title("Procenat letnjih parfema sa ocenama ispod 4.0")
    plt.axis('equal')  # Da bi pie chart bio u obliku kruga
    plt.show()

def visualize_winter_perfumes_accords_notes(data):
    # Pozivanje funkcije koja vraća najčešće akorde i note
    accords, notes = winter_perfumes_accords_notes(data)
    
    # Prvo, dobijamo podatke o akordima i notama
    accord_labels, accord_counts = zip(*accords)
    note_labels, note_counts = zip(*notes)
    
    # Kombinovani bar chart
    # Kreiramo sve etikete u jednu listu, akorde i note
    all_labels = list(accord_labels) + list(note_labels)
    all_counts = list(accord_counts) + list(note_counts)
    
    # Za grupisani prikaz, trebate podešavati širinu barova
    width = 0.4
    x_pos = np.arange(len(all_labels))  # Pozicije za barove
    
    # Stvaramo boje za akorde i note
    accord_colors = ['#FFCC99'] * len(accord_labels)
    note_colors = ['#66B3FF'] * len(note_labels)
    
    # Prvi bar za akorde
    plt.barh(x_pos[:len(accord_labels)], accord_counts, color=accord_colors, height=width, label='Akordi')
    # Drugi bar za note
    plt.barh(x_pos[len(accord_labels):], note_counts, color=note_colors, height=width, label='Note')
    
    # Dodavanje naslova i oznaka
    plt.title("Najčešći akordi i note u parfemima preporučenim za zimu")
    plt.xlabel("Broj pojavljivanja")
    plt.ylabel("Akordi i Note")
    plt.yticks(x_pos, all_labels)  # Prikazujemo sve etikete (akorde i note)
    
    # Dodavanje legende
    plt.legend()
    
    # Prikazivanje grafikona
    plt.show()
# Pozivanje funkcije
def plot_pie_chart(house_percentages):
    # Podaci za pie chart
    labels = list(house_percentages.keys())
    sizes = list(house_percentages.values())

    # Pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
    plt.title('Procenat učešća parfemskih kuća u top 20 parfema')
    plt.axis('equal')  # Osigurava da je pie chart kružni
    plt.show()
import matplotlib.pyplot as plt

def plot_season_pie_chart(season_counts):
    # Ekstrakcija sezona i njihovih brojeva
    labels = [item[0] for item in season_counts]
    sizes = [item[1] for item in season_counts]

    # Pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Učešće sezona u top parfemima')
    plt.axis('equal')  # Osigurava kružni oblik pie chart-a
    plt.show()
def visualize_top_perfumers(top_perfumers_data, perfumer_votes):
    # Prikupljanje imena, ponderisanih ocena i broja glasova
    perfumers = [perfumer for perfumer, _ in top_perfumers_data]
    scores = [score for _, score in top_perfumers_data]
    votes = [perfumer_votes[perfumer] for perfumer in perfumers]

    # Kreiranje figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Horizontalni bar chart
    ax.barh(perfumers, scores, color='skyblue')

    # Dodavanje broja glasova kao oznaku
    for i, (vote, score) in enumerate(zip(votes, scores)):
        ax.text(score + 0.01, i, f'{vote:,}', va='center', ha='left', color='black', fontsize=10)

    # Dodavanje naslova i etiketa
    ax.set_xlabel('Ponderisana Ocena')
    ax.set_title('Top 5 Parfumeri sa Ponderisanim Ocenama i Brojem Glasova')
    ax.set_xlim(0, max(scores) + 0.5)  # Povećavamo opseg kako bi broj glasova stao sa strane

    plt.tight_layout()
    plt.show()
def plot_most_common_triplets(top_triplet):
    # Preuzimanje tripleta i njihovih frekvencija
    triplets, counts = zip(*top_triplet)

    # Pretvaranje tripleta u string za bolji prikaz
    triplets_str = [' & '.join(triplet) for triplet in triplets]

    # Kreiranje bar grafikona sa vertikalnim stubovima
    plt.figure(figsize=(12, 8))  # Povecavamo dimenzije grafikona za bolji pregled
    sns.barplot(x=triplets_str, y=counts, palette='viridis', width=0.5)  # Smanjujemo širinu stubova

    plt.xlabel('Tripleti', fontsize=14)
    plt.ylabel('Frekvencija', fontsize=14)
    plt.title('Top 5 Najčešće Kombinacije Base Notes', fontsize=16)

    # Rotiramo oznake na x-osi za 45 stepeni i povećavamo razmak između oznaka
    plt.xticks(rotation=45, ha='right', fontsize=12)

    # Povećavamo razmak između stubova i automatski prilagođavamo raspored
    plt.tight_layout()

    plt.show()



# Primer poziva:
# results = most_recommended_season(data)
# plot_season_pie_chart(results['season_counts'])


# Rezultati

#print("UPIT 1")
#print("")
#most_common_notes, perfumes_info = top_notes_night_perfumes(data)
#print("Najzastupljenije note u top 5 parfema za noć:", most_common_notes)
'''
print("\nTop 5 parfema sa brendovima i nazivima:")
for perfume, brand, rating, votes in perfumes_info:
    print(f"Brend: {brand}, Naziv: {perfume}, Rejting: {rating}, Broj ocena: {votes}")
visualize_top_notes_and_perfumes(most_common_notes, perfumes_info)

print("UPIT 2")
print("")
print("Procenat parfema za leto ispod ocene 4.0:", summer_perfumes_below_rating(data))
visualize_summer_perfumes_below_rating(data)
'''

#print("UPIT 3")
#print("")
#print("Najčešći akordi i note za zimu:", winter_perfumes_accords_notes(data))
#visualize_winter_perfumes_accords_notes(data)

#print("UPIT 4")
#print("")
#results = top_perfume_houses(data)
#print("Procenat parfemskih kuća za top 20 parfema:", results)
#plot_pie_chart(results['house_percentages'])

#print("UPIT 5")
#print("")
#results = most_recommended_season(data)
#print("Najčešće preporučena sezona za parfeme 4.5+:", results)
#plot_season_pie_chart(results['season_counts'])

#print("UPIT 6")
#print("")
#top_perfumers_data, perfumer_votes = top_perfumers(data, min_votes=90000)  # Dobijamo top 5 parfumeri i perfumer_votes, PAZNJA MOZE SE MENJATI MIN VOTES
# Primer poziva funkcije
#visualize_top_perfumers(top_perfumers_data, perfumer_votes)

print("UPIT 7")
print("")
top_triplet = most_common_note_combinations(data)
print("Najčešća kombinacija 3 note za parfeme 3.5+ i 5000 recenzija:", top_triplet)
plot_most_common_triplets(top_triplet)