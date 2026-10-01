import spacy
from collections import Counter
import random
import os
import pickle
from collections import defaultdict

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
nlp.max_length = 600_000_000

with open("moyen.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = nlp(text)

tokens = []

for token in doc:
    if not token.is_space and not token.is_punct:
        tokens.append(token.text.lower())
total_mots = len(tokens)
unigram_count = Counter(tokens)
unigram_probs = {}

for t1, count in unigram_count.items():
    unigram_probs[t1] = count / total_mots
bigrams = []

for t1, t2 in zip(tokens[:-1], tokens[1:]): #zip deux listes qui sont décalées
    bigrams.append((t1, t2))

bigram_count = Counter(bigrams)

bigram_probs = {}

for (t1, t2), count in bigram_count.items():
    bigram_probs[(t1, t2)] = count / unigram_count[t1]
trigrams = []
for t1, t2, t3 in zip(tokens[:-2], tokens[1:-1], tokens[2:]): # zip trois listes
    trigrams.append((t1, t2, t3))

trigram_count = Counter(trigrams)

trigram_probs = {}
for (t1, t2, t3), count in trigram_count.items():
    trigram_probs[(t1, t2, t3)] = count / bigram_count[(t1, t2)]



trigram_index = defaultdict(dict)
for (t1, t2, t3), prob in trigram_probs.items():
    trigram_index[(t1, t2)][t3] = prob
bigram_index = defaultdict(dict)
for (t1, t2), prob in bigram_probs.items():
    bigram_index[t1][t2] = prob


def generate_answer(question, max_length=25):
    doc = nlp(question.lower())
    question_tokens = [token.text for token in doc if not token.is_space and not token.is_punct]
    if len(question_tokens) < 2:
        return "Pose une question avec au moins deux mots."
    current_bigram = (question_tokens[-2], question_tokens[-1])

    response = list(current_bigram)


    for i in range(max_length):
        candidates = trigram_index.get(current_bigram, {})
        if candidates:
            next_word = max(candidates, key=candidates.get)
        else:
            last_word = current_bigram[1]
            candidates = bigram_index.get(last_word,{})
            if candidates:
                next_word = max(candidates, key=candidates.get)
            else:
                mots = list(unigram_probs.keys())
                poids = list(unigram_probs.values())
                next_word = random.choices(mots, weights=poids, k=1)[0]

        response.append(next_word)
        current_bigram = (current_bigram[1], next_word)

    return " ".join(response)

while True:
    question = input("Question : ")

    if question.lower() == "quit":
        break
    answer = generate_answer(question)
    print(answer)