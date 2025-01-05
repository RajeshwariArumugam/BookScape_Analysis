import mysql.connector
import json

# Database configuration
db_config = {
    "host": "localhost",  # Replace with your host name
    "user": "root",       # Replace with your username
    "password": "Password",  # Replace with your password
    "database": "bookscape_explore"  # Replace with your database name
}

def connect_database():
    """
    Establishes a connection to the database.

    Returns:
        connection: The database connection object.
    """
    return mysql.connector.connect(**db_config)

def create_tables():
    """
    Creates the `books` table in the database if it doesn't already exist.
    """
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

def insert_books_data(books, search_key):
    """
    Inserts books data into the database.

    Args:
        books (list): List of books data fetched from the API.
        search_key (str): The search term used to fetch the books.
    """
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

def fetch_books_from_db(query):
    """
    Fetches data from the database based on the query.

    Args:
        query (str): SQL query to fetch the data.

    Returns:
        list: The fetched data as a list of dictionaries.
    """
    try:
        connection = connect_database()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
