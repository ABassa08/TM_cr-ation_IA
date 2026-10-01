import spacy
import random
from collections import Counter

nlp = spacy.load("en_core_web_sm")

with open("petit.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = nlp(text)
tokens = []

for token in doc:
    if not token.is_space and not token.is_punct:
        tokens.append(token.text.lower())

unigram_count = Counter(tokens)
total_mots = len(tokens)

unigram_probs = {}

for t1, count in unigram_count.items():
    unigram_probs[t1] = count / total_mots


mots = list(unigram_probs.keys())
poids = list(unigram_probs.values())

sentence = random.choices(mots, weights=poids, k=25)
print(" ".join(sentence))