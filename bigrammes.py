import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

with open("petit.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = nlp(text)

tokens = []

for token in doc:
    if not token.is_space and not token.is_punct:
        tokens.append(token.text.lower())

bigrams = []

for t1, t2 in zip(tokens[:-1], tokens[1:]): #zip deux listes qui sont décalées
    bigrams.append((t1, t2))

bigram_count = Counter(bigrams)
unigram_count = Counter(tokens)

bigram_probs = {}

for (t1, t2), count in bigram_count.items():
    bigram_probs[(t1, t2)] = count / unigram_count[t1] # compte combien de fois il y a une suite de mot et divise par le nbr de mot tot

# for (t1, t2), prob in list(bigram_probs.items())[:600]:
    # print(f"P({t2} | {t1}) = {prob:.4f}")

def generate_answer(question, bigram_probs, max_length=25):
    doc = nlp(question.lower())
    question_tokens = [token.text for token in doc if not token.is_space and not token.is_punct]

    current_word = question_tokens[-1]

    response = []

    for i in range(max_length):
        candidates = {t2: prob for (t1, t2), prob in bigram_probs.items() if t1 == current_word}

        if not candidates:
            break

        next_word = max(candidates, key=candidates.get)

        response.append(next_word)
        current_word = next_word

    return " ".join(response)


question = input("question:")
answer = generate_answer(question, bigram_probs)
print(answer)