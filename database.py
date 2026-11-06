import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE_FILE = Path(__file__).with_name("stocklens.db")

@contextmanager
def get_connection():
    """Open a SQLite connection, commit on success, roll back on error, always close."""
    connection = sqlite3.connect(DATABASE_FILE)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def create_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                tickers TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL
            )
        """)

def save_comparison(name, tickers, start, end):
    if isinstance(tickers, str):
        tickers = [tickers]  # # Wrap a single string in a list so it doesn't get split into individual characters
    ticker_to_text = ",".join(tickers)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO comparisons (name, tickers, start_date, end_date)
            VALUES (?, ?, ?, ?)
            """,
            (name, ticker_to_text, start, end),
        )
        return cursor.lastrowid

def get_saved_comparisons():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, name, tickers, start_date, end_date
            FROM comparisons
            ORDER BY id DESC
        """).fetchall()
    return [
        {
            "id": row[0],
            "name": row[1],
            "tickers": [t for t in row[2].split(",") if t],
            "start": row[3],
            "end": row[4],
        }
        for row in rows
    ]

def delete_comparison(comparison_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM comparisons WHERE id = ?",
            (comparison_id,),
        )
        return cursor.rowcount > 0

if __name__ == "__main__":
    create_table()
    print("Database and comparisons table are ready.")