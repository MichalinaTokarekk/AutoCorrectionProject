import csv
import difflib

# Funkcja do załadowania danych z pliku tekstowego
def load_sentences(file_path):
    sentences = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            sentences.append(line.strip())  # Wczytanie zdań z pliku tekstowego
    return sentences

# Funkcja do generowania listy słów z korpusu danych
def generate_word_list(sentences):
    word_list = []
    for sentence in sentences:
        word_list.extend(sentence.split())  # Rozbijamy zdanie na słowa
    return word_list

# Funkcja do znalezienia najbardziej podobnych słów z listy
def suggest_similar_word(word, word_list):
    # Użycie difflib do znalezienia najbardziej podobnego słowa
    similar_words = difflib.get_close_matches(word, word_list, n=5, cutoff=0.6)
    return similar_words

# Funkcja do autokorekty, która sugeruje poprawki w zdaniu
def autocorrect_sentence(input_text, word_list):
    words = input_text.split()  # Dzielimy tekst na słowa
    corrected_text = input_text  # Przypisujemy oryginalne zdanie do zmiennej

    for word in words:
        # Sprawdzamy, czy słowo ma sugestie
        suggestions = suggest_similar_word(word, word_list)
        
        if suggestions:
            print(f"Możliwy błąd w słowie: {word}")
            print(f"Proponowane poprawki: {', '.join(suggestions)}")
            
            # Wybieramy pierwszą sugestię
            corrected_word = suggestions[0]
            corrected_text = corrected_text.replace(word, corrected_word)

    return corrected_text  # Zwracamy poprawione zdanie

# Główna funkcja
def main():
    # Wczytanie zdań z pliku txt
    sentences = load_sentences('data/sentences.txt')
    
    # Generowanie listy słów z wczytanych zdań
    word_list = generate_word_list(sentences)
    
    # Wpisz tutaj swoje zdanie, które ma zostać poprawione
    input_text = "I live in a houde with my godd."  # Przykładowe zdanie, które można edytować
    
    print("Oryginalne zdanie:", input_text)
    
    # Autokorekta
    corrected_sentence = autocorrect_sentence(input_text, word_list)
    
    print("\nPoprawione zdanie:", corrected_sentence)

if __name__ == "__main__":
    main()
