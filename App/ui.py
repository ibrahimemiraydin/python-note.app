from PyQt5.QtWidgets import QLineEdit, QComboBox, QPushButton
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

def create_search_bar(parent):
    search_bar = QLineEdit(parent)
    search_bar.setPlaceholderText("Search...")
    return search_bar

def create_filter_box(parent):
    filter_box = QComboBox(parent)
    filter_box.setStyleSheet("""
        QComboBox {
            min-width: 20px;
            font-size: 14px;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QComboBox QAbstractItemView {
            min-width: 75px;
            font-size: 14px;
        }
    """)
    filter_box.addItems(["All", "Title", "Content"])
    return filter_box

def create_button(text, icon_path, width=50, height=40, icon_size=30):
    button = QPushButton(text)
    button.setIcon(QIcon(icon_path))
    button.setFixedWidth(width)
    button.setFixedHeight(height)
    button.setIconSize(QSize(icon_size, icon_size))
    return button
