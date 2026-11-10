import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from extensions import db

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
db.init_app(app)
JWTManager(app)

import db_models  # noqa: E402
from auth import auth_bp  # noqa: E402
from requests_api import req_bp  # noqa: E402

app.register_blueprint(auth_bp)
app.register_blueprint(req_bp)

with app.app_context():
    db.create_all()

@app.route("/api/health")
def health():
    db.session.execute(db.text("SELECT 1"))
    return jsonify(status="ok", db="connected")

if __name__ == "__main__":
    app.run(debug=True)