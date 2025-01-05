import requests
import json
from time import sleep

# Google Books API configuration
API_URL = "https://www.googleapis.com/books/v1/volumes"
API_KEY = "API_KEY"  # Replace it with your actual API key

def fetch_books_data(search_term, max_results=1000):
    """
    Fetches books data from the Google Books API.
    
    Args:
        search_term (str): The search term to query.
        max_results (int): Maximum number of books to fetch.

    Returns:
        list: A list of book items from the API response.
    """
    params = {
        "q": search_term,
        "key": API_KEY,
        "maxResults": 40
    }
    books = []
    start_index = 0

    while len(books) < max_results:
        params["startIndex"] = start_index
        response = requests.get(API_URL, params=params)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        books.extend(items)
        start_index += 40
        sleep(1)  # Respect API rate limits

    return books
