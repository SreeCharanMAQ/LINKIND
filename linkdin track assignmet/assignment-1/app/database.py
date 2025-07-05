import sqlite3
from contextlib import contextmanager

DATABASE_URL = "users.db"

def init_db():
    with sqlite3.connect(DATABASE_URL.replace("sqlite:///", "")) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                picture TEXT,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                author_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(author_id) REFERENCES users(id)
            )
        """)
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
def create_or_update_user(google_id: str, name: str, email: str, picture: str = None):
    """Create a new user or update existing user in the database"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE google_id = ?", (google_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET name = ?, email = ?, picture = ?, updated_at = CURRENT_TIMESTAMP
                WHERE google_id = ?
            """, (name, email, picture, google_id))
            user_id = existing_user[0]
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users (google_id, name, email, picture) 
                VALUES (?, ?, ?, ?)
            """, (google_id, name, email, picture))
            user_id = cursor.lastrowid

        conn.commit()
        return user_id
