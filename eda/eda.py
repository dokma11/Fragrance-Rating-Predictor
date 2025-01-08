import pandas as pd
from ast import literal_eval
from collections import Counter
from itertools import combinations
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
    filtered = data[data['Rating'].apply(lambda x: x['votes'] > 10000)]
    # Sortiranje po vrednosti ocene
    top_20 = filtered.sort_values(by='Rating', key=lambda x: x.apply(lambda y: y['rating']), ascending=False).head(20)
    
    houses = set(house for designers in top_20['Designers'] for house in designers)
    return len(houses) / len(data['Designers'].explode().unique()) * 100

# Pitanje 5: Која сезона се највише препоручује за парфеме са оценом 4,50 више, који такође имају најмање 5000 рецензија?
def most_recommended_season(data):
    filtered = data[(data['Rating'].apply(lambda x: x['rating'] >= 4.5)) & 
                    (data['Rating'].apply(lambda x: x['votes'] >= 5000))]
    season_counter = Counter()
    for _, row in filtered.iterrows():
        season_counter.update(row['Season ratings'])
    return season_counter.most_common(1)

# Pitanje 6: Ко су 5 најбољих парфимера на основу оцене њихових парфема?
def top_perfumers(data):
    perfumer_scores = Counter()
    perfumer_counts = Counter()
    for _, row in data.iterrows():
        for perfumer in row['Designers']:
            perfumer_scores[perfumer] += row['Rating']['rating']
            perfumer_counts[perfumer] += 1
    avg_scores = {perfumer: perfumer_scores[perfumer] / perfumer_counts[perfumer] for perfumer in perfumer_scores}
    return sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:5]

# Pitanje 7: Која комбинација од 3 ноте је најчешћа међу парфемима са оценом 4,50 и више, који такође имају најмање 5000 рецензија?
def most_common_note_combinations(data):
    filtered = data[(data['Rating'].apply(lambda x: x['rating'] >= 4.5)) & 
                    (data['Rating'].apply(lambda x: x['votes'] >= 5000))]
    note_combinations = Counter()
    for _, row in filtered.iterrows():
        notes = set(note for note_list in row['Notes'].values() for note in note_list)
        note_combinations.update(combinations(notes, 3))
    return note_combinations.most_common(1)

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
'''
print("UPIT 4")
print("")
print("Procenat parfemskih kuća za top 20 parfema:", top_perfume_houses(data))
print("UPIT 5")
print("")
print("Najčešće preporučena sezona za parfeme 4.5+:", most_recommended_season(data))
print("UPIT 6")
print("")
print("Top 5 parfemera:", top_perfumers(data))
print("UPIT 7")
print("")
print("Najčešća kombinacija 3 note za parfeme 4.5+:", most_common_note_combinations(data))'''
