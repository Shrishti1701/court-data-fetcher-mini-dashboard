import sqlite3

def init_db():
    conn = sqlite3.connect("queries.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_type TEXT,
            case_number TEXT,
            filing_year TEXT,
            raw_html TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_query(case_type, case_number, filing_year, raw_html):
    conn = sqlite3.connect("queries.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO queries (case_type, case_number, filing_year, raw_html) VALUES (?, ?, ?, ?)",
                   (case_type, case_number, filing_year, raw_html))
    query_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return query_id

def get_query_by_id(query_id):
    conn = sqlite3.connect("queries.db")
    cursor = conn.cursor()
    cursor.execute("SELECT raw_html FROM queries WHERE id = ?", (query_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
