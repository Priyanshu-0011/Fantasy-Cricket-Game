import sqlite3
import os

def setup_database():
    DB_PATH = 'fantasy_cricket.db'

    # Check if database already exists
    if os.path.exists(DB_PATH):
        print("⚠️ Database already exists.")
        return

    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE stats (
        player TEXT PRIMARY KEY,
        matches INTEGER,
        runs INTEGER,
        hundreds INTEGER,
        fifties INTEGER,
        value INTEGER,
        ctg TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE match (
        player TEXT PRIMARY KEY,
        scored INTEGER,
        faced INTEGER,
        fours INTEGER,
        sixes INTEGER,
        bowled INTEGER,
        maiden INTEGER,
        given INTEGER,
        wkts INTEGER,
        catches INTEGER,
        stumping INTEGER,
        ro INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE teams (
        name TEXT,
        players TEXT,
        value INTEGER
    )
    """)

    # Sample data
    stats_data = [
        ("Virat Kohli", 250, 12000, 43, 60, 9, "BAT"),
        ("Jasprit Bumrah", 120, 200, 0, 0, 8, "BWL"),
        ("MS Dhoni", 350, 10500, 10, 65, 10, "WK"),
        ("Hardik Pandya", 100, 1500, 0, 3, 9, "AR"),
    ]

    match_data = [
        ("Virat Kohli", 80, 60, 8, 2, 0, 0, 0, 0, 0, 0, 0),
        ("Jasprit Bumrah", 5, 7, 1, 0, 10, 2, 30, 3, 0, 0, 0),
        ("MS Dhoni", 45, 40, 4, 1, 0, 0, 0, 0, 2, 1, 0),
        ("Hardik Pandya", 30, 25, 2, 2, 4, 0, 20, 1, 1, 0, 1),
    ]

    # Insert sample data
    cursor.executemany("INSERT INTO stats VALUES (?, ?, ?, ?, ?, ?, ?)", stats_data)
    cursor.executemany("INSERT INTO match VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", match_data)

    # Commit and close
    conn.commit()
    conn.close()
    print("✅ Database setup complete.")

if __name__ == '__main__':
    setup_database()
