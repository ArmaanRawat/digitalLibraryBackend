from app.database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    # Authors table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Books table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author_id INTEGER,
        category_id INTEGER,
        total_copies INTEGER DEFAULT 1,
        available_copies INTEGER DEFAULT 1,
        FOREIGN KEY (author_id) REFERENCES authors(id),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)

    # Borrow records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        borrow_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        status TEXT DEFAULT 'borrowed',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
    """)

    # Fines table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        borrow_record_id INTEGER UNIQUE,
        amount REAL DEFAULT 0,
        paid INTEGER DEFAULT 0,
        FOREIGN KEY (borrow_record_id) REFERENCES borrow_records(id)
    )
    """)

    conn.commit()
    conn.close()