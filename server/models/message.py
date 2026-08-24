import uuid
from datetime import datetime

from server.extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(
        db.String(36), db.ForeignKey("conversations.id"), nullable=False, index=True
    )
    sender_id = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    conversation = db.relationship("Conversation", back_populates="messages")
    sender = db.relationship("Profile", back_populates="sent_messages", foreign_keys=[sender_id])
