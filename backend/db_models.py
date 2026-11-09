from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("victim", "responder", "coordinator"), nullable=False, default="victim")
    phone = db.Column(db.String(20))
    lat = db.Column(db.Float)   # responder base location
    lng = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    severity = db.Column(db.String(50))
    source_link = db.Column(db.String(500), unique=True)  # used for duplicate detection
    published_at = db.Column(db.DateTime)
    status = db.Column(db.Enum("pending", "verified", "discarded"), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Incident(db.Model):
    __tablename__ = "incidents"
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    disaster_type = db.Column(db.String(50))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    people_affected = db.Column(db.Integer, default=0)
    injuries = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum("open", "closed"), default="open")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmergencyRequest(db.Model):
    __tablename__ = "emergency_requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=True)
    disaster_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    people_affected = db.Column(db.Integer, default=1)
    injuries = db.Column(db.Integer, default=0)
    has_children_elderly = db.Column(db.Boolean, default=False)
    resource_needed = db.Column(db.String(100))
    description = db.Column(db.Text)
    urgency = db.Column(db.Enum("Critical", "High", "Medium", "Low"))
    urgency_source = db.Column(db.Enum("model", "coordinator"), default="model")
    status = db.Column(
        db.Enum("pending", "verified", "allocated", "in_progress", "completed", "rejected"),
        default="pending",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ResourceCentre(db.Model):
    __tablename__ = "resource_centres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    centre_id = db.Column(db.Integer, db.ForeignKey("resource_centres.id"), nullable=False)
    category = db.Column(
        db.Enum("food", "water", "medical_kit", "shelter", "response_unit"), nullable=False
    )
    quantity = db.Column(db.Integer, default=0)


class Allocation(db.Model):
    __tablename__ = "allocations"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("emergency_requests.id"), nullable=False)
    centre_id = db.Column(db.Integer, db.ForeignKey("resource_centres.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unmet = db.Column(db.Integer, default=0)
    status = db.Column(
        db.Enum("proposed", "approved", "accepted", "in_progress", "completed"),
        default="proposed",
    )
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    responder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    allocation_id = db.Column(db.Integer, db.ForeignKey("allocations.id"))
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StatusLog(db.Model):
    __tablename__ = "status_log"
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)  # e.g. "request", "allocation"
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)      # e.g. "urgency overridden"
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)