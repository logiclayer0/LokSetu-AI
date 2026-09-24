import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os


DATA_PATH = "../data/processed/complaints.csv"
MODEL_PATH = "../models/complaint_classifier.pkl"


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df["text"].tolist(), df["category"].tolist()


def train():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000, C=1.0)),
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    print(classification_report(y_test, predictions))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved at {MODEL_PATH}")


if __name__ == "__main__":
    train()