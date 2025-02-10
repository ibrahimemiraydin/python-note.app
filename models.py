class Note:
    def __init__(self, id, title, content, created_at):
        self.id = id
        self.title = title
        self.content = content
        self.created_at = created_at  # created_at eklendi

    def __repr__(self):
        return f"Note(id={self.id}, title={self.title}, content={self.content}, created_at={self.created_at})"