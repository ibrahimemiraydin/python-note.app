import customtkinter as ctk
from services import list_notes, delete_note

class NoteListFrame(ctk.CTkFrame):
    def __init__(self, master, open_note_form, open_note_detail, **kwargs):
        super().__init__(master, **kwargs)
        self.open_note_form = open_note_form
        self.open_note_detail = open_note_detail
        self.configure_layout()
        self.refresh_notes()

    def configure_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Üst panel (Bulunan Notlar yazısı, arama çubuğu ve Not Ekle butonu)
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Bulunan Notlar yazısı
        self.title_label = ctk.CTkLabel(self.top_frame, text="Notlar", font=("Arial", 16, "bold"))
        self.title_label.pack(side="left", padx=10, pady=5)

        # Arama çubuğu
        self.search_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Not ara...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", self.perform_search)  # Her tuş bırakıldığında arama yap

        # Not Ekle butonu
        self.add_button = ctk.CTkButton(self.top_frame, text="Not Ekle", command=self.open_note_form)
        self.add_button.pack(side="right", padx=10, pady=5)

        # Not listesi
        self.note_listbox = ctk.CTkScrollableFrame(self)
        self.note_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def perform_search(self, event=None):
        search_term = self.search_entry.get()
        self.refresh_notes(search_term)

    def refresh_notes(self, search_term=None):
        # Not listesini temizle
        for widget in self.note_listbox.winfo_children():
            widget.destroy()

        # Notları veritabanından al ve filtrele
        notes = list_notes()
        if search_term:
            notes = [note for note in notes if search_term.lower() in note.title.lower() or search_term.lower() in note.content.lower()]

        if notes:
            for note in notes:
                note_frame = ctk.CTkFrame(self.note_listbox)
                note_frame.pack(fill="x", pady=5, padx=5)

                # Başlık (daha büyük ve belirgin)
                title_label = ctk.CTkLabel(note_frame, text=note.title, font=("Arial", 14, "bold"))
                title_label.pack(side="top", padx=10, pady=(5, 0), anchor="w")

                # İçerik (ilk 100 karakter)
                content_preview = note.content[:100] + "..." if len(note.content) > 100 else note.content
                content_label = ctk.CTkLabel(note_frame, text=content_preview, font=("Arial", 12))
                content_label.pack(side="top", padx=10, pady=(0, 5), anchor="w")

                # Alt panel (Tarih ve butonlar)
                bottom_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
                bottom_frame.pack(side="bottom", fill="x", padx=10, pady=5)

                # Tarih
                date_label = ctk.CTkLabel(bottom_frame, text=f"Oluşturulma Tarihi: {note.created_at}", font=("Arial", 10))
                date_label.pack(side="left", padx=0, pady=5)

                # Butonlar (Aç ve Sil)
                button_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                button_frame.pack(side="right", padx=10, pady=5)

                detail_button = ctk.CTkButton(button_frame, text="Aç", command=lambda n=note: self.open_note_detail(n.id))
                detail_button.pack(side="right", padx=5)

                delete_button = ctk.CTkButton(button_frame, text="Sil", command=lambda n=note: self.delete_note(n.id))
                delete_button.pack(side="right", padx=5)
        else:
            no_notes_label = ctk.CTkLabel(self.note_listbox, text="Henüz hiç not eklenmemiş." if not search_term else "Aranan kriterlere uygun not bulunamadı.")
            no_notes_label.pack(padx=10, pady=10)

    def delete_note(self, note_id):
        delete_note(note_id)
        self.refresh_notes()