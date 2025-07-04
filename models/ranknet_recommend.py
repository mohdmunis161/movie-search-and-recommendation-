import pandas as pd
import numpy as np
import os
import torch
import torch.nn as nn
import pickle
import re
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from skorch import NeuralNetRegressor
import requests

# === RankNet Model ===
class RankNet(nn.Module):
    def __init__(self, num_features):
        super().__init__()
        self.hidden = nn.Sequential(
            nn.Linear(num_features, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.hidden(x)

# === Load and Cache Features ===
def load_data(sample_size=15000):
    ratings = pd.read_csv("data/ml-latest/ratings.csv")
    movies = pd.read_csv("data/ml-latest/movies.csv")
    tags = pd.read_csv("data/ml-latest/genome-tags.csv")
    scores = pd.read_csv("data/ml-latest/genome-scores.csv")

    tag_rel = scores[scores['relevance'] > 0.3].merge(tags, on='tagId')
    tag_text = tag_rel.groupby('movieId')['tag'].apply(lambda x: ' '.join(x)).reset_index()

    df = ratings.merge(movies, on='movieId')
    df = df.merge(tag_text, on='movieId', how='left')
    df['tag'] = df['tag'].fillna('')
    df = df.sample(sample_size, random_state=42).reset_index(drop=True)
    return df

def create_features(df, cache_path="cache/features.parquet"):
    if os.path.exists(cache_path):
        return pd.read_parquet(cache_path), ['text_len', 'genre_count', 'rating_norm']

    df['text'] = (df['title'] + ' ' + df['genres'] + ' ' + df['tag']).fillna('')
    df['text_len'] = df['text'].apply(lambda x: len(x.split()))
    df['genre_count'] = df['genres'].apply(lambda x: len(x.split('|')) if isinstance(x, str) else 0)
    df['rating_norm'] = (df['rating'] - df['rating'].min()) / (df['rating'].max() - df['rating'].min())

    le_user = LabelEncoder()
    le_movie = LabelEncoder()
    df['user_idx'] = le_user.fit_transform(df['userId'])
    df['movie_idx'] = le_movie.fit_transform(df['movieId'])

    df.to_parquet(cache_path)
    return df, ['text_len', 'genre_count', 'rating_norm']

# === Load/Train RankNet ===
def load_or_train_model(df, feature_cols, cache_path="cache/ranknet_model.pkl"):
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return pickle.load(f)

    X = torch.tensor(df[feature_cols].values, dtype=torch.float32)
    y = torch.tensor(df['rating_norm'].values, dtype=torch.float32)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    net = NeuralNetRegressor(
        RankNet(num_features=X.shape[1]),
        max_epochs=10,
        lr=0.01,
        optimizer=torch.optim.Adam,
        iterator_train__shuffle=True,
        verbose=0
    )
    net.fit(X_train, y_train)

    model = net.module_
    with open(cache_path, 'wb') as f:
        pickle.dump(model, f)

    return model

# === Cache User Recommendations ===
def cache_user_recs(model, df, features, cache_file="cache/user_recs.pkl"):
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    user_recs = {}
    unique_movies = df.drop_duplicates('movieId')[['movieId', 'title', 'genres'] + features]

    for user_id in df['userId'].unique():
        temp_df = unique_movies.copy()
        temp_df['userId'] = user_id
        X_user = torch.tensor(temp_df[features].values, dtype=torch.float32)
        with torch.no_grad():
            temp_df['score'] = model.forward(X_user).numpy()
        temp_df['year'] = temp_df['title'].str.extract(r'\((\d{4})\)').astype(float)
        recent = temp_df[temp_df['year'] >= 1990].sort_values('score', ascending=False).head(200)
        user_recs[user_id] = recent

    with open(cache_file, 'wb') as f:
        pickle.dump(user_recs, f)

    return user_recs

# === Load Movie Links ===
def load_title_link_map(txt_path="data/movies_links.txt"):
    title_map = {}
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                title = parts[0].strip().lower()
                title_map[title] = line.strip()
    return title_map

# === API Function: Recommend Movies ===
def recommend_movies_for_user(user_id):
    df = load_data()
    df, feature_cols = create_features(df)
    model = load_or_train_model(df, feature_cols)
    user_recs = cache_user_recs(model, df, feature_cols)
    title_map = load_title_link_map()

    # Join with links.csv to get imdbId
    links_df = pd.read_csv('data/ml-latest/links.csv')
    movieid_to_imdbid = dict(zip(links_df['movieId'], links_df['imdbId']))

    if user_id not in user_recs:
        return []

    results = []
    for _, row in user_recs[user_id].iterrows():
        title = row['title'].strip()
        key = title.lower()
        if key in title_map:
            parts = title_map[key].split('|')
            results.append({
                "title": parts[0],
                "link1": parts[1] if parts[1].lower() != "null" else None,
                "link2": parts[2] if len(parts) > 2 and parts[2].lower() != "null" else None
            })
        if len(results) >= 10:
            break
    return results  # list of dicts
