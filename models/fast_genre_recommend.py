import pandas as pd
import numpy as np
import os
import pickle
import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

# Import OMDB poster fetcher
from models.omdb_poster import get_movie_poster

# === Fast Genre-Based Recommendation System ===

def load_movies_from_links(cache_path="cache/movies_data.pkl"):
    """Load and process movies from movies_links.txt with caching"""
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    
    movies = []
    file_path = "data/movies_links.txt"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split('|')
                if len(parts) >= 3:
                    title = parts[0].strip()
                    link1 = parts[1].strip() if parts[1].strip().lower() != "null" else None
                    link2 = parts[2].strip() if len(parts) > 2 and parts[2].strip().lower() != "null" else None
                    
                    # Extract year from title
                    year_match = re.search(r'\((\d{4})\)', title)
                    year = int(year_match.group(1)) if year_match else 1900
                    
                    # Clean title (remove year)
                    clean_title = re.sub(r'\(\d{4}\)', '', title).strip()
                    
                    movies.append({
                        'title': title,
                        'clean_title': clean_title,
                        'year': year,
                        'link1': link1,
                        'link2': link2,
                        'original_line': line
                    })
    
    # Create processed data
    processed_data = {
        'movies': movies,
        'title_to_movie': {movie['title'].lower(): movie for movie in movies},
        'year_groups': defaultdict(list),
        'title_keywords': {}
    }
    
    # Group by decades for faster filtering
    for movie in movies:
        decade = (movie['year'] // 10) * 10
        processed_data['year_groups'][decade].append(movie)
    
    # Extract keywords from titles for genre matching
    for movie in movies:
        title_lower = movie['clean_title'].lower()
        keywords = set(re.findall(r'\b\w+\b', title_lower))
        processed_data['title_keywords'][movie['title']] = keywords
    
    # Cache the processed data
    with open(cache_path, 'wb') as f:
        pickle.dump(processed_data, f)
    
    return processed_data

def create_genre_keywords():
    """Create comprehensive genre keyword mappings"""
    return {
        'action': ['action', 'adventure', 'thriller', 'war', 'martial', 'fight', 'battle', 'hero', 'superhero', 'mission', 'spy', 'agent'],
        'comedy': ['comedy', 'funny', 'humor', 'romantic', 'romcom', 'sitcom', 'joke', 'laugh', 'hilarious', 'fun'],
        'drama': ['drama', 'romance', 'romantic', 'melodrama', 'emotional', 'tragedy', 'love', 'relationship'],
        'thriller': ['thriller', 'suspense', 'mystery', 'crime', 'detective', 'murder', 'investigation', 'conspiracy', 'psychological'],
        'sci-fi': ['sci-fi', 'science', 'futuristic', 'space', 'alien', 'robot', 'cyber', 'future', 'technology', 'apocalypse'],
        'horror': ['horror', 'scary', 'frightening', 'supernatural', 'ghost', 'demon', 'zombie', 'vampire', 'monster', 'haunted'],
        'fantasy': ['fantasy', 'magical', 'superhero', 'mythical', 'wizard', 'magic', 'dragon', 'fairy', 'enchanted'],
        'animation': ['animation', 'animated', 'cartoon', 'family', 'kids', 'children', 'pixar', 'disney'],
        'documentary': ['documentary', 'docu', 'real', 'biography', 'biopic', 'true', 'story', 'history'],
        'western': ['western', 'cowboy', 'wild', 'west', 'ranch', 'outlaw'],
        'musical': ['musical', 'music', 'song', 'dance', 'concert', 'band'],
        'sport': ['sport', 'football', 'basketball', 'baseball', 'soccer', 'tennis', 'boxing', 'wrestling'],
        'latest': ['latest', 'recent', 'new', '2020', '2021', '2022', '2023', '2024'],
        'classic': ['classic', 'old', 'vintage', 'retro', 'timeless', 'legendary'],
        'indian': ['hindi', 'bollywood', 'indian', 'tamil', 'telugu', 'malayalam', 'kannada', 'bengali'],
        'hollywood': ['hollywood', 'american', 'english', 'usa']
    }

def parse_user_preferences(preferences_text):
    """Parse user genre preferences from text input"""
    preferences = preferences_text.lower()
    
    genre_keywords = create_genre_keywords()
    matched_genres = []
    years = []
    
    # Find matching genres
    for genre, keywords in genre_keywords.items():
        if any(keyword in preferences for keyword in keywords):
            matched_genres.append(genre)
    
    # Extract year preferences
    year_pattern = r'(\d{4})'
    years = re.findall(year_pattern, preferences)
    
    # Check for decade preferences
    decade_pattern = r'(\d{3})0s'
    decades = re.findall(decade_pattern, preferences)
    for decade in decades:
        years.extend([f"{decade}0", f"{decade}1", f"{decade}2", f"{decade}3", f"{decade}4", f"{decade}5", f"{decade}6", f"{decade}7", f"{decade}8", f"{decade}9"])
    
    return matched_genres, years

def calculate_movie_score(movie, user_genres, user_years, title_keywords):
    """Calculate a score for a movie based on user preferences"""
    score = 0
    movie_title = movie['clean_title'].lower()
    movie_year = movie['year']
    movie_keywords = title_keywords.get(movie['title'], set())
    
    # Genre matching
    for genre in user_genres:
        genre_keywords = create_genre_keywords().get(genre, [])
        for keyword in genre_keywords:
            if keyword in movie_title or keyword in movie_keywords:
                score += 2
                break
    
    # Year matching
    if user_years:
        for year in user_years:
            try:
                target_year = int(year)
                if abs(movie_year - target_year) <= 5:
                    score += 1
            except ValueError:
                continue
    
    # Latest movies preference
    if 'latest' in user_genres and movie_year >= 2020:
        score += 3
    
    # Classic movies preference
    if 'classic' in user_genres and movie_year < 2000:
        score += 3
    
    # Recent movies bonus (2010+)
    if movie_year >= 2010:
        score += 0.5
    
    # Title length bonus (shorter titles often better)
    if len(movie['clean_title']) < 30:
        score += 0.3
    
    return score

def get_fast_recommendations(user_preferences, n_recommendations=15):
    """Get fast movie recommendations based on user preferences"""
    # Load cached data
    processed_data = load_movies_from_links()
    if not processed_data:
        return []
    
    movies = processed_data['movies']
    title_keywords = processed_data['title_keywords']
    
    # Parse user preferences
    user_genres, user_years = parse_user_preferences(user_preferences)
    
    # If no genres detected, use popular genres
    if not user_genres and not user_years:
        user_genres = ['action', 'comedy', 'drama']
    
    # Calculate scores for all movies
    scored_movies = []
    for movie in movies:
        score = calculate_movie_score(movie, user_genres, user_years, title_keywords)
        if score > 0:  # Only include movies with some relevance
            scored_movies.append((movie, score))
    
    # Sort by score and get top recommendations
    scored_movies.sort(key=lambda x: x[1], reverse=True)
    
    # Remove duplicates and format results
    seen_titles = set()
    recommendations = []
    
    for movie, score in scored_movies:
        title_lower = movie['title'].lower()
        if title_lower not in seen_titles and len(recommendations) < n_recommendations:
            seen_titles.add(title_lower)
            
            # Fetch poster from OMDB API
            poster_url = get_movie_poster(movie['title'])
            
            recommendations.append({
                'movieId': movie.get('movieId', 0),
                'title': movie['title'],
                'genres': movie.get('genres', ''),
                'year': movie['year'],
                'avg_rating': movie.get('avg_rating', 0),
                'rating_count': movie.get('rating_count', 0),
                'score': score,
                'link1': movie['link1'],
                'link2': movie['link2'],
                'poster_url': poster_url
            })
    
    return recommendations

def get_popular_genres():
    """Get list of popular genres for the UI"""
    return [
        'Action', 'Comedy', 'Drama', 'Thriller', 'Sci-Fi', 
        'Horror', 'Fantasy', 'Animation', 'Documentary', 
        'Latest', 'Classic', 'Indian', 'Hollywood'
    ]

def load_title_link_map(txt_path="data/movies_links.txt"):
    """Load movie title to link mapping"""
    title_map = {}
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                title = parts[0].strip().lower()
                title_map[title] = line.strip()
    return title_map

# === Main API Function ===
def recommend_movies_by_genre_fast(genre_preferences):
    """Main function to get fast movie recommendations based on genre preferences"""
    try:
        if not genre_preferences.strip():
            return []
        
        # Get recommendations
        recommendations = get_fast_recommendations(genre_preferences, n_recommendations=20)
        
        # Format results (limit to 10 for display)
        results = []
        for rec in recommendations[:10]:
            results.append({
                "title": rec['title'],
                "link1": rec['link1'],
                "link2": rec['link2'],
                "poster_url": rec['poster_url']
            })
        
        return results
        
    except Exception as e:
        print(f"Error in fast genre recommendation: {e}")
        return [] 