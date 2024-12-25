# Full Implementation Code for BookScape Explorer

# 1. Data Extraction (Google Books API)
import requests
import mysql.connector
import json
from time import sleep
import streamlit as st
import pandas as pd
import random

# Google Books API configuration
API_URL = "https://www.googleapis.com/books/v1/volumes"
API_KEY = "AIzaSyD4DEOE9JTYHR-MO9Wq0qHmDmyqi7l_VUM"

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "789456123",
    "database": "bookscape_explore"
}

def connect_database():
    connection = mysql.connector.connect(**db_config)
    return connection

def create_tables():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id VARCHAR(255) PRIMARY KEY,
        search_key VARCHAR(255),
        book_title VARCHAR(255),
        book_subtitle TEXT,
        book_authors TEXT,
        book_description TEXT,
        industryIdentifiers TEXT,
        text_readingModes BOOLEAN,
        image_readingModes BOOLEAN,
        pageCount INT,
        categories TEXT,
        language VARCHAR(10),
        imageLinks TEXT,
        ratingsCount INT,
        averageRating DECIMAL(3,2),
        country VARCHAR(10),
        saleability VARCHAR(50),
        isEbook BOOLEAN,
        amount_listPrice DECIMAL(10,2),
        currencyCode_listPrice VARCHAR(10),
        amount_retailPrice DECIMAL(10,2),
        currencyCode_retailPrice VARCHAR(10),
        buyLink TEXT,
        year TEXT
    );
    """)
    connection.commit()
    cursor.close()
    connection.close()

# Fetch data from Google Books API
def fetch_books_data(search_term, max_results=1000):
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
            print("Error fetching data")
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        books.extend(items)
        start_index += 40
        sleep(1)  # Rate limiting

    return books

# Insert data into the database
def insert_books_data(books, search_key):
    connection = connect_database()
    cursor = connection.cursor()

    for book in books:
        volume_info = book.get("volumeInfo", {})
        sale_info = book.get("saleInfo", {})

        book_data = (
            book.get("id"),
            search_key,
            volume_info.get("title"),
            volume_info.get("subtitle"),
            json.dumps(volume_info.get("authors")),
            volume_info.get("description"),
            json.dumps(volume_info.get("industryIdentifiers")),
            volume_info.get("readingModes", {}).get("text"),
            volume_info.get("readingModes", {}).get("image"),
            volume_info.get("pageCount"),
            json.dumps(volume_info.get("categories")),
            volume_info.get("language"),
            json.dumps(volume_info.get("imageLinks")),
            volume_info.get("ratingsCount"),
            volume_info.get("averageRating"),
            sale_info.get("country"),
            sale_info.get("saleability"),
            sale_info.get("isEbook"),
            sale_info.get("listPrice", {}).get("amount"),
            sale_info.get("listPrice", {}).get("currencyCode"),
            sale_info.get("retailPrice", {}).get("amount"),
            sale_info.get("retailPrice", {}).get("currencyCode"),
            sale_info.get("buyLink"),
            volume_info.get("publishedDate")
        )

        try:
            cursor.execute("""
            INSERT INTO books VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE book_title=VALUES(book_title);
            """, book_data)
        except mysql.connector.Error as e:
            print(f"Error inserting data: {e}")

    connection.commit()
    cursor.close()
    connection.close()

# Fetch books from database
def fetch_books_from_db(query):
    try:
        connection = connect_database()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result
    except mysql.connector.Error as e:
        st.error(f"Error fetching data: {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return []

# Main script
if __name__ == "__main__":
    create_tables()
    search_keyword = "Book_World"
    books = fetch_books_data(search_keyword)
    insert_books_data(books, search_keyword)

# 2. Streamlit Application
# Streamlit setup
import streamlit as st
import requests

# Function to load Lottie animations
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Streamlit App Configuration
st.set_page_config(page_title="BookScape Explorer", layout="wide")
st.title("📚 BookScape Explorer")

# Sidebar Menu
st.sidebar.header("Navigate")
menu = ["Home", "Explore!", "Need Help?"]
choice = st.sidebar.radio("Choose a page:", menu)

# Lottie Animation URL
lottie_animation_url = "https://assets2.lottiefiles.com/packages/lf20_kkflmtur.json"  # Replace with any Lottie animation URL
lottie_animation = load_lottie_url(lottie_animation_url)

if choice == "Home":
    # Home Page with Animation
    st.header("Welcome to BookScape Explorer! 🌟")
    st.subheader("Discover, Explore, and Analyze Books with Ease")
    # Two-column layout for text and animation
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Why You'll Love BookScape Explorer:
        - 📚 Explore a vast collection of books.
        - 🔍 Search by title, author, or genre.
        - 🌟 Analyze books with advanced tools.
        
        Get started by navigating through the sidebar. Whether you're a bookworm or a casual reader, BookScape Explorer is the perfect place to begin your literary adventure! 🚀
        """)
    with col2:
        from streamlit_lottie import st_lottie
        st_lottie(lottie_animation, height=300, key="welcome_animation")

    st.markdown("---")
    st.info("📖 **Tip:** Use the 'Explore!' tab to start your journey!")

