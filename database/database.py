import sqlite3
import uuid
from components.folders import restore_folder

def create_database():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS folders (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    notes_id TEXT,
                    trashed INTEGER DEFAULT 0,
                    foldered INTEGER DEFAULT 0,
                    parent_folder_id TEXT DEFAULT "")''')

    c.execute('''CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    trashed INTEGER DEFAULT 0,
                    completed INTEGER DEFAULT 0,
                    foldered INTEGER DEFAULT 0,
                    folder_id TEXT DEFAULT "")''')

    conn.commit()
    conn.close()

def add_note(title, content, folder_id=None):
    note_id = "note_" + str(uuid.uuid4())
    foldered = 1 if folder_id else 0
    if folder_id is None:
        folder_id = ""
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('INSERT INTO notes (id, title, content, foldered, folder_id) VALUES (?, ?, ?, ?, ?)', (note_id, title, content, foldered, folder_id))
    conn.commit()
    conn.close()
    return note_id

def update_note_title(note_id, title):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE notes SET title=? WHERE id=?', (title, note_id))
    conn.commit()
    conn.close()

def update_note_content(note_id, content):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE notes SET content=? WHERE id=?', (content, note_id))
    conn.commit()
    conn.close()

def update_note(note_id, title, content):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE notes SET title=?, content=? WHERE id=?', (title, content, note_id))
    conn.commit()
    conn.close()

def complete_note(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE notes SET completed=1 WHERE id=?', (note_id,))
    conn.commit()
    conn.close()

def uncomplete_note(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE notes SET completed=0 WHERE id=?', (note_id,))
    conn.commit()
    conn.close()

def trash_note(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE notes SET trashed=1 WHERE id=?', (note_id,))
    conn.commit()
    conn.close()

def restore_note_or_folder(item_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    if item_id.startswith('note_'):
        c.execute('SELECT folder_id FROM notes WHERE id=?', (item_id,))
        result = c.fetchone()
        if result:
            folder_id = result[0]
            if folder_id:
                c.execute('SELECT trashed FROM folders WHERE id=?', (folder_id,))
                folder_trashed = c.fetchone()
                if folder_trashed is None or folder_trashed[0] == 1:
                    # If the folder does not exist or is trashed, restore the note to the main page
                    c.execute('UPDATE notes SET trashed=0, foldered=0, folder_id="" WHERE id=?', (item_id,))
                else:
                    # If the folder exists, restore the note to the corresponding folder
                    c.execute('UPDATE notes SET trashed=0 WHERE id=?', (item_id,))
            else:
                # Restore un-foldered notes to the main page
                c.execute('UPDATE notes SET trashed=0, foldered=0, folder_id="" WHERE id=?', (item_id,))
        else:
            # If the note's folder is not found, restore the note to the main page
            c.execute('UPDATE notes SET trashed=0, foldered=0, folder_id="" WHERE id=?', (item_id,))
    elif item_id.startswith('folder_'):
        restore_folder(item_id)  # Restore the folder
    conn.commit()
    conn.close()

def delete_note_permanently(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('DELETE FROM notes WHERE id=?', (note_id,))
    conn.commit()
    conn.close()

def get_notes(include_trashed=False, include_completed=False, include_foldered=False, folder_id=None):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    query = 'SELECT id, title, content, trashed, completed, foldered, folder_id FROM notes WHERE 1=1'
    if not include_trashed:
        query += ' AND trashed=0'
    if not include_completed:
        query += ' AND completed=0'
    if not include_foldered:
        query += ' AND foldered=0'
    if folder_id is not None:
        query += ' AND folder_id=?'
        c.execute(query, (folder_id,))
    else:
        c.execute(query)
    notes = c.fetchall()
    conn.close()
    return notes

def get_trashed_notes():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, title, content, trashed, completed, foldered, folder_id FROM notes WHERE trashed=1')
    notes = c.fetchall()
    conn.close()
    return notes

def get_completed_notes():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, title, content, trashed, completed, foldered, folder_id FROM notes WHERE completed=1 AND trashed=0')
    notes = c.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM notes WHERE id=?', (note_id,))
    note = c.fetchone()
    conn.close()
    return note

def add_folder(name, parent_folder_id=None):
    new_folder_id = "folder_" + str(uuid.uuid4())
    foldered = 1 if parent_folder_id else 0
    if parent_folder_id is None:
        parent_folder_id = ""
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('INSERT INTO folders (id, name, notes_id, foldered, parent_folder_id) VALUES (?, ?, ?, ?, ?)', (new_folder_id, name, "", foldered, parent_folder_id))
    conn.commit()
    conn.close()
    return new_folder_id

def get_folders(include_trashed=False):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    query = 'SELECT * FROM folders WHERE 1=1'
    if not include_trashed:
        query += ' AND trashed=0'
    c.execute(query)
    folders = c.fetchall()
    conn.close()
    return folders

def get_folders_in_folder(parent_folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM folders WHERE parent_folder_id=? AND trashed=0 AND foldered=1', (parent_folder_id,))
    folders = c.fetchall()
    conn.close()
    return folders

def update_folder_name(folder_id, new_name):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE folders SET name=? WHERE id=?', (new_name, folder_id))
    conn.commit()
    conn.close()

def delete_folder(folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('DELETE FROM folders WHERE id=?', (folder_id,))
    conn.commit()
    conn.close()

def move_folder_to_folder(src_folder_id, dest_folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    foldered = 1 if dest_folder_id else 0
    if dest_folder_id is None:
        dest_folder_id = ""
    c.execute('UPDATE folders SET parent_folder_id=?, foldered=? WHERE id=?', (dest_folder_id, foldered, src_folder_id))
    conn.commit()
    conn.close()

def move_note_to_folder(note_id, folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    foldered = 1 if folder_id else 0
    if folder_id is None:
        folder_id = ""
    c.execute('UPDATE notes SET folder_id=?, foldered=? WHERE id=?', (folder_id, foldered, note_id))
    conn.commit()
    conn.close()

def get_notes_in_folder(folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, title, content FROM notes WHERE folder_id=? AND trashed=0 AND completed=0 AND foldered=1', (folder_id,))
    notes = c.fetchall()
    conn.close()
    return notes

def trash_folder(folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE folders SET trashed=1 WHERE id=?', (folder_id,))
    c.execute('UPDATE notes SET trashed=1 WHERE folder_id=?', (folder_id,))
    conn.commit()
    conn.close()

def get_trashed_folders():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM folders WHERE trashed=1')
    folders = c.fetchall()
    conn.close()
    return folders
