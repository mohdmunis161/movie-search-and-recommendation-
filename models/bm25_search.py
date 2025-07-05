import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
import nltk
import re
import os
import pickle
from tqdm import tqdm
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import requests

# Import OMDB poster fetcher
from models.omdb_poster import get_movie_poster

# === Ensure NLTK Resources Are Installed ===
def ensure_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

ensure_nltk_data()

# === Setup Stopwords and Stemmer ===
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess_text(text):
    text = text.replace("-", " ")
    text = re.sub(r'[\W_]+', ' ', text)
    tokens = nltk.word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    return [stemmer.stem(t) for t in tokens]

def extract_year(title):
    match = re.search(r'\((\d{4})\)', title)
    return int(match.group(1)) if match else None

def load_or_cache_data(movie_path="data/ml-latest/movies.csv", cache_path="cache"):
    os.makedirs(cache_path, exist_ok=True)

    df_cache_path = os.path.join(cache_path, "movies_df.pkl")
    tokens_cache_path = os.path.join(cache_path, "tokenized_titles.pkl")
    bm25_cache_path = os.path.join(cache_path, "bm25_index.pkl")

    if all(os.path.exists(p) for p in [df_cache_path, tokens_cache_path, bm25_cache_path]):
        with open(df_cache_path, 'rb') as f:
            df = pickle.load(f)
        with open(tokens_cache_path, 'rb') as f:
            tokenized_titles = pickle.load(f)
        with open(bm25_cache_path, 'rb') as f:
            bm25 = pickle.load(f)
    else:
        df = pd.read_csv(movie_path)
        df['title'] = df['title'].astype(str)
        df['year'] = df['title'].apply(extract_year)
        df['title_tokens'] = df['title'].apply(preprocess_text)
        tokenized_titles = df['title_tokens'].tolist()

        bm25 = BM25Okapi(tokenized_titles)

        with open(df_cache_path, 'wb') as f:
            pickle.dump(df, f)
        with open(tokens_cache_path, 'wb') as f:
            pickle.dump(tokenized_titles, f)
        with open(bm25_cache_path, 'wb') as f:
            pickle.dump(bm25, f)

    return df, tokenized_titles, bm25

# === Exposed Function for Flask ===
def search_specific(query, top_k=200, txt_path="data/movies_links.txt", movie_path="data/ml-latest/movies.csv", tags_path="data/ml-latest/genome-tags.csv", scores_path="data/ml-latest/genome-scores.csv", ratings_path="data/ml-latest/ratings.csv"):
    df, tokenized_titles, bm25 = load_or_cache_data()
    query_tokens = preprocess_text(query)

    bm25_scores = bm25.get_scores(query_tokens)
    df['bm25_score'] = bm25_scores
    df = df[df['year'].notnull() & (df['year'] >= 1990)]
    df = df.sort_values(by='bm25_score', ascending=False)

    top_titles = df.head(top_k)['title'].tolist()

    # Search in txt file
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    line_dict = {}
    for line in lines:
        parts = line.strip().split('|')
        title = parts[0].strip()
        line_dict[title.lower()] = line.strip()

    matched_lines = []
    for title in top_titles:
        if title.lower() in line_dict:
            matched_lines.append(line_dict[title.lower()])
        if len(matched_lines) == top_k:
            break

    # Filter final lines to contain all query tokens in title
    matched = []
    for line in matched_lines:
        movie_title = line.split('|')[0]
        title_tokens = set(preprocess_text(movie_title))
        if all(token in title_tokens for token in query_tokens):
            parts = line.split('|')
            
            # Fetch poster from OMDB API
            poster_url = get_movie_poster(parts[0].strip())
            
            matched.append({
                "title": parts[0].strip(),
                "link1": parts[1].strip() if parts[1].strip().lower() != "null" else None,
                "link2": parts[2].strip() if len(parts) > 2 and parts[2].strip().lower() != "null" else None,
                "poster_url": poster_url
            })

    return matched if matched else []
