import uuid
from datetime import datetime

from server.extensions import db


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=False, index=True)
    listing_id = db.Column(db.String(36), db.ForeignKey("listings.id"), nullable=False, index=True)
    title_snapshot = db.Column(db.String(255), nullable=False)
    price_snapshot = db.Column(db.BigInteger, nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    order = db.relationship("Order", back_populates="items")
    listing = db.relationship("Listing", back_populates="order_items")
