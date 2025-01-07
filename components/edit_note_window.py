from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QToolBar, QAction, QFontComboBox, QComboBox, QColorDialog, QFileDialog, QMenu, QInputDialog
from PyQt5.QtGui import QTextCursor, QFont, QIcon, QColor, QPixmap, QTextListFormat
from PyQt5.QtCore import Qt, QTimer
import database.database as database

class EditNoteWindow(QDialog):
    def __init__(self, note_id=None, content='', parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self.content = content
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Edit Note')
        self.resize(800, 600)  # Set window size

        layout = QVBoxLayout()

        self.toolbar = QToolBar(self)
        layout.addWidget(self.toolbar)

        self.text_edit = QTextEdit(self)
        self.text_edit.setHtml(self.content)  # Set content as HTML
        self.text_edit.textChanged.connect(self.auto_save)  # Connect auto-save function
        layout.addWidget(self.text_edit)

        self.create_toolbar()

        self.setLayout(layout)

    def create_toolbar(self):
        # Stylized dropdown menu for font selection
        font_box = QFontComboBox(self)
        font_box.setStyleSheet("""
            QFontComboBox {
                min-width: 150px;
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QFontComboBox QAbstractItemView {
                min-width: 150px;
                font-size: 14px;
            }
        """)
        font_box.currentFontChanged.connect(self.set_font)
        self.toolbar.addWidget(font_box)

        # Custom stylized dropdown menu for font size selection
        font_size_box = QComboBox(self)
        font_size_box.setEditable(True)
        font_size_box.addItems([str(i) for i in range(8, 30, 2)])
        font_size_box.setStyleSheet("""
            QComboBox {
                min-width: 75px;
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
        font_size_box.currentIndexChanged.connect(self.set_font_size)
        self.toolbar.addWidget(font_size_box)

        # Text color selection
        color_action = QAction(QIcon('icons/color.png'), 'Choose Color', self)
        color_action.triggered.connect(self.set_color)
        self.toolbar.addAction(color_action)

        # Background color selection
        bgcolor_action = QAction(QIcon('icons/bgcolor.png'), 'Choose Background Color', self)
        bgcolor_action.triggered.connect(self.set_bgcolor)
        self.toolbar.addAction(bgcolor_action)

        self.toolbar.addSeparator()

        # Bold text
        bold_action = QAction(QIcon('icons/bold.png'), 'Bold', self)
        bold_action.triggered.connect(self.set_bold)
        self.toolbar.addAction(bold_action)

        # Italic text
        italic_action = QAction(QIcon('icons/italic.png'), 'Italic', self)
        italic_action.triggered.connect(self.set_italic)
        self.toolbar.addAction(italic_action)

        # Underlined text
        underline_action = QAction(QIcon('icons/underline.png'), 'Underline', self)
        underline_action.triggered.connect(self.set_underline)
        self.toolbar.addAction(underline_action)

        self.toolbar.addSeparator()

        # Dropdown menu for headers
        header_menu = QMenu('Headers', self)
        h1_action = QAction(QIcon('icons/h1.png'), 'H1', self)
        h1_action.triggered.connect(lambda: self.set_header(1))
        header_menu.addAction(h1_action)

        h2_action = QAction(QIcon('icons/h2.png'), 'H2', self)
        h2_action.triggered.connect(lambda: self.set_header(2))
        header_menu.addAction(h2_action)

        h3_action = QAction(QIcon('icons/h3.png'), 'H3', self)
        h3_action.triggered.connect(lambda: self.set_header(3))
        header_menu.addAction(h3_action)

        h4_action = QAction(QIcon('icons/h4.png'), 'H4', self)
        h4_action.triggered.connect(lambda: self.set_header(4))
        header_menu.addAction(h4_action)

        h5_action = QAction(QIcon('icons/h5.png'), 'H5', self)
        h5_action.triggered.connect(lambda: self.set_header(5))
        header_menu.addAction(h5_action)

        h6_action = QAction(QIcon('icons/h6.png'), 'H6', self)
        h6_action.triggered.connect(lambda: self.set_header(6))
        header_menu.addAction(h6_action)

        header_action = QAction(QIcon('icons/header.png'), 'Headers', self)
        header_action.setMenu(header_menu)
        self.toolbar.addAction(header_action)

        self.toolbar.addSeparator()

        # Bullet list
        bullet_list_action = QAction(QIcon('icons/bullet_list.png'), 'Bullet List', self)
        bullet_list_action.triggered.connect(self.set_bullet_list)
        self.toolbar.addAction(bullet_list_action)

        # Numbered list
        numbered_list_action = QAction(QIcon('icons/numbered_list.png'), 'Numbered List', self)
        numbered_list_action.triggered.connect(self.set_numbered_list)
        self.toolbar.addAction(numbered_list_action)

        self.toolbar.addSeparator()

        # Alignment options
        align_left_action = QAction(QIcon('icons/align_left.png'), 'Align Left', self)
        align_left_action.triggered.connect(lambda: self.text_edit.setAlignment(Qt.AlignLeft))
        self.toolbar.addAction(align_left_action)

        align_center_action = QAction(QIcon('icons/align_center.png'), 'Align Center', self)
        align_center_action.triggered.connect(lambda: self.text_edit.setAlignment(Qt.AlignCenter))
        self.toolbar.addAction(align_center_action)

        align_right_action = QAction(QIcon('icons/align_right.png'), 'Align Right', self)
        align_right_action.triggered.connect(lambda: self.text_edit.setAlignment(Qt.AlignRight))
        self.toolbar.addAction(align_right_action)

        align_justify_action = QAction(QIcon('icons/align_justify.png'), 'Justify', self)
        align_justify_action.triggered.connect(lambda: self.text_edit.setAlignment(Qt.AlignJustify))
        self.toolbar.addAction(align_justify_action)

        self.toolbar.addSeparator()

        # Add Link
        link_action = QAction(QIcon('icons/link.png'), 'Add Link', self)
        link_action.triggered.connect(self.add_link)
        self.toolbar.addAction(link_action)

        self.toolbar.addSeparator()

        # Add Image
        image_action = QAction(QIcon('icons/image.png'), 'Add Image', self)
        image_action.triggered.connect(self.add_image)
        self.toolbar.addAction(image_action)

        self.toolbar.addSeparator()

        # Superscript
        superscript_action = QAction(QIcon('icons/superscript.png'), 'Superscript', self)
        superscript_action.triggered.connect(lambda: self.set_script('sup'))
        self.toolbar.addAction(superscript_action)

        # Subscript
        subscript_action = QAction(QIcon('icons/subscript.png'), 'Subscript', self)
        subscript_action.triggered.connect(lambda: self.set_script('sub'))
        self.toolbar.addAction(subscript_action)

    def set_font(self, font):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFont(font)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def set_font_size(self):
        size = self.sender().currentText()
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontPointSize(float(size))
        self.text_edit.mergeCurrentCharFormat(fmt)

    def set_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = self.text_edit.currentCharFormat()
            fmt.setForeground(color)
            self.text_edit.mergeCurrentCharFormat(fmt)

    def set_bgcolor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = self.text_edit.currentCharFormat()
            fmt.setBackground(color)
            self.text_edit.mergeCurrentCharFormat(fmt)

    def set_bold(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if fmt.fontWeight() != QFont.Bold else QFont.Normal)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def set_italic(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.text_edit.mergeCurrentCharFormat(fmt)

    def set_underline(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.text_edit.mergeCurrentCharFormat(fmt)

    def set_header(self, level):
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.BlockUnderCursor)
        header = f'<h{level}>{cursor.selectedText()}</h{level}>'
        cursor.insertHtml(header)
        cursor.movePosition(QTextCursor.EndOfBlock)
        self.text_edit.setTextCursor(cursor)

    def set_bullet_list(self):
        cursor = self.text_edit.textCursor()
        cursor.insertList(QTextListFormat.ListDisc)

    def set_numbered_list(self):
        cursor = self.text_edit.textCursor()
        cursor.insertList(QTextListFormat.ListDecimal)

    def add_link(self):
        cursor = self.text_edit.textCursor()
        link, ok = QInputDialog.getText(self, 'Add Link', 'URL:')
        if ok and link:
            cursor.insertHtml(f'<a href="{link}">{cursor.selectedText()}</a>')

    def add_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, 'Add Image', '', 'Image Files (*.png *.jpg *.bmp)')
        if image_path:
            cursor = self.text_edit.textCursor()
            cursor.insertHtml(f'<img src="{image_path}" />')

    def set_script(self, script_type):
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        text = cursor.selectedText()
        if script_type == 'sup':
            cursor.insertHtml(f'<sup>{text}</sup>')
        elif script_type == 'sub':
            cursor.insertHtml(f'<sub>{text}</sub>')
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def auto_save(self):
        self.content = self.text_edit.toHtml()  # Get content as HTML
        if self.note_id:
            database.update_note_content(self.note_id, self.content)  # Update the note

    def set_bold(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if fmt.fontWeight() != QFont.Bold else QFont.Normal)
        self.text_edit.mergeCurrentCharFormat(fmt)
