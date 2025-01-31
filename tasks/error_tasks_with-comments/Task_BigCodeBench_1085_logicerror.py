import re
from collections import Counter
from string import punctuation
import matplotlib.pyplot as plt

def task_func(text):
    cleaned_text = re.sub(f"[{punctuation}]", "", text).lower()
    words = cleaned_text.split()
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(10)
    _, ax = plt.subplots()
    if most_common_words: 
        ax.bar(*zip(*most_common_words))
    else: 
        ax.bar([], [])
    most_common_words = word_counts.most_common(5) # Fehler: Überschreibt die Variable most_common_words mit einem anderen Wert
    return most_common_words, ax

# Position des Fehlers: Zeile 16
# Subkategorie des Fehlers: Falsche Variable