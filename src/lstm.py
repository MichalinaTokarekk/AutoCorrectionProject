import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from tensorflow.keras.preprocessing.text import Tokenizer

# Wczytanie danych
misspelled_data = pd.read_csv("data/misspelled.csv")
print(misspelled_data.columns)

words_data = pd.read_csv("data/words.csv")

# Zbieranie danych z pliku misspelled.csv
misspelled_words = misspelled_data['błędne słowo'].values
correct_words = misspelled_data['poprawne słowo'].values

# Przygotowanie danych wejściowych i wyjściowych
input_data = []
output_data = []

# Dla każdego błędnego słowa dodajemy poprawne słowo do zestawu danych
for misspelled, correct in zip(misspelled_words, correct_words):
    input_data.append(misspelled)
    output_data.append(correct)

# Tokenizacja słów i stworzenie słownika
tokenizer = Tokenizer()
tokenizer.fit_on_texts(words_data['words'].values)

# Przekształcenie słów na sekwencje
input_sequences = tokenizer.texts_to_sequences(input_data)
output_sequences = tokenizer.texts_to_sequences(output_data)

# Padding sekwencji do tej samej długości
max_sequence_length = max([len(seq) for seq in input_sequences])
input_data_padded = pad_sequences(input_sequences, maxlen=max_sequence_length, padding='post')
output_data_padded = pad_sequences(output_sequences, maxlen=max_sequence_length, padding='post')

# One-hot encoding dla danych wyjściowych
output_data_padded = to_categorical(output_data_padded, num_classes=len(tokenizer.word_index)+1)

# Budowanie modelu LSTM
model = Sequential()
model.add(Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=128, input_length=max_sequence_length))
model.add(LSTM(128, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(128))
model.add(Dense(len(tokenizer.word_index)+1, activation='softmax'))

# Kompilowanie modelu
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Trenowanie modelu
model.fit(input_data_padded, output_data_padded, epochs=10, batch_size=64, validation_split=0.2)

# Funkcja do przewidywania poprawnego słowa na podstawie błędnego
def correct_word(misspelled_word):
    seq = tokenizer.texts_to_sequences([misspelled_word])
    padded_seq = pad_sequences(seq, maxlen=max_sequence_length, padding='post')
    prediction = model.predict(padded_seq)
    predicted_word = tokenizer.sequences_to_texts(np.argmax(prediction, axis=-1))
    return predicted_word[0]

# Testowanie modelu
test_word = "błędne_słowo"
predicted = correct_word(test_word)
print(f'Poprawna wersja słowa "{test_word}" to: {predicted}')
