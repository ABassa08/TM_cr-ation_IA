import spacy

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
nlp.max_length = 600_000_000

with open("moyen.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = nlp(text)
tokens = [token.text for token in doc if not token.is_space and not token.is_punct]
print("nombre de tokens (spaCy) :", len(tokens))