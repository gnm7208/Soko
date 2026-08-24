import uuid
from datetime import datetime

from server.extensions import db


class Shop(db.Model):
    __tablename__ = "shops"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(
        db.String(36), db.ForeignKey("profiles.id"), unique=True, nullable=False, index=True
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(1024))
    cover_url = db.Column(db.String(1024))
    category = db.Column(db.String(100))
    address = db.Column(db.String(512))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    rating_avg = db.Column(db.Float, default=0.0, nullable=False)
    rating_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner = db.relationship("Profile", back_populates="shop")
    listings = db.relationship("Listing", back_populates="shop", cascade="all, delete-orphan")
    conversations = db.relationship("Conversation", back_populates="shop")
    orders = db.relationship("Order", back_populates="shop")
    reviews = db.relationship("Review", back_populates="shop")
    promotions = db.relationship("Promotion", back_populates="shop", cascade="all, delete-orphan")
