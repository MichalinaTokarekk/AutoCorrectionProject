import re
from collections import Counter
from nltk import word_tokenize
from nltk.util import ngrams
import PyPDF2
import nltk
from nltk.corpus import words
from nltk.metrics.distance import edit_distance

# Załaduj słownik poprawnych słów
nltk.download('words')
correct_words = set(words.words())

def load_sentences(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return clean_text(text)

def load_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return clean_text(text)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # Usuń znaki specjalne
    return text

def generate_ngrams(text, n=2):
    tokens = word_tokenize(text)
    return list(ngrams(tokens, n))

def calculate_ngram_frequencies(ngrams_list):
    return Counter(ngrams_list)

def correct_sentence(sentence, bigram_freqs, trigram_freqs):
    words = word_tokenize(sentence.lower())
    corrected_sentence = [words[0]]  # Dodajemy pierwsze słowo

    for i in range(len(words) - 1):
        bigram = (words[i], words[i + 1])
        trigram = (words[i], words[i + 1], words[i + 2] if i + 2 < len(words) else '')  # Poprawka dla trigramów

        # Jeśli bigram istnieje w danych
        if bigram not in bigram_freqs and trigram in trigram_freqs:
            # Znajdź najbardziej prawdopodobne słowo na podstawie trigramu
            suggestions = [ngram for ngram in trigram_freqs if ngram[0] == words[i] and ngram[1] == words[i + 1]]
            if suggestions:
                # Wybierz trigram z najwyższą częstotliwością
                best_match = max(suggestions, key=lambda x: trigram_freqs[x])
                corrected_sentence.append(best_match[2])  # Dodaj słowo z trigramu
            else:
                corrected_sentence.append(words[i + 1])  # Jeśli brak sugestii, dodaj słowo
        else:
            # Jeśli bigram istnieje w danych, dodaj drugie słowo
            corrected_sentence.append(words[i + 1])

    # Dodatkowa funkcja porównania słów
    corrected_sentence = [correct_spelling(word) for word in corrected_sentence]

    return ' '.join(corrected_sentence)

def correct_spelling(word):
    """Funkcja do poprawy pisowni na podstawie porównania z poprawnymi słowami"""
    if word not in correct_words:
        # Znajdź najbardziej podobne słowo (minimum odległości Levenshteina)
        closest_word = min(correct_words, key=lambda w: edit_distance(word, w))
        return closest_word
    return word


if __name__ == "__main__":
    sentences_text = load_sentences("data/sentences2.txt")
    book_text = load_pdf("data/Relic.pdf")
    
    combined_text = sentences_text + ' ' + book_text
    
    bigrams = generate_ngrams(combined_text, n=2)
    bigram_freqs = calculate_ngram_frequencies(bigrams)
    
    trigrams = generate_ngrams(combined_text, n=3)
    trigram_freqs = calculate_ngram_frequencies(trigrams)
    
    test_sentence = "The emd of the worlr"
    corrected = correct_sentence(test_sentence, bigram_freqs, trigram_freqs)
    
    print(f"Poprawione zdanie: {corrected}")
