import customtkinter as ctk
from services import add_note, update_note, get_note_by_id

class NoteFormFrame(ctk.CTkToplevel):
    def __init__(self, master, note_id=None, refresh_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.note_id = note_id
        self.refresh_callback = refresh_callback
        self.title("Not Ekle/Güncelle" if not note_id else "Not Güncelle")
        
        self.geometry("600x600")
        self.configure_layout()
        self.after(100,self.lift) # Pencereyi öne al
        self.focus_force()  # Pencereye odaklan

        if note_id:
            self.load_note()

    def configure_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Başlık
        self.title_label = ctk.CTkLabel(self, text="Başlık", font=("Arial", 14))
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")  # pady=(üst, alt)

        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # İçerik
        self.content_label = ctk.CTkLabel(self, text="İçerik", font=("Arial", 14))
        self.content_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")

        self.content_text = ctk.CTkTextbox(self)
        self.content_text.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Kaydet butonu
        self.save_button = ctk.CTkButton(self, text="Kaydet", command=self.save_note)
        self.save_button.grid(row=4, column=0, padx=10, pady=10, sticky="e")

    def load_note(self):
        note = get_note_by_id(self.note_id)
        if note:
            self.title_entry.insert(0, note.title)
            self.content_text.insert("1.0", note.content)

    def save_note(self):
        title = self.title_entry.get()
        content = self.content_text.get("1.0", "end-1c")

        if self.note_id:
            update_note(self.note_id, title, content)
        else:
            add_note(title, content)

        if self.refresh_callback:
            self.refresh_callback()

        self.destroy()