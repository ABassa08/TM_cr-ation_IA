import requests
from bs4 import BeautifulSoup
import time
import re

headers = {"User-Agent": "Mozilla/5.0"} # user agent pour ne pas se faire prendre pour un bot par wikipédia

themes = [
    # Informatique / IA
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "natural language processing", "computer vision", "robotics", "data science",
    "algorithm", "computer science", "programming language", "software engineering",
    "cybersecurity", "cryptography", "database", "cloud computing", "internet",
    "World Wide Web", "operating system", "computer hardware", "compiler",
    "open source software", "computer network", "quantum computing",

    # Sciences
    "physics", "chemistry", "biology", "astronomy", "mathematics", "genetics",
    "evolution", "quantum mechanics", "climate change", "ecology", "neuroscience",
    "medicine", "psychology", "geology", "oceanography", "particle physics",
    "thermodynamics", "electromagnetism", "relativity", "organic chemistry",
    "biochemistry", "microbiology", "immunology", "virology", "paleontology",
    "meteorology", "seismology", "volcanology", "botany", "zoology",
    "marine biology", "genome", "photosynthesis",

    # Mathématiques
    "geometry", "calculus", "statistics", "probability", "number theory",
    "topology", "linear algebra", "game theory", "cryptanalysis", "logic",

    # Technologie / ingénierie
    "engineering", "mechanical engineering", "electrical engineering",
    "civil engineering", "aerospace engineering", "semiconductor",
    "nuclear power", "solar power", "wind power", "battery technology",
    "supercomputer", "automation", "drone", "autonomous vehicle",
    "wearable technology", "3D printing", "nanotechnology", "biotechnology",
    "virtual reality", "augmented reality", "blockchain",

    # Histoire
    "World War II", "World War I", "ancient Rome", "ancient Egypt",
    "ancient Greece", "Byzantine Empire", "Ottoman Empire",
    "Industrial Revolution", "Renaissance", "Middle Ages",
    "colonialism", "slavery", "human migration", "silk road",
    "printing press", "scientific revolution", "space race",

    # Nature / géographie
    "mountain", "ocean", "continent", "river", "desert", "glacier",
    "rainforest", "coral reef", "biodiversity", "deforestation",
    "endangered species", "volcano", "earthquake", "tsunami", "hurricane",
    "drought", "pollution", "recycling", "conservation", "weather",

    # Culture / art
    "philosophy", "literature", "music", "cinema", "art", "architecture",
    "religion", "mythology", "language", "education", "painting",
    "sculpture", "poetry", "theatre", "opera", "ballet", "photography",
    "fashion", "video game", "animation", "jazz", "classical music",
    "rock music", "hip hop",

    # Société / sciences humaines
    "ethics", "metaphysics", "existentialism", "stoicism",
    "sociology", "anthropology", "linguistics", "communication",
    "propaganda", "censorship", "journalism",

    # Sport
    "Olympic Games", "football", "basketball", "tennis", "swimming",
    "cricket", "rugby", "golf", "boxing", "martial arts", "cycling",
    "athletics", "chess", "esports", "marathon",

    # Santé / médecine
    "vaccine", "epidemic", "pandemic", "surgery", "mental health",
    "nutrition", "anatomy", "pharmacology", "cancer", "genetic disorder",

    # Société moderne
    "social media", "smartphone", "electric vehicle", "e-commerce",
    "cryptocurrency", "streaming service", "podcast", "remote work",
    "artificial general intelligence", "big data","wireless network",

    # Espace / univers
    "space exploration", "black hole", "galaxy", "solar system",
    "exoplanet", "asteroid", "comet", "telescope",
    "International Space Station", "Mars", "Moon landing", "universe",

    # Vie quotidienne
    "food", "agriculture", "transportation", "tourism", "health",
    "sport", "animal", "plant"
]

def get_titles_from_search(query, limit=100, retries=3):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'utf8': 1,
        'srsearch': query,
        'srlimit': limit
    }

    for attempt in range(retries): # cette partie a été faite avec l'IA car mon code ne fonctionnait pas et je ne savais pas comment le fixer.
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 429:
            print(f" Rate limit atteint pour '{query}', pause de 5s (tentative {attempt + 1}/{retries})")
            time.sleep(5)
            continue

        try:
            data = response.json()
            return [result['title'] for result in data['query']['search']]
        except requests.exceptions.JSONDecodeError:
            print(f" Erreur JSON pour '{query}', tentative {attempt + 1}/{retries}")
            time.sleep(2)

    print(f" Abandon définitif pour la recherche : {query}")
    return []

def scrape_wikipedia_page(subject, retries=3):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': subject,
        'format': 'json',
        'prop': 'text',
        'redirects': ''
    }

    for attempt in range(retries):  # même fonction que avant avec l'ia
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 429:
            print(f" Rate limit atteint pour {subject}, pause de 5s (tentative {attempt + 1}/{retries})")
            time.sleep(5)
            continue

        try:
            data = response.json()
            break
        except requests.exceptions.JSONDecodeError:
            print(f"️ Erreur JSON pour {subject}, tentative {attempt + 1}/{retries}")
            time.sleep(2)
    else:
        print(f" Abandon définitif pour : {subject}")
        return ""

    if 'parse' not in data:
        return ""

    raw_html = data['parse']['text']['*']
    soup = BeautifulSoup(raw_html, 'html.parser')

    text = ""
    for p in soup.find_all('p'):
        text += p.text
    return text

for theme in themes:
    texte_complet = ""
    titres = get_titles_from_search(theme, limit=120)
    print(f"{len(titres)} titres trouvés pour {theme}")
    time.sleep(2)

    for titre in titres: # pour tout les titres de chaques thèmes ça scrap
        texte_complet += scrape_wikipedia_page(titre) + " "
        time.sleep(2)

    with open("moyen.txt", "a", encoding="utf-8") as f:
        f.write(texte_complet) # on écrit le texte scrapé
with open("moyen.txt", "r", encoding="utf-8") as f:
    text = f.read()
text = re.sub(r'\{\\displaystyle.*?\}', '', text) # lecture du texte et nettoyage
text = re.sub(r'\[\d+\]', '', text)
with open("moyen.txt", "w", encoding="utf-8") as f:
    f.write(text) # remplacement des endroits nettoyés
with open("moyen.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

lignes_filtrees = []
for line in lines:
    stripped = line.strip()

    if len(stripped) > 3: # filtrage des lignes trop petites
        lignes_filtrees.append(line)

with open("moyen.txt", "w", encoding="utf-8") as f:
    f.writelines(lignes_filtrees) #remplacement des lignes