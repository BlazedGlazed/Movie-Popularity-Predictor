import pandas as pd
import os
import time
from scripts.yt_stats import get_video_details
from scripts.comment_scraper import get_comments
from scripts.sentiment import get_comment_sentiment
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

def collect_all_features(video_id):
    # --- 1. Get YouTube stats (saved to yt_data.csv) ---
    get_video_details([video_id])
    time.sleep(2)  # Give time to write file

    if not os.path.exists("data/yt_data.csv"):
        print("YouTube stats file not found!")
        return None

    yt_data = pd.read_csv("data/yt_data.csv")
    yt_data = yt_data[yt_data["video_id"] == video_id]

    if yt_data.empty:
        print("No data found for this video ID in yt_data.csv")
        return None

    # --- 2. Get Comments and Sentiment ---
    comments = get_comments(video_id)
    sentiments = [get_comment_sentiment(c) for c in comments] if comments else []
    avg_sentiment = np.mean(sentiments) if sentiments else 0

    features = {
        "video_id": video_id,
        "views": int(yt_data["views"].values[0]),
        "likes": int(yt_data["likes"].values[0]),
        "comments_count": int(yt_data["comments"].values[0]),
        "avg_sentiment": avg_sentiment
    }

    return features

def train_regression_model(full_df):
    feature_cols = ["views", "likes", "comments_count", "avg_sentiment", "budget", "duration", "release_year"]
    full_df = full_df.dropna(subset=feature_cols + ["popularity"])
    X = full_df[feature_cols]
    y = full_df["popularity"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    mse = mean_squared_error(y_test, pred)
    print(f"[✔] Model trained. MSE: {mse:.2f}")
    return model

def predict_new_video(video_id, model, movie_data):
    print(f"\n🔎 Collecting data for Video ID: {video_id}...")
    yt_features = collect_all_features(video_id)
    if not yt_features:
        print("Failed to collect features.")
        return

    # Use average values from movie_data for missing fields
    avg_data = movie_data[["budget", "duration", "release_year"]].mean().to_dict()
    full_input = {**yt_features, **avg_data}
    input_df = pd.DataFrame([full_input])
    prediction = model.predict(input_df)[0]

    print(f"\n🎯 Predicted Popularity Score: {prediction:.2f}")
    return prediction

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_prediction.py <YouTube_VIDEO_ID>")
        exit(1)

    video_id = sys.argv[1]

    if not os.path.exists("data/movie_data.csv"):
        print("Missing movie_data.csv file!")
        exit(1)

    movie_data = pd.read_csv("data/movie_data.csv")
    model = train_regression_model(movie_data)
    predict_new_video(video_id, model, movie_data)
