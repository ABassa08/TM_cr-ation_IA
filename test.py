import pickle
with open("tokens.pkl", "rb") as f:
    tokens = pickle.load(f)
print("nombre de tokens :", len(tokens))
print("taille du vocabulaire :", len(set(tokens)))
from collections import Counter

counts = Counter(tokens)
min_freq = 100

vocab = sorted(w for w, c in counts.items() if c >= min_freq)
vocab = ["<UNK>"] + vocab

print("taille du vocabulaire après filtrage :", len(vocab))