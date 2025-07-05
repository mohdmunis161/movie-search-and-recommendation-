import os
import re
import pickle
import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process, fuzz
import nltk
import requests

# Import OMDB poster fetcher
from models.omdb_poster import get_movie_poster

# Ensure NLTK Resources
def ensure_nltk_data():
    try: nltk.data.find('tokenizers/punkt')
    except LookupError: nltk.download('punkt')

ensure_nltk_data()

# === GloVe Loader with Cache ===
def load_glove_embeddings(path, cache_file='cache/glove_dict.pkl'):
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    glove_dict = {}
    with open(path, 'r', encoding='utf8') as f:
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            vec = np.array(parts[1:], dtype='float32')
            glove_dict[word] = vec

    with open(cache_file, 'wb') as f:
        pickle.dump(glove_dict, f)
    return glove_dict

# === Tokenize and Embed ===
def embed_text_glove(text, glove_dict, dim=100):
    words = nltk.word_tokenize(text.lower())
    vectors = [glove_dict[w] for w in words if w in glove_dict]
    return np.mean(vectors, axis=0) if vectors else np.zeros(dim)

def correct_query(query, all_titles, min_score=85):
    best_match, score, _ = process.extractOne(query, all_titles, scorer=fuzz.token_sort_ratio)
    return best_match if score > min_score else query

# === Boosters ===
def boost_title_matches(df, query_tokens, bm25_scores, boost=0.5):
    boost_vector = np.array([
        any(token in title.lower() for token in query_tokens)
        for title in df['title']
    ], dtype=float)
    return bm25_scores + boost * boost_vector

def boost_phrase_matches(df, query, scores, boost_val=0.5):
    return scores + np.array([boost_val if query.lower() in title.lower() else 0 for title in df['title']])

# === Load + Cache Movie Data ===
def load_movie_data_cached(movie_path, tags_path, scores_path, ratings_path, cache_dir='cache'):
    os.makedirs(cache_dir, exist_ok=True)
    df_path = os.path.join(cache_dir, 'movie_df.pkl')
    token_path = os.path.join(cache_dir, 'tokenized_docs.pkl')

    if os.path.exists(df_path) and os.path.exists(token_path):
        df = pd.read_pickle(df_path)
        with open(token_path, 'rb') as f:
            tokenized = pickle.load(f)
        return df, tokenized

    movies_df = pd.read_csv(movie_path)
    tags_df = pd.read_csv(tags_path)
    scores_df = pd.read_csv(scores_path)
    ratings_df = pd.read_csv(ratings_path)

    top_tags = scores_df[scores_df['relevance'] > 0.3].merge(tags_df, on='tagId')
    tag_groups = top_tags.groupby('movieId')['tag'].apply(lambda tags: ' '.join(tags)).reset_index()

    rating_summary = ratings_df.groupby('movieId').agg({'rating': 'mean', 'userId': 'count'}).reset_index()
    rating_summary.columns = ['movieId', 'avg_rating', 'rating_count']

    df = movies_df.merge(tag_groups, on='movieId', how='left')
    df = df.merge(rating_summary, on='movieId', how='left')
    df = df.fillna({'tag': '', 'avg_rating': 0, 'rating_count': 0})
    df['doc'] = df['title'] + ' ' + df['genres'] + ' ' + df['tag']

    tokenized = [nltk.word_tokenize(doc.lower()) for doc in df['doc']]

    df.to_pickle(df_path)
    with open(token_path, 'rb') as f:
        pickle.dump(tokenized, f)

    return df, tokenized

def load_bm25_index(tokenized_docs, cache_file='cache/bm25_index.pkl'):
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    bm25 = BM25Okapi(tokenized_docs)
    with open(cache_file, 'wb') as f:
        pickle.dump(bm25, f)
    return bm25

def load_glove_doc_vectors(df, glove_dict, cache_file='cache/glove_doc_vectors.npy'):
    if os.path.exists(cache_file):
        return np.load(cache_file)
    vectors = np.array([
        embed_text_glove(doc, glove_dict) for doc in df['doc']
    ])
    np.save(cache_file, vectors)
    return vectors

# === Hybrid Search Core ===
def hybrid_search(query, bm25, tokenized_docs, glove_doc_vectors, all_titles, df, glove_dict, alpha=0.6):
    corrected = correct_query(query, all_titles)
    query_tokens = nltk.word_tokenize(corrected.lower())

    bm25_raw = bm25.get_scores(query_tokens)
    bm25_boosted = boost_title_matches(df, query_tokens, bm25_raw)
    bm25_boosted = boost_phrase_matches(df, corrected, bm25_boosted)

    query_vec = embed_text_glove(corrected, glove_dict).reshape(1, -1)
    cosine_scores = cosine_similarity(glove_doc_vectors, query_vec).flatten()

    # Normalize
    bm25_norm = (bm25_boosted - bm25_boosted.min()) / (bm25_boosted.max() - bm25_boosted.min() + 1e-8)
    cosine_norm = (cosine_scores - cosine_scores.min()) / (cosine_scores.max() - cosine_scores.min() + 1e-8)

    hybrid_scores = alpha * bm25_norm + (1 - alpha) * cosine_norm
    hybrid_scores *= (df['avg_rating'] / 5).values

    df['score'] = hybrid_scores
    return df.sort_values('score', ascending=False)

# === Final API Function ===
def search_general(query, top_k=200, txt_path="data/movies_links.txt",
                   movie_path="data/ml-latest/movies.csv",
                   tags_path="data/ml-latest/genome-tags.csv",
                   scores_path="data/ml-latest/genome-scores.csv",
                   ratings_path="data/ml-latest/ratings.csv",
                   glove_path="models/glove.6B.100d.txt"):

    # Load data + cache
    df, tokenized_docs = load_movie_data_cached(movie_path, tags_path, scores_path, ratings_path)
    glove_dict = load_glove_embeddings(glove_path)
    bm25 = load_bm25_index(tokenized_docs)
    glove_doc_vectors = load_glove_doc_vectors(df, glove_dict)
    all_titles = df['title'].tolist()

    # Rank by hybrid
    ranked_df = hybrid_search(query, bm25, tokenized_docs, glove_doc_vectors, all_titles, df, glove_dict, alpha=0.6)

    # Filter top_k with year ≥ 1990
    def extract_year(title):
        match = re.search(r'\((\d{4})\)', title)
        return int(match.group(1)) if match else None

    top_df = ranked_df.head(500).copy()
    top_df['year'] = top_df['title'].apply(extract_year)
    top_df = top_df[top_df['year'].notnull() & (top_df['year'] >= 1990)].head(top_k)

    # Load txt file
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    title_to_line = {line.split('|')[0].strip().lower(): line.strip() for line in lines}

    # Match titles and build results with poster fetching
    matched = []
    count = 0
    for _, row in top_df.iterrows():
        title = row['title']
        key = title.lower()
        if key in title_to_line:
            parts = title_to_line[key].split('|')
            
            # Fetch poster from OMDB API
            poster_url = get_movie_poster(parts[0].strip())
            
            matched.append({
                "title": parts[0].strip(),
                "link1": parts[1].strip() if parts[1].strip().lower() != 'null' else None,
                "link2": parts[2].strip() if len(parts) > 2 and parts[2].strip().lower() != 'null' else None,
                "poster_url": poster_url
            })
        count += 1
        if len(matched) >= 10 or count >= 100:
            break
    return matched  # list of dicts or empty list
