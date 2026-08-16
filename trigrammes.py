import spacy
from collections import Counter
import requests
from bs4 import BeautifulSoup
import time

headers = {"User-Agent": "Mozilla/5.0"}


def get_titles_from_search(query, limit=50):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'utf8': 1,
        'srsearch': query,
        'srlimit': limit
    }
    data = requests.get(url, params=params, headers=headers).json()
    return [result['title'] for result in data['query']['search']]


def scrape_wikipedia_page(subject, retries=3):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': subject,
        'format': 'json',
        'prop': 'text',
        'redirects': ''
    }

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 429:
            print(f"⏳ Rate limit atteint pour {subject}, pause de 5s (tentative {attempt+1}/{retries})")
            time.sleep(5)
            continue

        try:
            data = response.json()
            break
        except requests.exceptions.JSONDecodeError:
            print(f"⚠️ Erreur JSON pour {subject}, tentative {attempt+1}/{retries}")
            time.sleep(2)
    else:
        print(f"❌ Abandon définitif pour : {subject}")
        return ""

    if 'parse' not in data:
        return ""

    raw_html = data['parse']['text']['*']
    soup = BeautifulSoup(raw_html, 'html.parser')

    text = ""
    for p in soup.find_all('p'):
        text += p.text
    return text


titres = get_titles_from_search("artificial intelligence", limit=50)
print(f"{len(titres)} titres trouvés")

texte_complet = ""
for titre in titres:
    texte_complet += scrape_wikipedia_page(titre) + " "
    time.sleep(2)

with open("text.txt", "w", encoding="utf-8") as f:
    f.write(texte_complet)

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
nlp.max_length = 2_000_000

with open("text.txt", "r", encoding="utf-8") as f:
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

trigrams = []
for t1, t2, t3 in zip(tokens[:-2], tokens[1:-1], tokens[2:]):
    trigrams.append((t1, t2, t3))

trigram_count = Counter(trigrams)

trigram_probs = {}
for (t1, t2, t3), count in trigram_count.items():
    trigram_probs[(t1, t2, t3)] = count / bigram_count[(t1, t2)]

def generate_answer(question, trigram_probs, max_length=100):
    doc = nlp(question.lower())
    question_tokens = [token.text for token in doc if not token.is_space and not token.is_punct]

    current_bigram = (question_tokens[-2], question_tokens[-1])

    response = list(current_bigram)

    for i in range(max_length):
        candidates = {t3: prob for (t1, t2, t3), prob in trigram_probs.items() if (t1, t2) == current_bigram} # regarde tous les trigrammes et ne garde que ceux qui ont les mêmes t1, t2 que ceux de la question et retient le t3

        if not candidates:
            break

        next_word = max(candidates, key=candidates.get)

        response.append(next_word)
        current_bigram = (current_bigram[1], next_word)

    return " ".join(response)

while True:
    question = input("Question : ")

    if question.lower() == "quit":
        break
    answer = generate_answer(question, trigram_probs)
    print(answer)