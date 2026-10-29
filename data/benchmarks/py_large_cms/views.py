"""CMS views."""
from models import Post, Author
from database import DatabaseConnection

class CMSController:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def get_post_detail(self, post_id: int) -> dict:
        results = self.db.query(f"SELECT * FROM posts WHERE id={post_id}")
        return results[0] if results else {}

    def publish_post(self, title: str, content: str, author_id: int) -> int:
        self.db.query(f"INSERT INTO posts (title, content, author_id) VALUES ('{title}', '{content}', {author_id})")
        return 1
