from database import get_db_connection
from models import Note
from datetime import datetime

def add_note(title, content):
    conn = get_db_connection()
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Şu anki tarih ve saat
    c.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)", (title, content, created_at))
    conn.commit()
    conn.close()
    print("Not başarıyla eklendi!")

def list_notes():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, content, created_at FROM notes")
    rows = c.fetchall()
    conn.close()

    # Satırları Note nesnelerine dönüştür
    notes = []
    for row in rows:
        note = Note(id=row[0], title=row[1], content=row[2], created_at=row[3])  # created_at eklendi
        notes.append(note)

    return notes  # Not listesini döndür

def delete_note(note_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    print("Not başarıyla silindi!")

def update_note(note_id, title, content):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, note_id))
    conn.commit()
    conn.close()
    print("Not başarıyla güncellendi!")
    
def get_note_by_id(note_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, content, created_at FROM notes WHERE id = ?", (note_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return Note(id=row[0], title=row[1], content=row[2], created_at=row[3])  # created_at eklendi
    return None

def update_old_notes():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM notes WHERE created_at = '1970-01-01 00:00:00'")
    old_notes = c.fetchall()

    for note_id in old_notes:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE notes SET created_at = ? WHERE id = ?", (created_at, note_id[0]))

    conn.commit()
    conn.close()

# Uygulama başladığında eski notları güncelle
update_old_notes()