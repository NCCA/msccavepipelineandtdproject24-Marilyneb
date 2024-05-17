from app import app, db
from models import User, Asset, Tag

with app.app_context():
    db.create_all()