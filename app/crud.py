from app.database import get_db_connection

def create_user(name: str, email: str, password: str, role: str = "user"):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, role))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {
        "id": user_id,
        "name": name,
        "email": email,
        "role": role
    }


def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    conn.close()
    return user




def get_or_create_author(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM authors WHERE name = ?", (name,))
    author = cursor.fetchone()

    if author:
        conn.close()
        return author["id"]

    cursor.execute("INSERT INTO authors (name) VALUES (?)", (name,))
    conn.commit()
    author_id = cursor.lastrowid
    conn.close()

    return author_id


# CATEGORY FUNCTIONS

def get_or_create_category(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories WHERE name = ?", (name,))
    category = cursor.fetchone()

    if category:
        conn.close()
        return category["id"]

    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()

    return category_id


# BOOK FUNCTIONS

def create_book(title: str, author: str, category: str, total_copies: int):
    author_id = get_or_create_author(author)
    category_id = get_or_create_category(category)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO books (title, author_id, category_id, total_copies, available_copies)
        VALUES (?, ?, ?, ?, ?)
    """, (title, author_id, category_id, total_copies, total_copies))

    conn.commit()
    book_id = cursor.lastrowid
    conn.close()

    return {
        "id": book_id,
        "title": title,
        "author": author,
        "category": category,
        "available_copies": total_copies
    }


def get_all_books():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT books.id, books.title, authors.name AS author, categories.name AS category,
               books.available_copies
        FROM books
        JOIN authors ON books.author_id = authors.id
        JOIN categories ON books.category_id = categories.id
    """)

    books = cursor.fetchall()
    conn.close()

    return [dict(book) for book in books]


def search_books(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = f"%{query}%"

    cursor.execute("""
        SELECT books.id, books.title, authors.name AS author, categories.name AS category,
               books.available_copies
        FROM books
        JOIN authors ON books.author_id = authors.id
        JOIN categories ON books.category_id = categories.id
        WHERE books.title LIKE ? OR authors.name LIKE ? OR categories.name LIKE ?
    """, (search_term, search_term, search_term))

    books = cursor.fetchall()
    conn.close()

    return [dict(book) for book in books]