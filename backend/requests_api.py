from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from db_models import EmergencyRequest, StatusLog
from utils import role_required

req_bp = Blueprint("requests", __name__, url_prefix="/api/requests")


def to_dict(r):
    return {
        "id": r.id, "disaster_type": r.disaster_type, "address": r.address,
        "lat": r.lat, "lng": r.lng, "people_affected": r.people_affected,
        "injuries": r.injuries, "has_children_elderly": r.has_children_elderly,
        "resource_needed": r.resource_needed, "description": r.description,
        "urgency": r.urgency, "urgency_source": r.urgency_source,
        "status": r.status, "created_at": r.created_at.isoformat(),
    }


@req_bp.route("", methods=["POST"])
@role_required("victim")
def create_request():
    data = request.get_json() or {}
    if not data.get("disaster_type"):
        return jsonify(error="disaster_type is required"), 400

    has_gps = data.get("lat") is not None and data.get("lng") is not None
    if not has_gps and not data.get("address"):
        return jsonify(error="Provide GPS (lat/lng) or an address"), 400

    r = EmergencyRequest(
        user_id=int(get_jwt_identity()),
        disaster_type=data["disaster_type"],
        address=data.get("address"),
        lat=data.get("lat"), lng=data.get("lng"),
        people_affected=data.get("people_affected", 1),
        injuries=data.get("injuries", 0),
        has_children_elderly=data.get("has_children_elderly", False),
        resource_needed=data.get("resource_needed"),
        description=data.get("description"),
        # urgency stays empty until the classifier is added in Step 4
    )
    db.session.add(r)
    db.session.flush()
    db.session.add(StatusLog(entity_type="request", entity_id=r.id,
                             action="submitted", actor_id=r.user_id))
    db.session.commit()
    return jsonify(to_dict(r)), 201


@req_bp.route("/mine")
@role_required("victim")
def my_requests():
    rows = (EmergencyRequest.query.filter_by(user_id=int(get_jwt_identity()))
            .order_by(EmergencyRequest.created_at.desc()).all())
    return jsonify([to_dict(r) for r in rows])


@req_bp.route("/<int:req_id>")
@jwt_required()
def get_request(req_id):
    r = db.session.get(EmergencyRequest, req_id)
    if not r:
        return jsonify(error="Not found"), 404
    if get_jwt().get("role") != "coordinator" and r.user_id != int(get_jwt_identity()):
        return jsonify(error="Forbidden"), 403
    return jsonify(to_dict(r))


@req_bp.route("")
@role_required("coordinator")
def list_requests():
    status = request.args.get("status")
    q = EmergencyRequest.query
    if status:
        q = q.filter_by(status=status)
    return jsonify([to_dict(r) for r in q.order_by(EmergencyRequest.created_at.desc()).all()])