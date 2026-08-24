import uuid
from datetime import datetime

from server.extensions import db


class Promotion(db.Model):
    __tablename__ = "promotions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = db.Column(db.String(36), db.ForeignKey("shops.id"), nullable=True, index=True)
    listing_id = db.Column(db.String(36), db.ForeignKey("listings.id"), nullable=True, index=True)
    type = db.Column(db.String(20), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    discount_pct = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    shop = db.relationship("Shop", back_populates="promotions")
    listing = db.relationship("Listing", back_populates="promotions")
