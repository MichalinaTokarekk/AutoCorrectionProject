import re
from collections import Counter
from nltk import word_tokenize
from nltk.util import ngrams
import PyPDF2

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

def correct_sentence(sentence, ngram_freqs):
    words = word_tokenize(sentence.lower())
    corrected_sentence = [words[0]]  # Dodajemy pierwsze słowo

    for i in range(len(words) - 1):
        bigram = (words[i], words[i + 1])
        if bigram not in ngram_freqs:
            # Znajdź najbardziej prawdopodobne następne słowo dla bieżącego
            suggestions = [ngram for ngram in ngram_freqs if ngram[0] == words[i]]
            if suggestions:
                # Wybierz bigram z najwyższą częstotliwością
                best_match = max(suggestions, key=lambda x: ngram_freqs[x])
                print(f"Debug: Suggestions for '{words[i]}': {suggestions}, chosen: {best_match}")
                corrected_sentence.append(best_match[1])
            else:
                # Jeśli brak sugestii, pozostaw oryginalne słowo
                corrected_sentence.append(words[i + 1])
        else:
            # Jeśli bigram istnieje, dodaj drugie słowo
            corrected_sentence.append(words[i + 1])

    return ' '.join(corrected_sentence)


if __name__ == "__main__":
    sentences_text = load_sentences("data/sentences.txt")
    book_text = load_pdf("data/Relic.pdf")
    
    combined_text = sentences_text + ' ' + book_text
    
    bigrams = generate_ngrams(combined_text, n=2)
    bigram_freqs = calculate_ngram_frequencies(bigrams)
    
    test_sentence = "The emd of the world"
    corrected = correct_sentence(test_sentence, bigram_freqs)
    
    print(f"Poprawione zdanie: {corrected}")
