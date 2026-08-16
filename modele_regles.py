import spacy
import random
nlp = spacy.load("en_core_web_sm")
reponses_merci = [
        "Happy to help!",
        "No worries!",
        "You're welcome!"
]
reponses_requete = [
    "Sorry, I can only answer questions and nothing else.",
    "Sorry I'm not able to do that.",
    "Unfortunatly I can only answer questions"
]
reponses_salutation = [
    "Hello, I am a chatbot. How can I assist you?",
    "Hey, what can I do for you?",
    "Hi, i'm your personnal ai chatbot. Ask me something."
]
reponses_aurevoir = [
    "Bye, see you soon!",
    "See you!",
    "Hope i could help!"
]
reponse_chauvesouris =  [
    "A bat is a small flying animal that can loacate itself using echolocation.",
    "Bats are commonly found in caves and these animals live during night."
]
while True:
    question = input("question:")
    doc = nlp(question.lower())
    tokens = [token.text.lower() for token in doc if not token.is_space and not token.is_punct]

    if any(mot in tokens for mot in ["hello", "hi"]):
        print(random.choice(reponses_salutation))
    elif any(mot in tokens for mot in ["can", "could"]):
        print(random.choice(reponses_requete))
    elif any(mot in tokens for mot in ["thank", "thanks"]):
        print(random.choice(reponses_merci))
    elif any(mot in tokens for mot in ["bye", "goodbye"]):
        print(random.choice(reponses_aurevoir))
        break
    elif any(mot in tokens for mot in["bat", "bats"]):
        print(random.choice(reponse_chauvesouris))
    else:
        print("Sorry, I didn't understand. You can reformulate or ask me something different.")