from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QSize, pyqtSignal  # pyqtSignal imported
from PyQt5.QtGui import QIcon
import database.database as database

class CompletedWindow(QDialog):
    note_uncompleted = pyqtSignal()  # Signal for marking a note as uncompleted

    def __init__(self, completed_notes, parent=None):
        super().__init__(parent)
        self.completed_notes = completed_notes
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Completed Notes')
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.completed_list = QListWidget()
        self.completed_list.setMinimumWidth(600)  # Increase the width of QListWidget
        for note in self.completed_notes:
            item = QListWidgetItem(note[1])
            item.setData(Qt.UserRole, note[0])
            item.setSizeHint(QSize(300, 35))
            self.completed_list.addItem(item)
        layout.addWidget(self.completed_list)

        uncomplete_button = QPushButton('Mark as Uncompleted', self)
        uncomplete_icon = QIcon("icons/uncomplete_icon.png")  # Path to the icon for Mark as Uncompleted
        uncomplete_button.setIcon(uncomplete_icon)
        uncomplete_button.setIconSize(QSize(24, 24))  # Set the icon size
        uncomplete_button.clicked.connect(self.uncomplete_note)
        layout.addWidget(uncomplete_button)

        self.setLayout(layout)

    def uncomplete_note(self):
        item = self.completed_list.currentItem()
        if item:
            note_id = item.data(Qt.UserRole)
            database.uncomplete_note(note_id)  # Mark the note as uncompleted
            self.note_uncompleted.emit()  # Emit the signal for marking the note as uncompleted
            self.completed_list.takeItem(self.completed_list.row(item))
