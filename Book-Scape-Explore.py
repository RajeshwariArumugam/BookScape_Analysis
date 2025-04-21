import requests
import mysql.connector
import json
from time import sleep
import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie

API_URL = "https://www.googleapis.com/books/v1/volumes"
API_KEY = "replace it with api key"

db_config = {
    "host": "localhost", 
    "user": "root",
    "password": "789456123",
    "database": "books_db1"
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
        year TEXT,
        publisher TEXT           
    );
    """)
    connection.commit()
    cursor.close()
    connection.close()

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
            print(f"Error fetching data: {response.status_code}")
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        books.extend(items)
        start_index += 40
        
        # Break if we've reached max_results or there are no more results
        if len(books) >= max_results or len(items) < 40:
            break
            
        sleep(1)  # Rate limiting

    return books[:max_results]  # Ensure we don't exceed max_results

def insert_books_data(books, search_key):
    connection = connect_database()
    cursor = connection.cursor()
    inserted_count = 0

    for book in books:
        volume_info = book.get("volumeInfo", {})
        sale_info = book.get("saleInfo", {})

        book_data = (
            book.get("id"),
            search_key,  # Store the search key with each book
            volume_info.get("title"),
            volume_info.get("subtitle"),
            json.dumps(volume_info.get("authors") or []),  # Handle None values
            volume_info.get("description"),
            json.dumps(volume_info.get("industryIdentifiers") or []),
            volume_info.get("readingModes", {}).get("text"),
            volume_info.get("readingModes", {}).get("image"),
            volume_info.get("pageCount"),
            json.dumps(volume_info.get("categories") or []),
            volume_info.get("language"),
            json.dumps(volume_info.get("imageLinks") or {}),
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
            volume_info.get("publishedDate"),
            volume_info.get("publisher")
        )

        try:
            cursor.execute("""
            INSERT INTO books VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE search_key=VALUES(search_key), book_title=VALUES(book_title);
            """, book_data)
            inserted_count += 1
        except mysql.connector.Error as e:
            print(f"Error inserting data: {e}")

    connection.commit()
    cursor.close()
    connection.close()
    return inserted_count

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

# Function to process book data for display
def process_books_for_display(books):
    processed_books = []
    for book in books:
        volume_info = book.get("volumeInfo", {})
        sale_info = book.get("saleInfo", {})
        
        processed_book = {
            "book_id": book.get("id"),
            "book_title": volume_info.get("title", "Unknown Title"),
            "book_authors": volume_info.get("authors", []),
            "publisher": volume_info.get("publisher", "Unknown"),
            "publishedDate": volume_info.get("publishedDate", "Unknown"),
            "pageCount": volume_info.get("pageCount", 0),
            "categories": volume_info.get("categories", []),
            "language": volume_info.get("language", "Unknown"),
            "averageRating": volume_info.get("averageRating", 0),
            "isEbook": sale_info.get("isEbook", False),
            "saleability": sale_info.get("saleability", "Unknown"),
            "description": volume_info.get("description", "No description available")
        }
        processed_books.append(processed_book)
    
    return processed_books

# Function to load Lottie animations
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Main function
def main():
    # Initialize database
    create_tables()
    
    # Streamlit App Configuration
    st.set_page_config(page_title="BookScape Explorer", layout="wide")
    st.title("📚 BookScape Explorer")
    st.sidebar.header("Navigate")
    
    # Menu options
    menu = ["Home", "Explore!", "Need Help?"]
    choice = st.sidebar.radio("Choose a page:", menu)

    lottie_animation_url = "https://assets2.lottiefiles.com/packages/lf20_kkflmtur.json"
    lottie_animation = load_lottie_url(lottie_animation_url)

    if choice == "Home":
        st.header("Welcome to BookScape Explorer! 🌟")
        st.subheader("Discover, Explore, and Analyze Books with Ease")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### Why You'll Love BookScape Explorer:
            - 📚 Explore a vast collection of books.
            - 🔍 Search by title, author, or genre.
            - 📥 Fetch books directly from Google Books API.
            - 🌟 Analyze books with advanced tools.
            
            Get started by navigating through the sidebar. Whether you're a bookworm or a casual reader, BookScape Explorer is the perfect place to begin your literary adventure! 🚀
            """)
        with col2:
            st_lottie(lottie_animation, height=300, key="welcome_animation")

        st.markdown("---")
        st.info("📖 **Tip:** Use the 'Explore!' tab to search for books and fetch them directly from Google Books API!")

    elif choice == "Explore!":
        st.header("🔍 Search and Explore Books")
        
        # Create two tabs for different search modes
        search_tab, api_tab = st.tabs(["Search Database", "Fetch from API"])
        
        with search_tab:
            st.subheader("Search Existing Books")
            # Database search form
            col1, col2 = st.columns(2)
            with col1:
                search_title = st.text_input("Search by Title", key="db_title")
                search_author = st.text_input("Search by Author", key="db_author")
            with col2:
                search_publisher = st.text_input("Search by Publisher", key="db_publisher")
                search_key = st.text_input("Search by Search Key", key="db_search_key")
            
            # Query construction based on user input
            query = "SELECT * FROM books WHERE 1=1"
            if search_title:
                query += f" AND book_title LIKE '%{search_title}%'"
            if search_author:
                query += f" AND book_authors LIKE '%{search_author}%'"
            if search_publisher:
                query += f" AND publisher LIKE '%{search_publisher}%'"
            if search_key:
                query += f" AND search_key LIKE '%{search_key}%'"

            # Add a limit to prevent overwhelming results
            query += " LIMIT 1000"
            
            # Add a button to execute the search
            if st.button("Search Database"):
                with st.spinner("Fetching books from database..."):
                    books_df = pd.DataFrame(fetch_books_from_db(query))

                    if not books_df.empty:
                        st.subheader(f"Search Results: {len(books_df)} books found")
                        st.dataframe(books_df)
                    else:
                        st.warning("No books found matching your criteria.")
            
            # Display available search keys
            st.markdown("---")
            st.subheader("Available Search Keys")
            search_keys_query = "SELECT search_key, COUNT(*) as book_count FROM books GROUP BY search_key ORDER BY book_count DESC"
            search_keys_df = pd.DataFrame(fetch_books_from_db(search_keys_query))
            if not search_keys_df.empty:
                st.dataframe(search_keys_df)
            else:
                st.info("No search keys found in the database yet. Use the 'Fetch from API' tab to add books with search keys.")
        
        with api_tab:
            st.subheader("Fetch Books from Google Books API")
            
            # API search form
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("Search Key (e.g., fiction, python)", key="api_search_term")
            with col2:
                max_results = st.slider("Maximum Books to Fetch", min_value=10, max_value=1000, value=100, step=10)
            
            # Checkbox to save to database
            save_to_db = st.checkbox("Save search results to database", value=True)
            
            if st.button("Search Google Books API"):
                if not search_term:
                    st.warning("Please enter a search term")
                else:
                    with st.spinner(f"Fetching books for '{search_term}' from Google Books API..."):
                        try:
                            books = fetch_books_data(search_term, max_results)
                            if books:
                                st.success(f"Found {len(books)} books for '{search_term}'")
                                
                                # Process books for display
                                processed_books = process_books_for_display(books)
                                books_df = pd.DataFrame(processed_books)
                                
                                # Display the results
                                st.dataframe(books_df)
                                
                                # Save to database if requested
                                if save_to_db:
                                    with st.spinner("Saving books to database..."):
                                        # Display a progress bar
                                        progress_bar = st.progress(0)
                                        batch_size = min(10, len(books))
                                        
                                        inserted_count = 0
                                        for i in range(0, len(books), batch_size):
                                            batch = books[i:i+batch_size]
                                            inserted_count += insert_books_data(batch, search_term)
                                            progress = min(1.0, (i + batch_size) / len(books))
                                            progress_bar.progress(progress)
                                        
                                        # Complete the progress bar
                                        progress_bar.progress(1.0)
                                        st.success(f"Successfully stored {inserted_count} books with search key '{search_term}' in the database!")
                            else:
                                st.warning(f"No books found for '{search_term}'")
                        except Exception as e:
                            st.error(f"Error fetching books: {e}")

    elif choice == "Need Help?":
        st.header("Run Predefined Queries")
        
        queries = {
            "Availability of eBooks vs Physical Books": "SELECT COALESCE(isEbook, 0) AS book_type, COUNT(*) AS count FROM books GROUP BY COALESCE(isEbook, 0)",
            "Top 5 Most Expensive Books": "SELECT DISTINCT book_title, amount_retailPrice FROM books WHERE amount_retailPrice IS NOT NULL ORDER BY amount_retailPrice DESC LIMIT 5",
            "Books Published After 2010 with At Least 500 Pages": "SELECT DISTINCT book_title, COALESCE(pageCount, 0) AS pageCount FROM books WHERE year > '2010' AND COALESCE(pageCount, 0) >= 500",
            "Books with Discounts Greater than 20%": "SELECT DISTINCT book_title, amount_listPrice, amount_retailPrice FROM books WHERE amount_listPrice > 0 AND amount_retailPrice IS NOT NULL AND (amount_listPrice - amount_retailPrice) / amount_listPrice > 0.2",
            "Average Page Count for eBooks vs Physical Books": "SELECT COALESCE(isEbook, 0) AS book_type, AVG(COALESCE(pageCount, 0)) AS avg_page_count FROM books GROUP BY COALESCE(isEbook, 0)",
            "Top 3 Authors with Most Books": "SELECT JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]')) AS author, COUNT(*) AS count FROM books WHERE JSON_VALID(book_authors) = 1 AND JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]')) IS NOT NULL AND LOWER(JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]'))) NOT IN ('null', 'unknown') GROUP BY author ORDER BY count DESC LIMIT 3",            
            "Average Page Count for Each Category": "SELECT COALESCE(JSON_UNQUOTE(JSON_EXTRACT(categories, '$[0]')), 'Uncategorized') AS category, AVG(COALESCE(pageCount, 0)) AS avg_page_count FROM books WHERE JSON_VALID(categories) = 1 OR categories IS NULL GROUP BY COALESCE(JSON_UNQUOTE(JSON_EXTRACT(categories, '$[0]')), 'Uncategorized')",
            "Books with More Than 3 Authors": "SELECT DISTINCT book_title, JSON_LENGTH(book_authors) AS author_count FROM books WHERE JSON_VALID(book_authors) = 1 AND JSON_LENGTH(book_authors) > 3",
            "Books with Ratings Greater Than Average": "SELECT DISTINCT book_title, averageRating FROM books WHERE averageRating IS NOT NULL AND averageRating > (SELECT AVG(averageRating) FROM books WHERE averageRating IS NOT NULL)",
            "Books by Same Author Published in Same Year": "WITH author_years AS (SELECT CASE WHEN JSON_EXTRACT(book_authors, '$[0]') IS NULL THEN 'UNKNOWN' WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]'))) = 'null' THEN 'UNKNOWN' WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]'))) = 'unknown' THEN 'UNKNOWN' ELSE JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]')) END AS author, year, COUNT(*) AS book_count FROM books WHERE (JSON_VALID(book_authors) = 1 OR book_authors IS NULL) AND year IS NOT NULL GROUP BY author, year HAVING book_count > 1) SELECT author, year, book_count FROM author_years ORDER BY book_count DESC LIMIT 0, 1000",
            "Books with Specific Keyword in Title": "SELECT DISTINCT book_title FROM books WHERE book_title LIKE '%{keyword}%'",
            "Year with Highest Average Book Price": "SELECT COALESCE(year, 'Unknown') AS year, AVG(COALESCE(amount_retailPrice, 0)) AS avg_price FROM books WHERE amount_retailPrice IS NOT NULL GROUP BY COALESCE(year, 'Unknown') ORDER BY avg_price DESC LIMIT 1",
            "Count of Authors Who Published 3 Consecutive Years": "WITH author_years AS (SELECT DISTINCT CASE WHEN JSON_EXTRACT(book_authors, '$[0]') IS NULL THEN 'UNKNOWN' WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]'))) = 'null' THEN 'UNKNOWN' WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]'))) = 'unknown' THEN 'UNKNOWN' ELSE JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]')) END AS author, year FROM books WHERE (JSON_VALID(book_authors) = 1 OR book_authors IS NULL) AND year IS NOT NULL) SELECT author, COUNT(DISTINCT year) AS years FROM author_years WHERE author != 'UNKNOWN' GROUP BY author HAVING years >= 3 LIMIT 0, 1000",
            "Authors with Books Published Under Different Publishers": "WITH author_publishers AS (SELECT DISTINCT CASE WHEN author IS NULL THEN 'UNKNOWN' WHEN LOWER(author) = 'null' THEN 'UNKNOWN' WHEN LOWER(author) = 'unknown' THEN 'UNKNOWN' ELSE author END AS author, publisher, year FROM (SELECT JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[0]')) AS author, publisher, year FROM books WHERE (JSON_VALID(book_authors) = 1 OR book_authors IS NULL) AND publisher IS NOT NULL AND year IS NOT NULL UNION ALL SELECT JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[1]')) AS author, publisher, year FROM books WHERE JSON_VALID(book_authors) = 1 AND publisher IS NOT NULL AND year IS NOT NULL AND JSON_EXTRACT(book_authors, '$[1]') IS NOT NULL UNION ALL SELECT JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[2]')) AS author, publisher, year FROM books WHERE JSON_VALID(book_authors) = 1 AND publisher IS NOT NULL AND year IS NOT NULL AND JSON_EXTRACT(book_authors, '$[2]') IS NOT NULL UNION ALL SELECT JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[3]')) AS author, publisher, year FROM books WHERE JSON_VALID(book_authors) = 1 AND publisher IS NOT NULL AND year IS NOT NULL AND JSON_EXTRACT(book_authors, '$[3]') IS NOT NULL UNION ALL SELECT JSON_UNQUOTE(JSON_EXTRACT(book_authors, '$[4]')) AS author, publisher, year FROM books WHERE JSON_VALID(book_authors) = 1 AND publisher IS NOT NULL AND year IS NOT NULL AND JSON_EXTRACT(book_authors, '$[4]') IS NOT NULL) AS authors_data) SELECT author, year, COUNT(DISTINCT publisher) AS publishers_count FROM author_publishers WHERE author != 'UNKNOWN' GROUP BY author, year HAVING publishers_count > 1 ORDER BY publishers_count DESC",
            "Average Retail Price of eBooks vs Physical Books": "SELECT AVG(CASE WHEN isEbook = 1 THEN COALESCE(amount_retailPrice, 0) ELSE NULL END) AS avg_ebook_price, AVG(CASE WHEN COALESCE(isEbook, 0) = 0 THEN COALESCE(amount_retailPrice, 0) ELSE NULL END) AS avg_physical_price FROM books WHERE amount_retailPrice IS NOT NULL",
            "Outlier Books Based on Ratings": "WITH rating_stats AS (SELECT AVG(averageRating) AS avg_rating, STDDEV(averageRating) AS std_rating FROM books WHERE averageRating IS NOT NULL) SELECT DISTINCT book_title, averageRating, COALESCE(ratingsCount, 0) AS ratingsCount FROM books, rating_stats WHERE averageRating IS NOT NULL AND (averageRating > (avg_rating + 2 * std_rating) OR averageRating < (avg_rating - 2 * std_rating))",
            "Top 5 Most Expensive Books by Retail Price": "SELECT DISTINCT book_title, amount_retailPrice FROM books WHERE amount_retailPrice IS NOT NULL ORDER BY amount_retailPrice DESC LIMIT 5",
            "Identify the Publisher with the Highest Average Rating": "SELECT COALESCE(publisher, 'Unknown') AS publisher, AVG(COALESCE(averageRating, 0)) AS avg_rating, COUNT(*) AS book_count FROM books GROUP BY COALESCE(publisher, 'Unknown') HAVING book_count > 10 AND avg_rating > 0 ORDER BY avg_rating DESC LIMIT 1",
            "Find the Publisher with the Most Books Published": "SELECT publisher, COUNT(*) AS book_count FROM books WHERE publisher IS NOT NULL AND LOWER(publisher) NOT IN ('null', 'unknown') GROUP BY publisher ORDER BY book_count DESC LIMIT 1",
            "Books with Ratings Count Greater Than the Average": "SELECT DISTINCT book_title, ratingsCount FROM books WHERE ratingsCount IS NOT NULL AND ratingsCount > (SELECT AVG(ratingsCount) FROM books WHERE ratingsCount IS NOT NULL) ORDER BY ratingsCount DESC"
        }
        
        query_choice = st.selectbox("Choose a Query", list(queries.keys()))
        
        # Only show the keyword search input when the specific query is selected
        title_keyword = "  "  # Default value
        if query_choice == "Books with Specific Keyword in Title":
            title_keyword = st.text_input("Enter keyword to search in book titles:", "  ")
        
        if query_choice:
            with st.spinner("Running query..."):
                # Process the query based on the selection
                if query_choice == "Books with Specific Keyword in Title":
                    query = queries[query_choice].format(keyword=title_keyword)
                else:
                    query = queries[query_choice]
                    
                results = pd.DataFrame(fetch_books_from_db(query))
                if not results.empty:
                    st.dataframe(results)
                else:
                    st.warning("No results found.")

if __name__ == "__main__":
    main()
