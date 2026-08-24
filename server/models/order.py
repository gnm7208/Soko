import uuid
from datetime import datetime

from server.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=False, index=True)
    shop_id = db.Column(db.String(36), db.ForeignKey("shops.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="pending", index=True)
    total = db.Column(db.BigInteger, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    payment_method = db.Column(db.String(30), nullable=False)
    payment_status = db.Column(db.String(30), nullable=False, default="pending")
    delivery_method = db.Column(db.String(20), nullable=False, default="pickup")
    delivery_address = db.Column(db.String(512))
    delivery_lat = db.Column(db.Float)
    delivery_lng = db.Column(db.Float)
    rider_id = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    buyer = db.relationship("Profile", back_populates="orders", foreign_keys=[buyer_id])
    shop = db.relationship("Shop", back_populates="orders")
    rider = db.relationship("Profile", foreign_keys=[rider_id])
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = db.relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    delivery = db.relationship(
        "Delivery", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    review = db.relationship(
        "Review", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    disputes = db.relationship("Dispute", back_populates="order", cascade="all, delete-orphan")
