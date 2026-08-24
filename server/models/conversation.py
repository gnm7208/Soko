import uuid
from datetime import datetime

from server.extensions import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=False, index=True)
    shop_id = db.Column(db.String(36), db.ForeignKey("shops.id"), nullable=False, index=True)
    listing_id = db.Column(db.String(36), db.ForeignKey("listings.id"), nullable=True, index=True)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    buyer = db.relationship(
        "Profile", back_populates="conversations_as_buyer", foreign_keys=[buyer_id]
    )
    shop = db.relationship("Shop", back_populates="conversations")
    listing = db.relationship("Listing")
    messages = db.relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
