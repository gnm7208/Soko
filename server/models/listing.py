import uuid
from datetime import datetime

from server.extensions import db


class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = db.Column(db.String(36), db.ForeignKey("shops.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.BigInteger, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    category_id = db.Column(
        db.String(36), db.ForeignKey("categories.id"), nullable=True, index=True
    )
    condition = db.Column(db.String(20), nullable=False, default="new")
    stock = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    location = db.Column(db.String(255))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    shop = db.relationship("Shop", back_populates="listings")
    category = db.relationship("Category", back_populates="listings")
    images = db.relationship(
        "ListingImage",
        back_populates="listing",
        cascade="all, delete-orphan",
        order_by="ListingImage.position",
    )
    favorites = db.relationship("Favorite", back_populates="listing", cascade="all, delete-orphan")
    order_items = db.relationship("OrderItem", back_populates="listing")
    promotions = db.relationship(
        "Promotion", back_populates="listing", cascade="all, delete-orphan"
    )
