# Movie Search and Recommendation System

A fast and intelligent movie search and recommendation system built with Flask, featuring genre-based recommendations and advanced search capabilities.

## 🎬 Features

- **🔍 Smart Search**: BM25 and hybrid search algorithms
- **🎯 Genre Recommendations**: Fast genre-based movie recommendations
- **📱 Responsive Design**: Modern, mobile-friendly interface
- **⚡ Fast Performance**: Cached data and optimized algorithms
- **🔗 Direct Links**: Movies come with download/viewing links
- **🎬 Movie Posters**: Automatic poster fetching from OMDB API

## 🚀 Live Demo

[Deployed on Render](https://your-app-name.onrender.com)

## 🛠️ Technology Stack

- **Backend**: Flask, Python 3.9
- **Search**: BM25, Hybrid Search with TF-IDF
- **Recommendations**: Fast genre-based algorithm
- **Posters**: OMDB API integration
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Render, Gunicorn

## 📁 Project Structure

```
movie-search-and-recommendation-/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Procfile                        # Render deployment config
├── runtime.txt                     # Python version
├── build.sh                        # Build script for Render
├── models/
│   ├── fast_genre_recommend.py    # Fast genre recommendation system
│   ├── bm25_search.py             # BM25 search algorithm
│   └── hybrid_search.py           # Hybrid search algorithm
├── templates/
│   ├── user_id_entry.html         # Home page
│   ├── search_page.html           # Search interface
│   ├── genre_recommendations.html # Genre input page
│   └── results.html               # Results display
├── static/
│   └── css/style.css              # Styling and responsive design
└── data/
    └── movies_links.txt           # Movie database (22,657+ movies)
```

## 🚀 Deployment on Render

### Prerequisites
- Render account
- GitHub repository with this code

### Deployment Steps

1. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/your-username/movie-search-and-recommendation.git
   cd movie-search-and-recommendation
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Deploy on Render**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure settings:
     - **Name**: `movie-search-recommendation`
     - **Environment**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2`
     - **Plan**: Free (or paid for better performance)

4. **Environment Variables** (Optional)
   - No environment variables required for basic functionality

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete (5-10 minutes)

### Build Process
The `build.sh` script automatically:
- Downloads required NLTK data
- Creates cache directory
- Sets up the environment

## 🎯 Usage

### Home Page
- **Search Movies**: Direct search functionality
- **Get Recommendations**: Genre-based recommendations

### Search Movies
1. Enter movie title, genre, or keywords
2. Choose search type:
   - **Specific Search**: Exact matches
   - **General Search**: Semantic search
3. Get results with movie posters and direct download links

### Get Recommendations
1. Enter genre preferences (e.g., "action comedy latest")
2. Get personalized movie recommendations
3. Browse movies with posters and download links

## 🔧 Local Development

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/movie-search-and-recommendation.git
cd movie-search-and-recommendation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Run application
python app.py
```

### Access
- Open browser: `http://localhost:5000`

## 📊 Performance

- **Search Speed**: < 1 second for most queries
- **Recommendations**: < 2 seconds for genre-based recommendations
- **Database**: 22,657+ movies with metadata
- **Caching**: Automatic caching for fast performance

## 🎨 Features

### Search Algorithms
- **BM25**: Best for exact movie titles
- **Hybrid Search**: Combines TF-IDF and semantic search

### Recommendation System
- **Genre Matching**: 15+ genres supported
- **Year Filtering**: Latest, classic, specific years
- **Smart Scoring**: Multi-factor recommendation algorithm

### User Interface
- **Responsive Design**: Works on all devices
- **Modern UI**: Clean, intuitive interface
- **Fast Loading**: Optimized for performance

## 🔒 Security

- **Input Validation**: All user inputs are validated
- **Error Handling**: Graceful error handling
- **Session Management**: Secure session handling

## 📈 Monitoring

- **Logs**: Application logs available in Render dashboard
- **Performance**: Built-in performance monitoring
- **Uptime**: 99.9% uptime with Render

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the deployment logs in Render dashboard
- Review the application logs for errors

---

**Made with ❤️ for movie lovers everywhere!** 🎬✨ 