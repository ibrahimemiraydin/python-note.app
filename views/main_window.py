from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QLineEdit, QMessageBox, QListWidgetItem
from PySide6.QtCore import Qt
from models.database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Uygulaması")
        self.setGeometry(100, 100, 400, 600)

        # Veritabanı bağlantısı
        self.db = Database()

        # Arayüz bileşenlerini oluştur
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)

        # Görev ekleme alanı
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Bir görev ekleyin...")
        self.input.setStyleSheet("""
            padding: 10px; 
            border-radius: 5px; 
            border: 1px solid #ccc;
            font-size: 16px;
            color: black;  /* Yazı rengini siyah yap */
            background-color: #fff;  /* Arka plan rengini beyaz yap */
        """)
        self.layout.addWidget(self.input)

        # Görev ekleme butonu
        self.add_button = QPushButton("Ekle", self)
        self.add_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
        """)
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        # Görev listesi
        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet("""
            border: none;
            border-radius: 10px;
            background-color: #f4f4f4;
            padding: 10px;
            margin-top: 20px;
            font-size: 16px;
        """)
        self.layout.addWidget(self.list_widget)

        # Görev silme butonu
        self.delete_button = QPushButton("Seçili Görevi Sil", self)
        self.delete_button.setStyleSheet("""
            background-color: #f44336;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
        """)
        self.delete_button.clicked.connect(self.delete_task)
        self.layout.addWidget(self.delete_button)

        # Merkezi widget'ı ayarla
        self.setCentralWidget(self.central_widget)

        # Görevleri yükle
        self.load_tasks()

    def load_tasks(self):
        """Veritabanından görevleri yükler ve listeye ekler."""
        tasks = self.db.get_all_tasks()
        self.list_widget.clear()
        for task in tasks:
            task_id, task_text, completed = task
            item = QListWidgetItem(task_text)
            
            # Yazı boyutunu arttır ve rengini siyah yap
            item.setFont(self.font())  # Varsayılan fontu kullan
            item.setForeground(Qt.black)  # Siyah renk

            # Görev tamamlandıysa yeşil renkte göster
            if completed:
                item.setForeground(Qt.green)  # Yeşil renk

            self.list_widget.addItem(item)

    def add_task(self):
        """Yeni bir görev ekler."""
        task_text = self.input.text()
        if task_text:
            # Veritabanına ekle
            self.db.insert_task(task_text)
            self.load_tasks()  # Listeyi güncelle
            self.input.clear()

        else:
            QMessageBox.warning(self, "Uyarı", "Boş bir görev ekleyemezsiniz!")

    def delete_task(self):
        """Seçilen görevi siler."""
        selected_item = self.list_widget.currentRow()
        if selected_item != -1:
            task_text = self.list_widget.item(selected_item).text()
            task_id = self.get_task_id(task_text)
            if task_id:
                # Yalnızca tamamlanmamış görevler silinecek
                if "(Tamamlandı)" not in task_text:
                    self.db.delete_task(task_id)
                    self.load_tasks()  # Listeyi güncelle
                else:
                    QMessageBox.warning(self, "Hata", "Tamamlanan görevler silinemez!")
            else:
                QMessageBox.warning(self, "Hata", "Görev silinemedi!")
        else:
            QMessageBox.warning(self, "Uyarı", "Silmek için bir görev seçin!")

    def get_task_id(self, task_text):
        """Görev metnini kullanarak görev ID'sini alır."""
        self.db.cursor.execute("SELECT id FROM tasks WHERE task = ?", (task_text,))
        result = self.db.cursor.fetchone()
        return result[0] if result else None

    def closeEvent(self, event):
        """Uygulama kapatıldığında veritabanı bağlantısını kapatır."""
        self.db.close()
        event.accept()
