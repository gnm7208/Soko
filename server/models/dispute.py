import uuid
from datetime import datetime

from server.extensions import db


class Dispute(db.Model):
    __tablename__ = "disputes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=False, index=True)
    raised_by = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open", index=True)
    resolution_note = db.Column(db.Text)
    resolved_by = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    order = db.relationship("Order", back_populates="disputes")
    raiser = db.relationship("Profile", foreign_keys=[raised_by])
    resolver = db.relationship("Profile", foreign_keys=[resolved_by])
