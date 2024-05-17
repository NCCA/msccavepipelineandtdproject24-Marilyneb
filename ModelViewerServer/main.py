from app import app, db
from flask_sqlalchemy import SQLAlchemy
import routes  # Add this line

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 30001)