import database.database as database
import components.folders as folders  # Importing the module for folder management
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
import uuid

def load_notes(note_list, filter_box, filter_text="", folder_id=None):
    note_list.clear()
    note_icon = QIcon("icons/note_icon.png")

    if folder_id is not None:
        notes = database.get_notes_in_folder(folder_id)
    else:
        notes = database.get_notes(include_foldered=False)

    for note in notes:
        if filter_box.currentText() == "All" and (filter_text.lower() in note[1].lower() or filter_text.lower() in note[2].lower()):
            item = QListWidgetItem(note_icon, note[1])
            item.setData(Qt.UserRole, note[0])
            item.setSizeHint(QSize(300, 35))
            note_list.addItem(item)
        elif filter_box.currentText() == "Title" and filter_text.lower() in note[1].lower():
            item = QListWidgetItem(note_icon, note[1])
            item.setData(Qt.UserRole, note[0])
            item.setSizeHint(QSize(300, 35))
            note_list.addItem(item)
        elif filter_box.currentText() == "Content" and filter_text.lower() in note[2].lower():
            item = QListWidgetItem(note_icon, note[1])
            item.setData(Qt.UserRole, note[0])
            item.setSizeHint(QSize(300, 35))
            note_list.addItem(item)

def load_folders(note_list, filter_box, filter_text="", parent_folder_id=None):
    folder_icon = QIcon("icons/folder_icon.png")

    if parent_folder_id is not None:
        folders_in_folder = folders.get_folders_in_folder(parent_folder_id)
    else:
        folders_in_folder = folders.get_folders(only_root=True)

    for folder in folders_in_folder:
        if filter_box.currentText() == "All" and filter_text.lower() in folder[1].lower():
            item = QListWidgetItem(folder_icon, folder[1])
            item.setData(Qt.UserRole, folder[0])
            item.setFlags(item.flags() | Qt.ItemIsEditable)  # Folders can be renamed
            item.setSizeHint(QSize(300, 35))
            note_list.addItem(item)
        elif filter_box.currentText() == "Title" and filter_text.lower() in folder[1].lower():
            item = QListWidgetItem(folder_icon, folder[1])
            item.setData(Qt.UserRole, folder[0])
            item.setFlags(item.flags() | Qt.ItemIsEditable)  # Folders can be renamed
            item.setSizeHint(QSize(300, 35))
            note_list.addItem(item)

def delete_note_permanently(self):
    item = self.trash_list.currentItem()
    if item:
        item_id = item.data(Qt.UserRole)
        if item_id.startswith('note_'):
            database.delete_note_permanently(item_id)  # Permanently delete the note
        elif item_id.startswith('folder_'):
            folders.delete_folder(item_id)  # Permanently delete the folder and its contents
        self.trash_list.takeItem(self.trash_list.row(item))

def create_new_note():
    temp_title = "New Note"
    note_id = database.add_note(temp_title, "")
    return note_id

def load_items(note_list, filter_box, filter_text="", folder_id=None):
    note_list.clear()
    note_icon = QIcon("icons/note_icon.png")
    folder_icon = QIcon("icons/folder_icon.png")

    items = database.get_items_in_folder(folder_id)
    for item in items:
        if filter_box.currentText() == "All" and filter_text.lower() in item[1].lower():
            item_widget = QListWidgetItem(folder_icon if item[3] == 'folder' else note_icon, item[1])
            item_widget.setData(Qt.UserRole, item[0])
            if item[3] == 'folder':
                item_widget.setFlags(item_widget.flags() | Qt.ItemIsEditable)  # Folders can be renamed
            item_widget.setSizeHint(QSize(300, 35))
            note_list.addItem(item_widget)
        elif filter_box.currentText() == "Title" and filter_text.lower() in item[1].lower():
            item_widget = QListWidgetItem(folder_icon if item[3] == 'folder' else note_icon, item[1])
            item_widget.setData(Qt.UserRole, item[0])
            if item[3] == 'folder':
                item_widget.setFlags(item_widget.flags() | Qt.ItemIsEditable)  # Folders can be renamed
            item_widget.setSizeHint(QSize(300, 35))
            note_list.addItem(item_widget)
