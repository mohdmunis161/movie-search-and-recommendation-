from flask import Flask, render_template, request, redirect, url_for, session
import os

# === Import your methods ===
from models.bm25_search import search_specific as bm25_specific_search
from models.hybrid_search import search_general as hybrid_general_search
from models.ranknet_recommend import recommend_movies_for_user
# === Flask App Setup ===
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# === Sample user IDs for RankNet ===
SAMPLE_USER_IDS = [211360, 122101, 183489, 123359, 192886, 183624, 188996, 39466, 299307, 248977]

@app.route('/')
def home():
    return render_template('user_id_entry.html')

@app.route('/validate_user', methods=['POST'])
def validate_user():
    user_id = request.form['user_id']
    try:
        user_id = int(user_id)
    except:
        return render_template('user_id_entry.html', error="Invalid User ID. Please enter a valid number.")

    if user_id not in SAMPLE_USER_IDS:
        return render_template('user_id_entry.html', error="User ID not found in our sample. Please try one of the sample IDs.")

    # Store user_id in session for later use
    session['user_id'] = user_id
    return redirect(url_for('main_menu'))

@app.route('/main_menu')
def main_menu():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('main_menu.html', user_id=session['user_id'])

@app.route('/search_page')
def search_page():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('search_page.html')

@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    query = request.form['query']
    search_type = request.form['search_type']

    print(f"🔎 Received query: {query} | Type: {search_type}")

    if search_type == "specific":
        lines = bm25_specific_search(query)
    else:
        lines = hybrid_general_search(query)

    if not lines:
        return render_template('results.html', results=[], message="No match found.", user_id=session['user_id'])
    return render_template('results.html', results=lines, user_id=session['user_id'])

@app.route('/must_watch')
def must_watch():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    user_id = session['user_id']
    print(f"🎯 Running RankNet for User ID: {user_id}")
    lines = recommend_movies_for_user(user_id)

    if not lines:
        return render_template('results.html', results=[], message="No recommendations found.", user_id=user_id)
    return render_template('results.html', results=lines, user_id=user_id, is_recommendation=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
