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

def suggest_similar_ngram(ngram, ngram_freqs):
    """Funkcja do sugerowania podobnych bigramów/trigramów na podstawie edytowania Levenshteina"""
    suggestions = []
    for existing_ngram in ngram_freqs:
        # Oblicz odległość Levenshteina dla podobnych bigramów i trigramów
        if edit_distance(' '.join(ngram), ' '.join(existing_ngram)) <= 2:
            suggestions.append((existing_ngram, ngram_freqs[existing_ngram]))
    
    # Sortowanie sugestii po częstotliwości, aby wybrać te najbardziej prawdopodobne
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return suggestions

def correct_sentence(sentence, bigram_freqs, trigram_freqs):
    words = word_tokenize(sentence.lower())
    corrected_sentence = [words[0]]  # Add the first word
    print(f"Poprawianie zdania: {sentence}")  # Debug: Display sentence to be corrected

    for i in range(len(words) - 1):
        bigram = (words[i], words[i + 1])
        trigram = (words[i], words[i + 1], words[i + 2] if i + 2 < len(words) else '')  # Fix for trigrams

        print(f"\nAnalizowanie słowa '{words[i]}':")  # Debug: Analyze current word

        # If bigram is not in the data, check if trigram is available
        if bigram not in bigram_freqs and trigram in trigram_freqs:
            # Find the most probable word based on trigram
            suggestions = [ngram for ngram in trigram_freqs if ngram[0] == words[i] and ngram[1] == words[i + 1]]
            if suggestions:
                # Select the trigram with the highest frequency
                best_match = max(suggestions, key=lambda x: trigram_freqs[x])
                print(f"Używam trigramu: {best_match} z częstotliwością {trigram_freqs[best_match]}")  # Debug
                corrected_sentence.append(best_match[2])  # Add the word from the trigram
            else:
                # If no suggestions, try to suggest similar trigrams
                similar_trigrams = suggest_similar_ngram((words[i], words[i + 1]), trigram_freqs)
                print(f"Brak sugestii w trigramach dla '{words[i]} {words[i+1]}'. Sugerowane podobne trigramy: {similar_trigrams}")
                if similar_trigrams:
                    corrected_sentence.append(sorted(similar_trigrams, key=lambda x: x[1], reverse=True)[0][0][2])
                else:
                    corrected_sentence.append(words[i + 1])  # Fallback: Use the original word
        elif bigram in bigram_freqs:
            # If bigram exists in the data, append the second word
            print(f"Używam bigramu: {bigram} z częstotliwością {bigram_freqs[bigram]}")  # Debug
            corrected_sentence.append(words[i + 1])
        else:
            # If bigram doesn't exist, try to find similar bigrams
            print(f"Brak bigramu '{bigram}' w danych. Sugerowane podobne bigramy: {suggest_similar_ngram(bigram, bigram_freqs)}")
            suggestions = suggest_similar_ngram(bigram, bigram_freqs)
            if suggestions:
                corrected_sentence.append(sorted(suggestions, key=lambda x: x[1], reverse=True)[0][0][1])
            else:
                corrected_sentence.append(words[i + 1])  # Fallback: Use the original word

    # Additional spelling correction
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
    
    test_sentence = "I hace a prettty house"
    corrected = correct_sentence(test_sentence, bigram_freqs, trigram_freqs)
    
    print(f"\nPoprawione zdanie: {corrected}")
