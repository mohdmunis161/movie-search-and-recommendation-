# Movie Search & Recommendation App

A Flask-based web application for searching and recommending movies using advanced NLP and machine learning techniques. Powered by MovieLens data and deployable on Render.com.

---

## 🚀 Features
- **Movie Search:**
  - Specific (BM25) and General (Hybrid) search options
- **Personalized Recommendations:**
  - RankNet neural network for user-based recommendations
- **Modern UI:**
  - Responsive, mobile-friendly, and easy to use

---

## 🛠️ Project Structure
```
movie_search_app/
├── app.py
├── requirements.txt
├── Procfile
├── README.md
├── models/
├── static/
├── templates/
└── ...
```

---

## 🌐 Deploying on Render.com

### 1. **Push to GitHub**
Make sure your code is in a GitHub repository.

### 2. **Create a Render Web Service**
- Go to [https://dashboard.render.com/](https://dashboard.render.com/)
- Click **New +** → **Web Service**
- Connect your GitHub and select your repo
- Fill out:
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `gunicorn app:app`
- Click **Create Web Service**

### 3. **Wait for Build & Deploy**
- Render will build and deploy your app
- You'll get a public URL when it's ready!

---

## ⚙️ Requirements
- Python 3.8+
- See `requirements.txt` for all dependencies

---

## 📦 Notes
- The app uses MovieLens data (not included in repo for size reasons)
- For large datasets, use Render's persistent disk or upload data as part of your build process
- If you need to change the Flask app filename or variable, update the `Procfile` accordingly

---

## 📄 License
This project is for educational/demo purposes. See MovieLens data license for dataset terms. 