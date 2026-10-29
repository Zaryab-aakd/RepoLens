"""Content models."""
from database import DatabaseConnection

class Post:
    def __init__(self, post_id: int, title: str, content: str):
        self.post_id = post_id
        self.title = title
        self.content = content

class Author:
    def __init__(self, author_id: int, name: str, email: str):
        self.author_id = author_id
        self.name = name
        self.email = email
