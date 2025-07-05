import requests
import re
import time
from typing import Optional, Dict, Any, Tuple

class OMDBPosterFetcher:
    """Fetch movie posters from OMDB API"""
    
    def __init__(self, api_key: str = "64357812"):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"
        self.session = requests.Session()
        # Add delay to respect API rate limits
        self.last_request_time = 0
        self.min_delay = 0.1  # 100ms between requests
    
    def extract_title_and_year(self, movie_title: str) -> Tuple[str, Optional[str]]:
        """Extract title and year from movie title string"""
        # Pattern to match year in parentheses at the end
        year_pattern = r'\((\d{4})\)'
        year_match = re.search(year_pattern, movie_title)
        
        if year_match:
            year = year_match.group(1)
            # Remove year from title
            clean_title = re.sub(year_pattern, '', movie_title).strip()
            return clean_title, year
        else:
            return movie_title.strip(), None
    
    def fetch_movie_poster(self, movie_title: str) -> Optional[str]:
        """Fetch movie poster URL from OMDB API"""
        try:
            # Respect rate limits
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_delay:
                time.sleep(self.min_delay - time_since_last)
            
            # Extract title and year
            title, year = self.extract_title_and_year(movie_title)
            
            # Prepare API request
            params = {
                't': title,
                'apikey': self.api_key
            }
            
            if year:
                params['y'] = year
            
            # Make API request
            response = self.session.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            self.last_request_time = time.time()
            
            # Check if movie found and has poster
            if data.get('Response') == 'True' and data.get('Poster'):
                poster_url = data.get('Poster')
                # Check if poster URL is valid (not N/A)
                if poster_url and poster_url != 'N/A':
                    return poster_url
            
            return None
            
        except requests.RequestException as e:
            print(f"OMDB API request failed for '{movie_title}': {e}")
            return None
        except Exception as e:
            print(f"Error fetching poster for '{movie_title}': {e}")
            return None
    
    def fetch_movie_details(self, movie_title: str) -> Optional[Dict[str, Any]]:
        """Fetch complete movie details from OMDB API"""
        try:
            # Respect rate limits
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_delay:
                time.sleep(self.min_delay - time_since_last)
            
            # Extract title and year
            title, year = self.extract_title_and_year(movie_title)
            
            # Prepare API request
            params = {
                't': title,
                'apikey': self.api_key
            }
            
            if year:
                params['y'] = year
            
            # Make API request
            response = self.session.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            self.last_request_time = time.time()
            
            # Check if movie found
            if data.get('Response') == 'True':
                return {
                    'title': data.get('Title'),
                    'year': data.get('Year'),
                    'poster': data.get('Poster') if data.get('Poster') != 'N/A' else None,
                    'plot': data.get('Plot'),
                    'rating': data.get('imdbRating'),
                    'genre': data.get('Genre'),
                    'runtime': data.get('Runtime'),
                    'director': data.get('Director')
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"OMDB API request failed for '{movie_title}': {e}")
            return None
        except Exception as e:
            print(f"Error fetching details for '{movie_title}': {e}")
            return None

# Global instance for reuse
poster_fetcher = OMDBPosterFetcher()

def get_movie_poster(movie_title: str) -> Optional[str]:
    """Get movie poster URL for a given movie title"""
    return poster_fetcher.fetch_movie_poster(movie_title)

def get_movie_details(movie_title: str) -> Optional[Dict[str, Any]]:
    """Get complete movie details for a given movie title"""
    return poster_fetcher.fetch_movie_details(movie_title) 