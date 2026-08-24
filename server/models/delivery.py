import uuid
from datetime import datetime

from server.extensions import db


class Delivery(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(
        db.String(36), db.ForeignKey("orders.id"), nullable=False, unique=True, index=True
    )
    rider_id = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=True, index=True)
    status = db.Column(db.String(30), nullable=False, default="pending")
    pickup_lat = db.Column(db.Float)
    pickup_lng = db.Column(db.Float)
    dropoff_lat = db.Column(db.Float)
    dropoff_lng = db.Column(db.Float)
    tracking_updates = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    order = db.relationship("Order", back_populates="delivery")
    rider = db.relationship("Profile", foreign_keys=[rider_id])
