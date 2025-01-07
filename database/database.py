import sqlite3
import uuid
from components.folders import restore_folder

# Mevcut fonksiyonlarınızı koruyun ve altına ekleyin
def create_database():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()

    # Folders tablosunu güncelleme
    c.execute('''CREATE TABLE IF NOT EXISTS folders (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    notes_id TEXT,
                    trashed INTEGER DEFAULT 0,
                    foldered INTEGER DEFAULT 0,
                    parent_folder_id TEXT DEFAULT "",
                    "order" INTEGER DEFAULT 0)''')
    try:
        c.execute('ALTER TABLE folders ADD COLUMN "order" INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Sütun zaten varsa hatayı yoksay

    # Notes tablosunu güncelleme
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    trashed INTEGER DEFAULT 0,
                    completed INTEGER DEFAULT 0,
                    foldered INTEGER DEFAULT 0,
                    folder_id TEXT DEFAULT "",
                    "order" INTEGER DEFAULT 0)''')
    try:
        c.execute('ALTER TABLE notes ADD COLUMN "order" INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Sütun zaten varsa hatayı yoksay

    conn.commit()
    conn.close()

# Yeni fonksiyon olarak ekleyin
def get_items_in_folder(folder_id=None):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()

    if folder_id is None:
        query = '''
            SELECT id, name, "order", 'folder' as type
            FROM folders
            WHERE (parent_folder_id IS NULL OR parent_folder_id = '')
            AND trashed = 0
            UNION
            SELECT id, title as name, "order", 'note' as type
            FROM notes
            WHERE folder_id = ''
            AND trashed = 0
            AND completed = 0
            ORDER BY "order" ASC
        '''
        c.execute(query)
    else:
        query = '''
            SELECT id, name, "order", 'folder' as type
            FROM folders
            WHERE parent_folder_id = ?
            AND trashed = 0
            UNION
            SELECT id, title as name, "order", 'note' as type
            FROM notes
            WHERE folder_id = ?
            AND trashed = 0
            AND completed = 0
            ORDER BY "order" ASC
        '''
        c.execute(query, (folder_id, folder_id))
    
    items = c.fetchall()
    conn.close()
    return items

def get_max_order_in_folder(folder_id=None):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    if folder_id is None:
        c.execute('''
            SELECT MAX("order") FROM (
                SELECT "order" FROM folders WHERE (parent_folder_id IS NULL OR parent_folder_id = '') AND trashed = 0
                UNION ALL
                SELECT "order" FROM notes WHERE folder_id = '' AND trashed = 0 AND completed = 0
            )
        ''')
    else:
        c.execute('''
            SELECT MAX("order") FROM (
                SELECT "order" FROM folders WHERE parent_folder_id = ? AND trashed = 0
                UNION ALL
                SELECT "order" FROM notes WHERE folder_id = ? AND trashed = 0 AND completed = 0
            )
        ''', (folder_id, folder_id))
    
    max_order = c.fetchone()[0]
    conn.close()
    return max_order if max_order is not None else 0

def add_note(title, content, folder_id=None):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    note_id = f'note_{uuid.uuid4()}'
    max_order = get_max_order_in_folder(folder_id) + 1
    c.execute('INSERT INTO notes (id, title, content, folder_id, "order") VALUES (?, ?, ?, ?, ?)', 
              (note_id, title, content, folder_id if folder_id else '', max_order))
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
        query += ' ORDER BY "order" ASC'
        c.execute(query, (folder_id,))
    else:
        query += ' ORDER BY "order" ASC'
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
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    folder_id = f'folder_{uuid.uuid4()}'
    max_order = get_max_order_in_folder(parent_folder_id) + 1
    c.execute('INSERT INTO folders (id, name, parent_folder_id, "order") VALUES (?, ?, ?, ?)',
              (folder_id, name, parent_folder_id if parent_folder_id else '', max_order))
    conn.commit()
    conn.close()
    return folder_id

def get_folders(include_trashed=False):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    query = 'SELECT * FROM folders WHERE 1=1'
    if not include_trashed:
        query += ' AND trashed=0'
    query += ' ORDER BY "order" ASC'  # Sıralama ekleme
    c.execute(query)
    folders = c.fetchall()
    conn.close()
    return folders

def get_folders_in_folder(parent_folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM folders WHERE parent_folder_id=? AND trashed=0 AND foldered=1 ORDER BY "order" ASC', (parent_folder_id,))
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
    max_order = get_max_order_in_folder(dest_folder_id) + 1
    foldered = 1 if dest_folder_id else 0
    if dest_folder_id is None:
        dest_folder_id = ""
    c.execute('UPDATE folders SET parent_folder_id=?, foldered=?, "order"=? WHERE id=?', (dest_folder_id, foldered, max_order, src_folder_id))
    conn.commit()
    conn.close()


def move_note_to_folder(note_id, folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    max_order = get_max_order_in_folder(folder_id) + 1
    foldered = 1 if folder_id else 0
    if folder_id is None:
        folder_id = ""
    c.execute('UPDATE notes SET folder_id=?, foldered=?, "order"=? WHERE id=?', (folder_id, foldered, max_order, note_id))
    conn.commit()
    conn.close()

def get_notes_in_folder(folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, title, content FROM notes WHERE folder_id=? AND trashed=0 AND completed=0 AND foldered=1 ORDER BY "order" ASC', (folder_id,))
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

def update_note_order(note_id, order):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE notes SET "order"=? WHERE id=?', (order, note_id))
    conn.commit()
    conn.close()
