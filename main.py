import sqlite3
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import database.database as database
from App.note_app import NoteApp

if __name__ == '__main__':
    database.create_database()

    # Update database to add folder_id column to notes table
    def update_database():
        conn = sqlite3.connect('notes.db')
        c = conn.cursor()
        try:
            c.execute('ALTER TABLE notes ADD COLUMN folder_id TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.close()

    update_database()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons/app_icon.png'))
    ex = NoteApp()
    ex.show()
    ex.load_notes()
    sys.exit(app.exec_())
