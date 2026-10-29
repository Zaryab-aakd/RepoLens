"""Main CMS application."""
from database import DatabaseConnection
from views import CMSController

def create_cms_app(db_uri: str) -> CMSController:
    db = DatabaseConnection(db_uri)
    db.connect()
    return CMSController(db)
