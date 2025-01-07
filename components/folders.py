import sqlite3
import uuid
import database.database as database

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

def get_folders(include_trashed=False, only_root=False):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    query = 'SELECT * FROM folders WHERE 1=1'
    if not include_trashed:
        query += ' AND trashed=0'
    if only_root:
        query += ' AND (parent_folder_id IS NULL OR parent_folder_id="")'
    query += ' ORDER BY "order" ASC'
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
    
    # First, delete subfolders and their notes
    c.execute('SELECT id FROM folders WHERE parent_folder_id=?', (folder_id,))
    subfolders = c.fetchall()
    for subfolder in subfolders:
        delete_folder(subfolder[0])
    
    # Delete notes in the folder
    c.execute('SELECT id FROM notes WHERE folder_id=?', (folder_id,))
    notes_in_folder = c.fetchall()
    for note in notes_in_folder:
        database.delete_note_permanently(note[0])
    
    # Then delete the folder itself
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
    
    # First, move subfolders to trash
    c.execute('SELECT id FROM folders WHERE parent_folder_id=?', (folder_id,))
    subfolders = c.fetchall()
    for subfolder in subfolders:
        trash_folder(subfolder[0])
    
    # Move notes in the folder to trash
    c.execute('UPDATE notes SET trashed=1 WHERE folder_id=?', (folder_id,))
    
    # Then move the folder to trash
    c.execute('UPDATE folders SET trashed=1 WHERE id=?', (folder_id,))
    conn.commit()
    conn.close()

def get_trashed_folders():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM folders WHERE trashed=1')
    folders = c.fetchall()
    conn.close()
    return folders

def restore_folder(folder_id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('SELECT parent_folder_id FROM folders WHERE id=?', (folder_id,))
    result = c.fetchone()
    if result:
        parent_folder_id = result[0]
        if parent_folder_id:
            c.execute('SELECT trashed FROM folders WHERE id=?', (parent_folder_id,))
            parent_folder_trashed = c.fetchone()
            if parent_folder_trashed is None or parent_folder_trashed[0] == 1:
                # If the parent folder does not exist or is trashed, restore the folder in the root directory
                c.execute('UPDATE folders SET trashed=0, foldered=0, parent_folder_id="" WHERE id=?', (folder_id,))
            else:
                # If the parent folder exists, restore the folder in the respective parent folder
                c.execute('UPDATE folders SET trashed=0 WHERE id=?', (folder_id,))
        else:
            # If the folder has no parent folder, restore it in the root directory
            c.execute('UPDATE folders SET trashed=0, foldered=0, parent_folder_id="" WHERE id=?', (folder_id,))
    else:
        # If the folder is not found, restore it in the root directory
        c.execute('UPDATE folders SET trashed=0, foldered=0, parent_folder_id="" WHERE id=?', (folder_id,))
    conn.commit()
    conn.close()

def update_folder_order(folder_id, order):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('UPDATE folders SET "order"=? WHERE id=?', (order, folder_id))
    conn.commit()
    conn.close()
