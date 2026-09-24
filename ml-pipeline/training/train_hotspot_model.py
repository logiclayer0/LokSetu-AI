import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os


DATA_PATH = "../data/processed/hotspot_data.csv"
MODEL_PATH = "../models/hotspot_model.pkl"


def load_data():
    df = pd.read_csv(DATA_PATH)
    features = ["population", "infrastructure_index", "complaint_count", "avg_income"]
    target = "priority_score"
    return df[features], df[target]


def train():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, predictions):.4f}")
    print(f"R2: {r2_score(y_test, predictions):.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved at {MODEL_PATH}")


if __name__ == "__main__":
    train()