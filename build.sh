#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Download NLTK data if needed
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" 