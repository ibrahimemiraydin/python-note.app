import sqlite3

def get_db_connection():
    conn = sqlite3.connect('notes.db')
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at TEXT NOT NULL)''')  # created_at sütunu eklendi
    conn.commit()
    conn.close()

init_db()