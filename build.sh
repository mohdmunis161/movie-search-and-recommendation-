#!/usr/bin/env bash
# Build script for Render deployment

echo "🚀 Starting build process..."

# Download NLTK data
echo "📥 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Create cache directory if it doesn't exist
echo "📁 Creating cache directory..."
mkdir -p cache

echo "✅ Build process completed!" 