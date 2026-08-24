import uuid
from datetime import datetime

from server.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("Profile", back_populates="notifications", foreign_keys=[user_id])
