import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
db = SQLAlchemy(app)

@app.route("/api/health")
def health():
    db.session.execute(db.text("SELECT 1"))
    return jsonify(status="ok", db="connected")

if __name__ == "__main__":
    app.run(debug=True)