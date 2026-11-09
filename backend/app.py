import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
db.init_app(app)

import db_models  # noqa: E402  (must come after db.init_app)

with app.app_context():
    db.create_all()

@app.route("/api/health")
def health():
    db.session.execute(db.text("SELECT 1"))
    return jsonify(status="ok", db="connected")

if __name__ == "__main__":
    app.run(debug=True)