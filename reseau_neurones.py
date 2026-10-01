import torch
import pickle
import os
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from collections import Counter
import time

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device utilisé :", device)

context_size = 2
embedding_dim = 32
nombre_neurone = 128


class modele(nn.Module):
    def __init__(self, context_size, vocab_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.linear1 = nn.Linear(context_size * embedding_dim, nombre_neurone)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(nombre_neurone, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        x = torch.flatten(x, start_dim=1)
        x = self.linear1(x)
        x = self.relu(x)
        x = self.linear2(x)
        return x


if os.path.exists("modele") and os.path.exists("vocab.pkl"):
    with open("vocab.pkl", "rb") as f:
        word_to_n, n_to_word = pickle.load(f)
    unk_index = word_to_n["<unknown>"]
    vocab_size = len(word_to_n)
    reseau = modele(context_size, vocab_size)
    reseau.load_state_dict(torch.load("modele"))
    reseau = reseau.to(device)
    reseau.eval()

else:
    with open("tokens.pkl", "rb") as f:
        tokens = pickle.load(f)
    print("nombre de tokens :", len(tokens))
    print("taille du vocabulaire :", len(set(tokens)))

    count = Counter(tokens)
    frequence_min = 50

    vocab = sorted(w for w, c in count.items() if c >= frequence_min)
    vocab = ["<unknown>"] + vocab
    word_to_n = {word: n for n, word in enumerate(vocab)}
    n_to_word = {n: word for word, n in word_to_n.items()}

    unk_index = word_to_n["<unknown>"]

    def get_index(word):
        return word_to_n.get(word, unk_index)

    entree = []
    sortie = []

    for i in range(len(tokens) - context_size):
        context = tokens[i : i + context_size]
        target = tokens[i + context_size]
        entree.append(context)
        sortie.append(target)

    debut = time.time()
    entree_numbers = []
    sortie_numbers = []

    for context, target in zip(entree, sortie):
        context_numbers = [get_index(word) for word in context]
        target_number = get_index(target)
        entree_numbers.append(context_numbers)
        sortie_numbers.append(target_number)

    tensor_entree = torch.tensor(entree_numbers, dtype=torch.long)
    tensor_sortie = torch.tensor(sortie_numbers, dtype=torch.long)
    print(f"préparation des données : {time.time() - debut:.1f} secondes")

    dataset = TensorDataset(tensor_entree, tensor_sortie)
    loader = DataLoader(dataset, batch_size=512, shuffle=True)

    reseau = modele(context_size, len(vocab))
    reseau = reseau.to(device)
    optimizer = torch.optim.Adam(reseau.parameters(), lr=0.0005)
    loss_function = nn.CrossEntropyLoss()

    for i in range(15):
        for x_batch, y_batch in loader:
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)
            prediction = reseau(x_batch)
            loss = loss_function(prediction, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"epoch {i} — loss : {loss.item():.4f}")

    torch.save(reseau.state_dict(), "modele")
    with open("vocab.pkl", "wb") as f:
        pickle.dump((word_to_n, n_to_word), f)

    prediction = reseau(tensor_entree[:5].to(device))
    for i in range(5):
        mot_predit = torch.argmax(prediction[i]).item()
        mot_reel = tensor_sortie[i].item()
        print("réel :", n_to_word[mot_reel])
        print("prédit :", n_to_word[mot_predit])
def generate_answer(mot1, mot2, longueur=25):
    contexte = [get_index_safe(mot1), get_index_safe(mot2)]
    resultat = [mot1, mot2]

    for _ in range(longueur - 2):
        x = torch.tensor([contexte], dtype=torch.long).to(device)
        prediction = reseau(x)
        prediction[0][unk_index] = float("-inf")
        probs = F.softmax(prediction[0], dim=0)
        mot_predit_index = torch.multinomial(probs, num_samples=1).item()
        mot_predit = n_to_word[mot_predit_index]

        resultat.append(mot_predit)
        contexte = [contexte[1], mot_predit_index]

    return " ".join(resultat)


def get_index_safe(word):
    return word_to_n.get(word, word_to_n["<unknown>"])


while True:
    question = input("Question : ")
    if question.lower() == "quit":
        break

    mots = question.lower().split()
    if len(mots) < context_size:
        print(f"Il faut au moins {context_size} mots.")
        continue

    phrase = generate_answer(mots[-2], mots[-1])
    print(phrase)