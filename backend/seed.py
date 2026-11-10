from werkzeug.security import generate_password_hash
from app import app
from extensions import db
from db_models import User

with app.app_context():
    if not User.query.filter_by(email="coordinator@test.com").first():
        db.session.add(User(
            name="Coordinator", email="coordinator@test.com",
            password_hash=generate_password_hash("admin123"), role="coordinator",
        ))
        db.session.commit()
        print("Coordinator created")
    else:
        print("Already exists")