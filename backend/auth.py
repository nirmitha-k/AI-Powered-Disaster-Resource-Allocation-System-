from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from db_models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    role = data.get("role", "victim")

    if not name or not email or not password:
        return jsonify(error="name, email and password are required"), 400
    if role not in ("victim", "responder"):   # coordinators are created via seed.py
        return jsonify(error="role must be victim or responder"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered"), 409

    user = User(
        name=name, email=email, role=role,
        phone=data.get("phone"), lat=data.get("lat"), lng=data.get("lng"),
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(message="Registered", id=user.id), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not check_password_hash(user.password_hash, data.get("password", "")):
        return jsonify(error="Invalid email or password"), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(token=token, user={"id": user.id, "name": user.name, "role": user.role})


@auth_bp.route("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    return jsonify(id=user.id, name=user.name, email=user.email, role=user.role)