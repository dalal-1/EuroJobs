from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_app(app):
    """Initialize the app with the db instance."""
    db.init_app(app)
