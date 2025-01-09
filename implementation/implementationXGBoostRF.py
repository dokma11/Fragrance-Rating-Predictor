import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Dense, Flatten, Concatenate
from tensorflow.keras.models import Model
from sklearn.metrics import mean_absolute_error, mean_squared_error
import re
from ast import literal_eval

# Funkcija za parsiranje sezonskih i dnevnih ocena
def parse_season_ratings(rating_str):
    pattern = r'([A-Za-z]+):\s*([0-9.]+)%'
    return {season: float(percent) for season, percent in re.findall(pattern, rating_str)}

# Funkcija koja spaja sve note u jednu listu
def consolidate_notes(notes):
    all_notes = []
    for note_type in ['Top Notes', 'Middle Notes', 'Base Notes']:
        if note_type in notes:  # Proverava da li postoji ta kategorija
            all_notes.extend(notes[note_type])
    return all_notes

# Učitavanje podataka iz CSV fajla
file_path = "../datasets/mainDataset.csv"
data = pd.read_csv(file_path, delimiter='|')

# Pretvaranje stringova u liste i rečnike gde je potrebno
data['Accords'] = data['Accords'].apply(literal_eval)
data['Notes'] = data['Notes'].apply(literal_eval)
data['Votes'] = data['Rating'].apply(lambda x: literal_eval(x)['votes'])
data['Rating'] = data['Rating'].apply(lambda x: literal_eval(x)['rating'])
data['Season ratings'] = data['Season ratings'].apply(parse_season_ratings)
data['Day ratings'] = data['Day ratings'].apply(parse_season_ratings)
data['Designers'] = data['Designers'].apply(literal_eval)

# Priprema podataka za modele
records = []
for _, row in data.iterrows():
    record = {
        "Brand": row["Brand"],
        "Gender": row["Gender"],
        "Longevity": row["Longevity"],
        "Sillage": row["Sillage"],
        "Rating": row["Rating"],
        "Votes" : row["Votes"],
        "Season_Winter": row["Season ratings"].get("Winter", 0),
        "Season_Spring": row["Season ratings"].get("Spring", 0),
        "Season_Summer": row["Season ratings"].get("Summer", 0),
        "Season_Fall": row["Season ratings"].get("Fall", 0),
        "Day": row["Day ratings"].get("Day", 0),
        "Night": row["Day ratings"].get("Night", 0)
    }
    records.append(record)
#print(records[0])

# Kreiranje DataFrame-a
structured_df = pd.DataFrame(records)
structured_df = structured_df.fillna(0)
structured_df['All Notes'] = data['Notes'].apply(consolidate_notes)

# Lista svih unikatnih nota
all_unique_notes = set()
for notes in structured_df['All Notes']:
    all_unique_notes.update(notes)

# One-Hot Encoding za Brand, Gender i All Notes
ohe = OneHotEncoder(sparse_output=False)
ohe_features = pd.DataFrame(ohe.fit_transform(structured_df[['Brand', 'Gender']]),
                            columns=ohe.get_feature_names_out(['Brand', 'Gender']))

# Collect the binary columns for all unique notes
note_columns = []

for note in all_unique_notes:
    note_columns.append(structured_df['All Notes'].apply(lambda x: 1 if note in x else 0))

# Create a DataFrame from the note columns
note_df = pd.DataFrame(note_columns).T  # Transpose to get notes as columns

# Add column names for each note
note_df.columns = [f'Note_{note}' for note in all_unique_notes]

# Concatenate the note columns with the existing structured_df
structured_df = pd.concat([structured_df, note_df], axis=1)

X = pd.concat([ohe_features, structured_df.drop(columns=['Brand', 'Gender', 'Rating', 'All Notes'])], axis=1)
y = structured_df['Rating']

# Deljenje podataka na trening i test skupove
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Random Forest Regressor
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)

rf_score = rf_model.score(X_test, y_test)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"Random Forest R^2 Score: {rf_score}")
print(f"Random Forest Mean Absolute Error (MAE): {mae}")
print(f"Random Forest Root Mean Squared Error (RMSE): {rmse}")



# XGBoost
# XGBoost Regressor
xgb_model = XGBRegressor(random_state=42)
xgb_model.fit(X_train, y_train)
y_xgb_pred = xgb_model.predict(X_test)

# Evaluation metrics for XGBoost
xgb_r2_score = xgb_model.score(X_test, y_test)
xgb_mae = mean_absolute_error(y_test, y_xgb_pred)
xgb_mse = mean_squared_error(y_test, y_xgb_pred)
xgb_rmse = np.sqrt(xgb_mse)

print(f"XGBoost R^2 Score: {xgb_r2_score}")
print(f"XGBoost Mean Absolute Error (MAE): {xgb_mae}")
print(f"XGBoost Root Mean Squared Error (RMSE): {xgb_rmse}")

