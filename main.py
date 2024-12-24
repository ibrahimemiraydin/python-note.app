import sys
import sqlite3
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QLineEdit, QMessageBox, QListWidgetItem
from PySide6.QtCore import Qt

class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Uygulaması")
        self.setGeometry(100, 100, 400, 600)

        # Veritabanı bağlantısı
        self.conn = sqlite3.connect('todo_list.db')
        self.cursor = self.conn.cursor()

        # `completed` sütunu ekleniyor (eğer yoksa)
        self.cursor.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'completed' not in columns:
            self.cursor.execute("ALTER TABLE tasks ADD COLUMN completed INTEGER DEFAULT 0")
            self.conn.commit()

        # Görevler tablosu oluşturuluyor (eğer yoksa)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               task TEXT NOT NULL,
                               completed INTEGER DEFAULT 0)''')
        self.conn.commit()

        # Ana widget ve düzen
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Görev ekleme alanı
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Bir görev ekleyin...")
        self.layout.addWidget(self.input)

        # Görev ekleme butonu
        self.add_button = QPushButton("Ekle", self)
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        # Görev listesi
        self.list_widget = QListWidget(self)
        self.layout.addWidget(self.list_widget)

        # Görev silme butonu
        self.delete_button = QPushButton("Seçili Görevi Sil", self)
        self.delete_button.clicked.connect(self.delete_task)
        self.layout.addWidget(self.delete_button)

        # Merkezi widget'ı ayarla
        self.setCentralWidget(self.central_widget)

        # Görevleri veritabanından yükle
        self.load_tasks()

    def add_task(self):
        task = self.input.text()
        if task:
            # Veritabanına ekle
            self.cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
            self.conn.commit()
            self.load_tasks()  # Listeyi güncelle
            self.input.clear()
        else:
            QMessageBox.warning(self, "Uyarı", "Boş bir görev ekleyemezsiniz!")

    def delete_task(self):
        selected_item = self.list_widget.currentRow()
        if selected_item != -1:
            task_text = self.list_widget.item(selected_item).text()
            task_id = self.get_task_id(task_text)
            if task_id:
                # Veritabanından sil
                self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                self.conn.commit()
                self.load_tasks()  # Listeyi güncelle
            else:
                QMessageBox.warning(self, "Hata", "Görev silinemedi!")
        else:
            QMessageBox.warning(self, "Uyarı", "Silmek için bir görev seçin!")

    def get_task_id(self, task_text):
        # Görev adını kullanarak ID'yi bul
        self.cursor.execute("SELECT id FROM tasks WHERE task = ?", (task_text,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def load_tasks(self):
        # Mevcut görevleri listeye yükle
        self.list_widget.clear()
        self.cursor.execute("SELECT id, task, completed FROM tasks")
        tasks = self.cursor.fetchall()
        for task in tasks:
            task_id, task_text, completed = task
            item = QListWidgetItem(task_text)
            self.list_widget.addItem(item)

    def closeEvent(self, event):
        # Uygulama kapatıldığında veritabanı bağlantısını kapat
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())
