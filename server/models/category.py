import uuid
from datetime import datetime

from server.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    parent_id = db.Column(db.String(36), db.ForeignKey("categories.id"), nullable=True)
    icon = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    parent = db.relationship(
        "Category", remote_side=[id], backref=db.backref("children", lazy="dynamic")
    )
    listings = db.relationship("Listing", back_populates="category")
