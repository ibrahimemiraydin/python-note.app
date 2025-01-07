from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMenu, QComboBox, QAction, QToolButton
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon
import database.database as database
import components.folders as folders  # Importing the module for folder management
import uuid
from components.edit_note_window import EditNoteWindow
from components.trash_window import TrashWindow
from components.completed_window import CompletedWindow
from App import ui
from App import context_menu
from App import notes

class NoteApp(QWidget):
    notes_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_folder_id = None
        self.folder_history = []  # Stack to store the IDs of previously visited folders
        self.initUI()
        self.apply_stylesheet()
        self.notes_updated.connect(self.load_notes)

    def initUI(self):
        self.setWindowTitle('Notefier')
        self.resize(1000, 800)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        self.prev_button = ui.create_button('', "icons/back_icon.png")  # Using back icon to go back
        self.prev_button.clicked.connect(self.go_back)  # Go to the previous page
        top_layout.addWidget(self.prev_button)

        self.home_button = ui.create_button('', "icons/home_icon.png")  # Using home icon to go to the home page
        self.home_button.clicked.connect(self.go_to_home)
        top_layout.addWidget(self.home_button)

        self.search_bar = ui.create_search_bar(self)
        self.search_bar.textChanged.connect(self.filter_notes)
        top_layout.addWidget(self.search_bar)

        self.filter_box = ui.create_filter_box(self)
        if self.filter_box.count() == 0:  # Ensure the filter box is populated only once
            self.filter_box.addItem("All")
            self.filter_box.addItem("Title")
        self.filter_box.currentIndexChanged.connect(self.filter_notes)
        top_layout.addWidget(self.filter_box)

        self.new_note_button = ui.create_button('', "icons/new_note_icon.png")
        self.new_note_button.clicked.connect(self.new_note)
        top_layout.addWidget(self.new_note_button)

        self.new_folder_button = ui.create_button('', "icons/new_folder_icon.png")
        self.new_folder_button.clicked.connect(self.new_folder)
        top_layout.addWidget(self.new_folder_button)

        self.trash_button = ui.create_button('', "icons/trash_icon.png")
        self.trash_button.clicked.connect(self.show_trash)
        top_layout.addWidget(self.trash_button)

        self.completed_button = ui.create_button('', "icons/completed_icon.png")
        self.completed_button.clicked.connect(self.show_completed)
        top_layout.addWidget(self.completed_button)

        main_layout.addLayout(top_layout)

        self.note_list = QListWidget()
        self.note_list.setDragDropMode(QListWidget.InternalMove)
        self.note_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.note_list.customContextMenuRequested.connect(self.context_menu)
        self.note_list.itemClicked.connect(self.handle_item_click)
        self.note_list.itemDoubleClicked.connect(self.open_folder)
        self.note_list.setMinimumWidth(600)
        self.note_list.itemChanged.connect(self.rename_note_finished)
        main_layout.addWidget(self.note_list)

        self.setLayout(main_layout)

    def apply_stylesheet(self):
        with open('styles/styles.qss', 'r') as f:
            stylesheet = f.read()
            self.setStyleSheet(stylesheet)

    def context_menu(self, position):
        item = self.note_list.itemAt(position)
        context_menu.create_context_menu(
            self, position,
            self.new_note,
            self.new_folder,
            self.load_notes,
            self.rename_note_item,
            self.trash_item,
            self.complete_item,
            self.move_item
        )

    def load_notes(self, filter_text="", folder_id=None):
        self.note_list.clear()
        if folder_id is not None:
            if self.current_folder_id is not None:
                self.folder_history.append(self.current_folder_id)  # Push the current folder ID to the stack
            self.current_folder_id = folder_id
        self.load_folder(filter_text, self.current_folder_id)
        self.load_folders(filter_text, self.current_folder_id)

    def filter_notes(self):
        filter_text = self.search_bar.text()
        self.load_notes(filter_text, self.current_folder_id)

    def handle_item_click(self, item):
        if item.data(Qt.UserRole) and str(item.data(Qt.UserRole)).startswith('note_'):
            self.load_note(item)

    def load_note(self, item):
        note_id = item.data(Qt.UserRole)
        if note_id and str(note_id).startswith('note_'):
            note = database.get_note_by_id(note_id)
            if note is not None:
                self.edit_note_window = EditNoteWindow(note_id, note[2], self)
                if self.edit_note_window.exec_():
                    updated_content = self.edit_note_window.content
                    database.update_note_content(note_id, updated_content)
                    self.notes_updated.emit()
            else:
                print(f"Note not found (ID: {note_id})")

    def load_folder(self, filter_text, folder_id):
        notes.load_notes(self.note_list, self.filter_box, filter_text, folder_id)

    def load_folders(self, filter_text, parent_folder_id):
        notes.load_folders(self.note_list, self.filter_box, filter_text, parent_folder_id)

    def go_back(self):
        if self.folder_history:
            self.current_folder_id = self.folder_history.pop()  # Pop the last folder ID from the stack
            self.load_notes()
        else:
            self.go_to_home()  # If stack is empty, go to the home page

    def go_to_home(self):
        self.folder_history.clear()  # Clear the stack
        self.load_all_notes()

    def new_note(self):
        note_id = database.add_note("New Note", "", self.current_folder_id)
        self.notes_updated.emit()

        # Immediately rename the new note
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            if item and item.data(Qt.UserRole) == note_id:
                self.rename_note_item(item)
                break

    def rename_note_item(self, item):
        self.line_edit = QLineEdit(self.note_list)
        self.line_edit.setText(item.text())
        self.note_list.setItemWidget(item, self.line_edit)
        self.line_edit.setFocus()
        self.line_edit.editingFinished.connect(lambda: self.finish_rename(item, self.line_edit))

    def finish_rename(self, item, line_edit):
        new_title = line_edit.text()
        if new_title:
            if str(item.data(Qt.UserRole)).startswith('folder_'):
                folder_id = item.data(Qt.UserRole)
                folders.update_folder_name(folder_id, new_title)
            elif str(item.data(Qt.UserRole)).startswith('note_'):
                note_id = item.data(Qt.UserRole)
                database.update_note_title(note_id, new_title)
        self.note_list.setItemWidget(item, None)
        self.notes_updated.emit()

    def rename_note_finished(self, item):
        self.finish_rename(item, QLineEdit(self.note_list))

    def trash_item(self, item):
        if str(item.data(Qt.UserRole)).startswith('note_'):
            note_id = item.data(Qt.UserRole)
            database.trash_note(note_id)
        elif str(item.data(Qt.UserRole)).startswith('folder_'):
            folder_id = item.data(Qt.UserRole)
            folders.trash_folder(folder_id)
        self.notes_updated.emit()

    def complete_item(self, item):
        if item.data(Qt.UserRole) and str(item.data(Qt.UserRole)).startswith('note_'):
            note_id = item.data(Qt.UserRole)
            database.complete_note(note_id)
            self.notes_updated.emit()

    def new_folder(self):
        folder_id = folders.add_folder("New Folder", self.current_folder_id)
        self.notes_updated.emit()

        # Immediately rename the new folder
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            if item and item.data(Qt.UserRole) == folder_id:
                self.rename_note_item(item)
                break

    def move_item(self, dest_folder_id):
        selected_items = self.note_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            if str(item.data(Qt.UserRole)).startswith('note_'):
                note_id = item.data(Qt.UserRole)
                database.move_note_to_folder(note_id, dest_folder_id)
            elif str(item.data(Qt.UserRole)).startswith('folder_'):
                src_folder_id = item.data(Qt.UserRole)
                folders.move_folder_to_folder(src_folder_id, dest_folder_id)
            self.notes_updated.emit()

    def show_trash(self):
        trash_window = TrashWindow(self)
        trash_window.note_restored.connect(self.update_note_list)
        trash_window.exec_()
        self.update_note_list()

    def show_completed(self):
        completed_notes = database.get_completed_notes()
        completed_window = CompletedWindow(completed_notes, self)
        completed_window.note_uncompleted.connect(self.update_note_list)
        completed_window.exec_()
        self.update_note_list()

    def update_note_list(self):
        self.load_notes("", self.current_folder_id)

    def load_all_notes(self):
        self.current_folder_id = None
        self.load_notes()

    def open_folder(self, item):
        if str(item.data(Qt.UserRole)).startswith('folder_'):
            folder_id = item.data(Qt.UserRole)
            self.load_notes(folder_id=folder_id)
