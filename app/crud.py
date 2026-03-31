from app.database import get_db_connection
from datetime import date, datetime, timedelta

BORROW_DAYS = 14
FINE_PER_DAY = 5.0

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


def get_user_by_id(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
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


def borrow_book(user_id: int, book_id: int):
    today = date.today()
    due_date = today + timedelta(days=BORROW_DAYS)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None, "user_not_found"

    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return None, "book_not_found"

    if book["available_copies"] <= 0:
        conn.close()
        return None, "no_copies_available"

    cursor.execute("""
        SELECT id
        FROM borrow_records
        WHERE user_id = ? AND book_id = ? AND status = 'borrowed'
    """, (user_id, book_id))
    active_record = cursor.fetchone()
    if active_record:
        conn.close()
        return None, "already_borrowed"

    cursor.execute("""
        INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date, status)
        VALUES (?, ?, ?, ?, 'borrowed')
    """, (user_id, book_id, today.isoformat(), due_date.isoformat()))
    borrow_record_id = cursor.lastrowid

    cursor.execute("""
        UPDATE books
        SET available_copies = available_copies - 1
        WHERE id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return {
        "id": borrow_record_id,
        "user_id": user_id,
        "book_id": book_id,
        "borrow_date": today.isoformat(),
        "due_date": due_date.isoformat(),
        "status": "borrowed"
    }, None


def calculate_fine_amount(due_date_str: str, return_date_str: str):
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()

    overdue_days = (return_date - due_date).days
    if overdue_days <= 0:
        return 0.0

    return float(overdue_days * FINE_PER_DAY)


def return_book(user_id: int, book_id: int):
    return_date = date.today().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None, "user_not_found"

    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return None, "book_not_found"

    cursor.execute("""
        SELECT *
        FROM borrow_records
        WHERE user_id = ? AND book_id = ? AND status = 'borrowed'
        ORDER BY id DESC
        LIMIT 1
    """, (user_id, book_id))
    record = cursor.fetchone()

    if not record:
        conn.close()
        return None, "active_borrow_not_found"

    fine_amount = calculate_fine_amount(record["due_date"], return_date)

    cursor.execute("""
        UPDATE borrow_records
        SET return_date = ?, status = 'returned'
        WHERE id = ?
    """, (return_date, record["id"]))

    cursor.execute("""
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE id = ?
    """, (book_id,))

    cursor.execute("""
        INSERT OR REPLACE INTO fines (borrow_record_id, amount, paid)
        VALUES (?, ?, 0)
    """, (record["id"], fine_amount))

    conn.commit()
    conn.close()

    return {
        "borrow_record_id": record["id"],
        "book_id": book_id,
        "user_id": user_id,
        "return_date": return_date,
        "status": "returned",
        "fine_amount": fine_amount
    }, None


def get_borrow_history(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT br.id AS borrow_record_id,
               br.book_id,
               b.title,
               br.borrow_date,
               br.due_date,
               br.return_date,
               br.status
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.user_id = ?
        ORDER BY br.id DESC
    """, (user_id,))

    records = cursor.fetchall()
    conn.close()

    return [dict(record) for record in records]


def get_user_fines(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.borrow_record_id,
               br.user_id,
               br.book_id,
               b.title,
               f.amount,
               CAST(f.paid AS BOOLEAN) AS paid
        FROM fines f
        JOIN borrow_records br ON f.borrow_record_id = br.id
        JOIN books b ON br.book_id = b.id
        WHERE br.user_id = ?
        ORDER BY f.borrow_record_id DESC
    """, (user_id,))

    fines = cursor.fetchall()
    conn.close()

    return [dict(fine) for fine in fines]

def get_overdue_books():
    from datetime import date

    today = date.today().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT br.id AS borrow_record_id,
               br.user_id,
               br.book_id,
               b.title,
               br.borrow_date,
               br.due_date
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.status = 'borrowed'
        AND br.due_date < ?
    """, (today,))

    records = cursor.fetchall()
    conn.close()

    return [dict(record) for record in records]
