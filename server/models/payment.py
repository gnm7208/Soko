import uuid
from datetime import datetime

from server.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(
        db.String(36), db.ForeignKey("orders.id"), nullable=False, unique=True, index=True
    )
    provider = db.Column(db.String(30), nullable=False)
    provider_ref = db.Column(db.String(255))
    amount = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending")
    raw_payload = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    order = db.relationship("Order", back_populates="payment")
