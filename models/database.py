import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("todo_list.db")
        self.cursor = self.conn.cursor()

    def insert_task(self, task_text):
        """Yeni bir görev ekler."""
        self.cursor.execute("INSERT INTO tasks (task, completed) VALUES (?, 0)", (task_text,))
        self.conn.commit()

    def get_all_tasks(self):
        """Tüm görevleri getirir."""
        self.cursor.execute("SELECT id, task, completed FROM tasks")
        return self.cursor.fetchall()

    def update_task_completed(self, task_id):
        """Bir görevi tamamlandı olarak işaretler."""
        self.cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()

    def delete_task(self, task_id):
        """Bir görevi siler."""
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def close(self):
        """Veritabanı bağlantısını kapatır."""
        self.conn.close()