elif choice == "Search Books":
    st.header("Search Books by Title, Author, or Publisher")

    col1, col2, col3 = st.columns(3)
    with col1:
        search_title = st.text_input("Search by Title")
    with col2:
        search_author = st.text_input("Search by Author")
    with col3:
        search_publisher = st.text_input("Search by Publisher")

    # Query construction based on user input
    query = "SELECT * FROM books WHERE 1=1"
    if search_title:
        query += f" AND book_title LIKE '%{search_title}%'"
    if search_author:
        query += f" AND book_authors LIKE '%{search_author}%'"
    if search_publisher:
        query += f" AND book_description LIKE '%{search_publisher}%'"

    # Fetching data from the database based on the constructed query
    books_df = pd.DataFrame(fetch_books_from_db(query))

    if not books_df.empty:
        st.dataframe(books_df)
    else:
        st.write("No books found.")

elif choice == "Explore!":
    st.header("🔍 Search and Explore Books")
    
    # Columns for searching by Title, Author, or Publisher
    col1, col2, col3 = st.columns(3)
    with col1:
        search_title = st.text_input("Search by Title")
    with col2:
        search_author = st.text_input("Search by Author")
    with col3:
        search_publisher = st.text_input("Search by Publisher")
    
    # Query construction based on user input
    query = "SELECT * FROM books WHERE 1=1"
    if search_title:
        query += f" AND book_title LIKE '%{search_title}%'"
    if search_author:
        query += f" AND book_authors LIKE '%{search_author}%'"
    if search_publisher:
        query += f" AND book_description LIKE '%{search_publisher}%'"

    # Fetching data from the database based on the constructed query
    books_df = pd.DataFrame(fetch_books_from_db(query))

    # Display results
    if not books_df.empty:
        st.subheader("Search Results")
        st.dataframe(books_df)
    else:
        st.write("No books found.")
    
    st.markdown("---")

elif choice == "Need Help?":
    st.header("Run Predefined Queries")

    queries = {
        "Availability of eBooks vs Physical Books": "SELECT isEbook, COUNT(*) AS count FROM books GROUP BY isEbook",
        "Top 5 Most Expensive Books": "SELECT book_title, amount_retailPrice FROM books ORDER BY amount_retailPrice DESC LIMIT 5",
        "Books Published After 2010 with At Least 500 Pages": "SELECT book_title, pageCount FROM books WHERE year > '2010' AND pageCount >= 500",
        "Books with Discounts Greater than 20%": "SELECT book_title, amount_listPrice, amount_retailPrice FROM books WHERE amount_listPrice > 0 AND (amount_listPrice - amount_retailPrice) / amount_listPrice > 0.2",
        "Average Page Count for eBooks vs Physical Books": "SELECT isEbook, AVG(pageCount) AS avg_page_count FROM books GROUP BY isEbook",
        "Top 3 Authors with Most Books": "SELECT JSON_EXTRACT(book_authors, '$[0]') AS author, COUNT(*) AS count FROM books GROUP BY author ORDER BY count DESC LIMIT 3",
        "Publishers with More Than 10 Books": "SELECT JSON_EXTRACT(book_description, '$') AS publisher, COUNT(*) AS count FROM books GROUP BY publisher HAVING count > 10",
        "Average Page Count for Each Category": "SELECT JSON_UNQUOTE(JSON_EXTRACT(categories, '$[0]')) AS category, AVG(pageCount) AS avg_page_count FROM books GROUP BY category",
        "Books with More Than 3 Authors": "SELECT book_title, JSON_LENGTH(book_authors) AS author_count FROM books WHERE JSON_LENGTH(book_authors) > 3",
        "Books with Ratings Greater Than Average": "SELECT book_title, averageRating FROM books WHERE averageRating > (SELECT AVG(averageRating) FROM books)",
        "Books by Same Author Published in Same Year": "SELECT JSON_EXTRACT(book_authors, '$[0]') AS author, year, COUNT(*) AS book_count FROM books GROUP BY author, year HAVING book_count > 1",
        "Books with Specific Keyword in Title": "SELECT book_title FROM books WHERE book_title LIKE '%specific keyword%'",
        "Year with Highest Average Book Price": "SELECT year, AVG(amount_retailPrice) AS avg_price FROM books GROUP BY year ORDER BY avg_price DESC LIMIT 1",
        "Count of Authors Who Published 3 Consecutive Years": "SELECT JSON_EXTRACT(book_authors, '$[0]') AS author, COUNT(DISTINCT year) AS years FROM books GROUP BY author HAVING years >= 3",
        "Authors with Books Published Under Different Publishers": "SELECT JSON_EXTRACT(book_authors, '$[0]') AS author, year, COUNT(DISTINCT JSON_EXTRACT(book_description, '$')) AS publishers FROM books GROUP BY author, year HAVING publishers > 1",
        "Average Retail Price of eBooks vs Physical Books": "SELECT isEbook, AVG(amount_retailPrice) AS avg_price FROM books GROUP BY isEbook",
        "Outlier Books Based on Ratings": "SELECT book_title, averageRating, ratingsCount FROM books WHERE averageRating > (SELECT AVG(averageRating) + 2 * STDDEV(averageRating) FROM books)",
        "Publisher with Highest Average Rating (More Than 10 Books)": "SELECT JSON_EXTRACT(book_description, '$') AS publisher, AVG(averageRating) AS avg_rating, COUNT(*) AS book_count FROM books GROUP BY publisher HAVING book_count > 10 ORDER BY avg_rating DESC LIMIT 1"
    }

    query_choice = st.selectbox("Choose a Query", list(queries.keys()))
    
    if query_choice:
        query = queries[query_choice]
        results = pd.DataFrame(fetch_books_from_db(query))
        if not results.empty:
            st.dataframe(results)
        else:
            st.write("No results found.")
