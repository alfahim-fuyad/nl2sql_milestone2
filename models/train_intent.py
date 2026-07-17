import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def train_and_save(csv_path="training_data/intent_dataset.csv",
                   model_path="models/intent_model.pkl",
                   vectorizer_path="models/vectorizer.pkl"):

    data = pd.read_csv(csv_path)
    X, y = data["question"], data["intent"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)

    model = MultinomialNB()
    model.fit(X_train_vec, y_train)

    acc = accuracy_score(y_test, model.predict(vectorizer.transform(X_test)))
    print(f"Accuracy: {round(acc * 100, 2)}%")

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)
    print("Model saved.")


if __name__ == "__main__":
    train_and_save()
