import uuid
from datetime import datetime

from server.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(
        db.String(36), db.ForeignKey("orders.id"), nullable=False, unique=True, index=True
    )
    shop_id = db.Column(db.String(36), db.ForeignKey("shops.id"), nullable=False, index=True)
    buyer_id = db.Column(db.String(36), db.ForeignKey("profiles.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    order = db.relationship("Order", back_populates="review")
    shop = db.relationship("Shop", back_populates="reviews")
    buyer = db.relationship("Profile", back_populates="reviews", foreign_keys=[buyer_id])
