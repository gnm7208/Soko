import uuid
from datetime import datetime

from server.extensions import db


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(
        db.String(36), db.ForeignKey("profiles.id"), unique=True, nullable=False, index=True
    )
    balance = db.Column(db.BigInteger, nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner = db.relationship("Profile", back_populates="wallet")
    transactions = db.relationship(
        "WalletTransaction", back_populates="wallet", cascade="all, delete-orphan"
    )
