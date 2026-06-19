import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "collection.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            genre       TEXT,
            year        INTEGER,
            rating      REAL,
            notes       TEXT,
            date_added  TEXT DEFAULT (date('now')),
            is_current  INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection_history (
            history_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id       INTEGER,
            title         TEXT,
            genre         TEXT,
            year          INTEGER,
            rating        REAL,
            notes         TEXT,
            changed_on    TEXT DEFAULT (datetime('now')),
            change_type   TEXT
        )
    """)

    conn.commit()
    conn.close()

def add_item(title, genre, year, rating, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO collection (title, genre, year, rating, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (title, genre, year, rating, notes))
    conn.commit()
    conn.close()

def get_all_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM collection WHERE is_current = 1 ORDER BY date_added DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_item(item_id, title, genre, year, rating, notes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM collection WHERE id = ?", (item_id,))
    old = cursor.fetchone()
    if old:
        cursor.execute("""
            INSERT INTO collection_history (item_id, title, genre, year, rating, notes, change_type)
            VALUES (?, ?, ?, ?, ?, ?, 'UPDATE')
        """, (old["id"], old["title"], old["genre"], old["year"], old["rating"], old["notes"]))

    cursor.execute("""
        UPDATE collection
        SET title=?, genre=?, year=?, rating=?, notes=?
        WHERE id=?
    """, (title, genre, year, rating, notes, item_id))

    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM collection WHERE id = ?", (item_id,))
    old = cursor.fetchone()
    if old:
        cursor.execute("""
            INSERT INTO collection_history (item_id, title, genre, year, rating, notes, change_type)
            VALUES (?, ?, ?, ?, ?, ?, 'DELETE')
        """, (old["id"], old["title"], old["genre"], old["year"], old["rating"], old["notes"]))

    cursor.execute("DELETE FROM collection WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def search_items(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    like = f"%{keyword}%"
    cursor.execute("""
        SELECT * FROM collection
        WHERE is_current = 1
        AND (title LIKE ? OR genre LIKE ? OR notes LIKE ?)
        ORDER BY date_added DESC
    """, (like, like, like))
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    create_tables()
    print("Database created successfully!")
    add_item("Inception", "Sci-Fi", 2010, 9.5, "Mind-bending thriller")
    add_item("The Alchemist", "Fiction", 1988, 9.0, "Great philosophy book")
    print("Test items added!")
    items = get_all_items()
    for item in items:
        print(f"  [{item['id']}] {item['title']} ({item['year']}) - {item['genre']} - {item['rating']}/10")