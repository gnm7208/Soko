import uuid
from datetime import datetime

from server.extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default="buyer")
    full_name = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    avatar_url = db.Column(db.String(1024))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    shop = db.relationship("Shop", back_populates="owner", uselist=False)
    orders = db.relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")
    reviews = db.relationship("Review", back_populates="buyer", foreign_keys="Review.buyer_id")
    wallet = db.relationship("Wallet", back_populates="owner", uselist=False)
    sent_messages = db.relationship(
        "Message", back_populates="sender", foreign_keys="Message.sender_id"
    )
    conversations_as_buyer = db.relationship(
        "Conversation", back_populates="buyer", foreign_keys="Conversation.buyer_id"
    )
    notifications = db.relationship(
        "Notification", back_populates="user", foreign_keys="Notification.user_id"
    )
