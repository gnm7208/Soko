import uuid
from datetime import datetime

from server.extensions import db


class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_id = db.Column(db.String(36), db.ForeignKey("wallets.id"), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.BigInteger, nullable=False)
    ref = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    wallet = db.relationship("Wallet", back_populates="transactions")
