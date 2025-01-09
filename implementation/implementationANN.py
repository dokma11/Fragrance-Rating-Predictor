import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dense, Flatten, Concatenate
from tensorflow.keras.optimizers import Adam
import re
from ast import literal_eval
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load and preprocess data
def parse_season_ratings(rating_str):
    pattern = r'([A-Za-z]+):\s*([0-9.]+)%'
    return {season: float(percent) for season, percent in re.findall(pattern, rating_str)}

def consolidate_notes(notes):
    all_notes = []
    for note_type in ['Top Notes', 'Middle Notes', 'Base Notes']:
        if note_type in notes:
            all_notes.extend(notes[note_type])
    return all_notes

file_path = "../datasets/mainDataset.csv"  # Change this path to your actual file path
data = pd.read_csv(file_path, delimiter='|')

# Process data columns
data['Accords'] = data['Accords'].apply(literal_eval)
data['Notes'] = data['Notes'].apply(literal_eval)
data['Votes'] = data['Rating'].apply(lambda x: literal_eval(x)['votes'])
data['Rating'] = data['Rating'].apply(lambda x: literal_eval(x)['rating'])
data['Season ratings'] = data['Season ratings'].apply(parse_season_ratings)
data['Day ratings'] = data['Day ratings'].apply(parse_season_ratings)
data['Designers'] = data['Designers'].apply(literal_eval)

# Prepare records
records = []
for _, row in data.iterrows():
    record = {
        "Brand": row["Brand"],
        "Gender": row["Gender"],
        "Longevity": row["Longevity"],
        "Sillage": row["Sillage"],
        "Rating": row["Rating"],
        "Votes": row["Votes"],
        "Season_Winter": row["Season ratings"].get("Winter", 0),
        "Season_Spring": row["Season ratings"].get("Spring", 0),
        "Season_Summer": row["Season ratings"].get("Summer", 0),
        "Season_Fall": row["Season ratings"].get("Fall", 0),
        "Day": row["Day ratings"].get("Day", 0),
        "Night": row["Day ratings"].get("Night", 0)
    }
    records.append(record)

structured_df = pd.DataFrame(records)
structured_df['All Notes'] = data['Notes'].apply(consolidate_notes)

# Encode notes for embedding
all_unique_notes = list(set(note for notes in structured_df['All Notes'] for note in notes))
note_to_id = {note: idx for idx, note in enumerate(all_unique_notes)}
structured_df['Note_IDs'] = structured_df['All Notes'].apply(lambda notes: [note_to_id[note] for note in notes if note in note_to_id])
max_len = 10  # Adjust this based on note length distribution
structured_df['Note_IDs_Padded'] = pad_sequences(structured_df['Note_IDs'], maxlen=max_len, padding='post').tolist()

# Encoding categorical features
label_encoder = LabelEncoder()
structured_df['Gender'] = label_encoder.fit_transform(structured_df['Gender'])
structured_df['Brand'] = label_encoder.fit_transform(structured_df['Brand'])

# Prepare data for ANN model
X = structured_df.drop(columns=['Rating', 'All Notes', 'Note_IDs', 'Note_IDs_Padded'])
y = structured_df['Rating']
X_notes = np.array(structured_df['Note_IDs_Padded'].tolist())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train_notes, X_test_notes = train_test_split(X_notes, test_size=0.2, random_state=42)

# ANN with embedding
note_input = Input(shape=(max_len,))
note_embedding = Embedding(input_dim=len(all_unique_notes), output_dim=32)(note_input)#output_dim je bio 16, deloalo je kao da ssto vise to bolje, ali ne kad sam stavila na 48 bio je krs
note_flattened = Flatten()(note_embedding)

structured_input = Input(shape=(X_train.shape[1],))
concatenated = Concatenate()([structured_input, note_flattened])

dense_1 = Dense(128, activation='relu')(concatenated)
dense_2 = Dense(64, activation='relu')(dense_1)
output = Dense(1)(dense_2)

ann_model = Model(inputs=[structured_input, note_input], outputs=output)
ann_model.compile(optimizer=Adam(learning_rate=0.005), loss='mse', metrics=['mae'])#learning rate bio 0.001, nisam primetila neki pattern

# Train the model
ann_model.fit([X_train, X_train_notes], y_train, epochs=200, batch_size=32, verbose=0)#povecala sam epohe sa 50 na 100 i bilo je bolje, sto vise to bolje, bar je tako u par pokusaja bilo, ali duze traje

# Evaluate the model
ann_loss, ann_mae = ann_model.evaluate([X_test, X_test_notes], y_test, verbose=0)
ann_predictions = ann_model.predict([X_test, X_test_notes]).flatten()
ann_rmse = np.sqrt(mean_squared_error(y_test, ann_predictions))

# Print ANN results
print(f"ANN Mean Absolute Error (MAE): {ann_mae}")
print(f"ANN Root Mean Squared Error (RMSE): {ann_rmse}")
