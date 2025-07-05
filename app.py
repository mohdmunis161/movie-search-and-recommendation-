from flask import Flask, render_template, request, redirect, url_for, session
import os

# === Import your methods ===
from models.bm25_search import search_specific as bm25_specific_search
from models.hybrid_search import search_general as hybrid_general_search
from models.fast_genre_recommend import recommend_movies_by_genre_fast

# === Flask App Setup ===
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

@app.route('/')
def home():
    return render_template('user_id_entry.html')

@app.route('/search_page')
def search_page():
    return render_template('search_page.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    search_type = request.form['search_type']

    print(f"🔎 Received query: {query} | Type: {search_type}")

    if search_type == "specific":
        lines = bm25_specific_search(query)
    else:
        lines = hybrid_general_search(query)

    if not lines:
        return render_template('results.html', results=[], message="No match found.")
    return render_template('results.html', results=lines)

@app.route('/genre_recommendations')
def genre_recommendations():
    return render_template('genre_recommendations.html')

@app.route('/get_genre_recommendations', methods=['POST'])
def get_genre_recommendations():
    genre_preferences = request.form['genre_preferences']
    
    if not genre_preferences.strip():
        return render_template('genre_recommendations.html', error="Please enter your genre preferences.")
    
    print(f"🎯 Running Fast Genre-Based Recommendations for: {genre_preferences}")
    lines = recommend_movies_by_genre_fast(genre_preferences)

    if not lines:
        return render_template('results.html', results=[], message="No recommendations found for your preferences.")
    return render_template('results.html', results=lines, is_recommendation=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
