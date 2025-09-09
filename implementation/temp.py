import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dense, Flatten, Concatenate, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.preprocessing.sequence import pad_sequences
from ast import literal_eval
import re

# --------- Helper functions ---------
def parse_season_ratings(rating_str):
    pattern = r'([A-Za-z]+):\s*([0-9.]+)%'
    return {season: float(percent) for season, percent in re.findall(pattern, rating_str)}

def consolidate_notes(notes):
    all_notes = []
    for note_type in ['Top Notes', 'Middle Notes', 'Base Notes']:
        if note_type in notes:
            all_notes.extend(notes[note_type])
    return all_notes

def extract_top_notes(x):
    if isinstance(x, dict):
        return x.get('Top Notes', [])
    elif isinstance(x, list):
        return []
    else:
        return []

def extract_middle_notes(x):
    if isinstance(x, dict):
        return x.get('Middle Notes', [])
    elif isinstance(x, list):
        return []
    else:
        return []

def extract_base_notes(x):
    if isinstance(x, dict):
        return x.get('Base Notes', [])
    elif isinstance(x, list):
        return x  # If notes are a list, put all in base
    else:
        return []

# --------- Load dataset ---------
file_path = "datasets/mainDataset.csv"
data = pd.read_csv(file_path, delimiter='|')

data['Accords'] = data['Accords'].apply(literal_eval)
data['Notes'] = data['Notes'].apply(literal_eval)
data['Votes'] = data['Rating'].apply(lambda x: literal_eval(x)['votes'])
data['Rating'] = data['Rating'].apply(lambda x: literal_eval(x)['rating'])
data['Season ratings'] = data['Season ratings'].apply(parse_season_ratings)
data['Day ratings'] = data['Day ratings'].apply(parse_season_ratings)
data['Designers'] = data['Designers'].apply(literal_eval)

# --------- Structured dataframe ---------
records = []
for _, row in data.iterrows():
    record = {
        "Brand": row["Brand"],
        "Gender": row["Gender"],
        "Longevity": row["Longevity"],
        "Sillage": row["Sillage"],
        "Votes": row["Votes"],
        "Rating": row["Rating"],
        "Season_Winter": row["Season ratings"].get("Winter", 0),
        "Season_Spring": row["Season ratings"].get("Spring", 0),
        "Season_Summer": row["Season ratings"].get("Summer", 0),
        "Season_Fall": row["Season ratings"].get("Fall", 0),
        "Day": row["Day ratings"].get("Day", 0),
        "Night": row["Day ratings"].get("Night", 0)
    }
    records.append(record)

structured_df = pd.DataFrame(records)
structured_df['Top_Notes'] = data['Notes'].apply(extract_top_notes)
structured_df['Middle_Notes'] = data['Notes'].apply(extract_middle_notes)
structured_df['Base_Notes'] = data['Notes'].apply(extract_base_notes)

# --------- Encode notes for embedding ---------
# Create note-to-id mappings for each type
all_top_notes = list(set(note for notes in structured_df['Top_Notes'] for note in notes))
all_middle_notes = list(set(note for notes in structured_df['Middle_Notes'] for note in notes))
all_base_notes = list(set(note for notes in structured_df['Base_Notes'] for note in notes))

top_note_to_id = {note: idx for idx, note in enumerate(all_top_notes)}
middle_note_to_id = {note: idx for idx, note in enumerate(all_middle_notes)}
base_note_to_id = {note: idx for idx, note in enumerate(all_base_notes)}

max_len = 30
structured_df['Top_IDs'] = structured_df['Top_Notes'].apply(lambda notes: [top_note_to_id[note] for note in notes if note in top_note_to_id])
structured_df['Middle_IDs'] = structured_df['Middle_Notes'].apply(lambda notes: [middle_note_to_id[note] for note in notes if note in middle_note_to_id])
structured_df['Base_IDs'] = structured_df['Base_Notes'].apply(lambda notes: [base_note_to_id[note] for note in notes if note in base_note_to_id])

X_top = np.array(pad_sequences(structured_df['Top_IDs'], maxlen=max_len, padding='post').tolist())
X_middle = np.array(pad_sequences(structured_df['Middle_IDs'], maxlen=max_len, padding='post').tolist())
X_base = np.array(pad_sequences(structured_df['Base_IDs'], maxlen=max_len, padding='post').tolist())

# --------- Encode categorical features ---------
label_encoder = LabelEncoder()
structured_df['Gender'] = label_encoder.fit_transform(structured_df['Gender'])
structured_df['Brand'] = label_encoder.fit_transform(structured_df['Brand'])

# --------- Prepare structured features ---------
X_structured = structured_df.drop(columns=[
    'Rating', 'Top_Notes', 'Middle_Notes', 'Base_Notes', 'Top_IDs', 'Middle_IDs', 'Base_IDs'
])
y = structured_df['Rating'].values.astype(np.float32)

# Scale numerical columns
num_cols = ['Longevity','Sillage','Votes','Season_Winter','Season_Spring','Season_Summer','Season_Fall','Day','Night']
scaler = StandardScaler()
X_structured[num_cols] = scaler.fit_transform(X_structured[num_cols])

# --------- Train-test split ---------
# Train-test split for all inputs
X_train_struct, X_test_struct, y_train, y_test, X_train_top, X_test_top, X_train_middle, X_test_middle, X_train_base, X_test_base = train_test_split(
    X_structured, y, X_top, X_middle, X_base, test_size=0.2, random_state=42
)

# --------- ANN with embedding ---------

# Inputs for structured and note types
structured_input = Input(shape=(X_train_struct.shape[1],), name='Structured_Input')
top_input = Input(shape=(max_len,), name='Top_Input')
middle_input = Input(shape=(max_len,), name='Middle_Input')
base_input = Input(shape=(max_len,), name='Base_Input')

# Embeddings for each note type
top_emb = Embedding(input_dim=len(all_top_notes)+1, output_dim=16, mask_zero=True)(top_input)
top_emb_flat = Flatten()(top_emb)
middle_emb = Embedding(input_dim=len(all_middle_notes)+1, output_dim=16, mask_zero=True)(middle_input)
middle_emb_flat = Flatten()(middle_emb)
base_emb = Embedding(input_dim=len(all_base_notes)+1, output_dim=16, mask_zero=True)(base_input)
base_emb_flat = Flatten()(base_emb)

# Concatenate all features
concat = Concatenate()([structured_input, top_emb_flat, middle_emb_flat, base_emb_flat])

x = Dense(128, activation='relu')(concat)
x = BatchNormalization()(x)
x = Dropout(0.2)(x)
x = Dense(64, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.1)(x)
output = Dense(1, activation='linear')(x)

model = Model(inputs=[structured_input, top_input, middle_input, base_input], outputs=output)
model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

# Learning rate scheduler
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=1e-5, verbose=1)

# Train
# Train
history = model.fit(
    [X_train_struct, X_train_top, X_train_middle, X_train_base], y_train,
    validation_split=0.2,
    epochs=300,
    batch_size=32,
    callbacks=[reduce_lr],
    verbose=1
)

# Evaluate
loss, mae = model.evaluate([X_test_struct, X_test_top, X_test_middle, X_test_base], y_test)
preds = model.predict([X_test_struct, X_test_top, X_test_middle, X_test_base]).flatten()
rmse = np.sqrt(mean_squared_error(y_test, preds))

print(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}")