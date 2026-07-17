import re
import pickle

SHOW = re.compile(r"\b(show|list|display|give me|find all|get all|fetch|retrieve)\b", re.I)
COUNT = re.compile(r"\b(count|how many|number of|total number)\b", re.I)
RANK = re.compile(r"\b(top|bottom|lowest|least|worst|best)\s+\d+\b", re.I)


def load_model(model_path="models/intent_model.pkl",
               vectorizer_path="models/vectorizer.pkl"):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)
    return model, vectorizer


def predict_intent(text, model, vectorizer):
    if RANK.search(text):
        return "SELECT"
    if SHOW.search(text) and not COUNT.search(text):
        return "SELECT"
    return model.predict(vectorizer.transform([text]))[0]
