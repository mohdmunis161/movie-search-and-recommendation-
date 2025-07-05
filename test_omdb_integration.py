#!/usr/bin/env python3
"""
Test script for OMDB API integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.omdb_poster import get_movie_poster, get_movie_details

def test_omdb_integration():
    """Test OMDB API integration"""
    print("🧪 Testing OMDB API Integration...")
    
    # Test movies with different formats
    test_movies = [
        "Spider-Man: Into the Spider-Verse (2018)",
        "The Dark Knight (2008)",
        "Inception (2010)",
        "Avatar (2009)",
        "Titanic (1997)"
    ]
    
    for i, movie_title in enumerate(test_movies, 1):
        print(f"\n📊 Test {i}: '{movie_title}'")
        
        try:
            # Test poster fetching
            poster_url = get_movie_poster(movie_title)
            if poster_url:
                print(f"✅ Poster URL: {poster_url}")
            else:
                print("⚠️  No poster found")
            
            # Test detailed info fetching
            details = get_movie_details(movie_title)
            if details:
                print(f"✅ Movie Details:")
                print(f"   Title: {details.get('title')}")
                print(f"   Year: {details.get('year')}")
                print(f"   Rating: {details.get('rating')}")
                print(f"   Genre: {details.get('genre')}")
            else:
                print("⚠️  No details found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎯 Testing with your API key...")
    try:
        # Test with the exact format from your example
        test_url = "http://www.omdbapi.com/?t=Spider-Man&y=2018&apikey=64357812"
        import requests
        response = requests.get(test_url)
        data = response.json()
        
        if data.get('Response') == 'True':
            print("✅ API key works correctly!")
            print(f"   Movie: {data.get('Title')} ({data.get('Year')})")
            print(f"   Poster: {data.get('Poster')}")
        else:
            print(f"❌ API error: {data.get('Error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_omdb_integration() 