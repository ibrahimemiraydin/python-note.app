from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon
import database.database as database
import components.folders as folders  # Importing the module for folder management

class TrashWindow(QDialog):
    note_restored = pyqtSignal()  # Signal for restoring a note

    def __init__(self, parent=None):
        super(TrashWindow, self).__init__(parent)
        self.setWindowTitle('Recycle bin')
        self.resize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.trash_list = QListWidget()
        layout.addWidget(self.trash_list)

        button_layout = QHBoxLayout()

        self.restore_button = QPushButton(' Restore')
        self.restore_button.setIcon(QIcon("icons/restore_icon.png"))  # Add icon for restore
        self.restore_button.clicked.connect(self.restore_note_or_folder)  # Updated function name
        button_layout.addWidget(self.restore_button)

        self.delete_button = QPushButton(' Permanently Delete')
        self.delete_button.setIcon(QIcon("icons/delete_icon.png"))  # Add icon for permanent delete
        self.delete_button.clicked.connect(self.delete_note_permanently)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.load_trashed_notes()

    def load_trashed_notes(self):
        self.trash_notes = database.get_trashed_notes()
        self.trash_folders = folders.get_trashed_folders()  # Called from `folders` module
        self.trash_list.clear()

        note_icon = QIcon("icons/note_icon.png")
        folder_icon = QIcon("icons/folder_icon.png")

        # Add notes in trash
        for note in self.trash_notes:
            item = QListWidgetItem(note_icon, note[1])
            item.setData(Qt.UserRole, note[0])
            item.setSizeHint(QSize(300, 35))
            self.trash_list.addItem(item)

        # Add folders in trash
        for folder in self.trash_folders:
            item = QListWidgetItem(folder_icon, folder[1])
            item.setData(Qt.UserRole, folder[0])
            item.setSizeHint(QSize(300, 35))
            self.trash_list.addItem(item)

    def restore_note_or_folder(self):
        item = self.trash_list.currentItem()
        if item:
            item_id = item.data(Qt.UserRole)
            database.restore_note_or_folder(item_id)  # Restore the note or folder
            self.note_restored.emit()  # Emit the restore signal
            self.trash_list.takeItem(self.trash_list.row(item))

    def delete_note_permanently(self):
        item = self.trash_list.currentItem()
        if item:
            item_id = item.data(Qt.UserRole)
            if item_id.startswith('note_'):
                database.delete_note_permanently(item_id)  # Permanently delete the note
            elif item_id.startswith('folder_'):
                folders.delete_folder(item_id)  # Permanently delete the folder and its contents
            self.trash_list.takeItem(self.trash_list.row(item))
