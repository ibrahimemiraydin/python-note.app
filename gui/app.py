import customtkinter as ctk
from gui.components.note_list import NoteListFrame
from gui.components.note_form import NoteFormFrame
from gui.components.note_detail import NoteDetailFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Not Uygulaması")
        self.geometry("800x600")
        self.configure_layout()

    def configure_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Not listesi paneli
        self.note_list_frame = NoteListFrame(self, self.open_note_form, self.open_note_detail)
        self.note_list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def open_note_form(self, note_id=None):
        # Not ekleme/güncelleme formunu aç
        form = NoteFormFrame(self, note_id, self.note_list_frame.refresh_notes)

    def open_note_detail(self, note_id):
        # Not detayını aç
        detail = NoteDetailFrame(self, note_id, self.note_list_frame.refresh_notes)

if __name__ == "__main__":
    app = App()
    app.mainloop()