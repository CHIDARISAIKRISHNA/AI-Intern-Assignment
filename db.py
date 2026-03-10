import sqlite3
DB_NAME = "incidents.db"
def create_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source TEXT,
        severity TEXT,
        raw_text TEXT
    )
    """)
    conn.commit()
    conn.close()
def insert_event(timestamp, source, severity, raw_text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (timestamp, source, severity, raw_text) VALUES (?, ?, ?, ?)",
        (timestamp, source, severity, raw_text)
    )
    conn.commit()
    conn.close()

def get_recent_events(window_seconds=30):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT timestamp, source, severity, raw_text
    FROM events
    WHERE timestamp >= datetime('now', ?)
    ORDER BY timestamp DESC
    """, (f"-{window_seconds} seconds",))
    rows = cursor.fetchall()
    conn.close()
    return rows