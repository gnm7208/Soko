from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Wallet, WalletTransaction
from server.schemas.wallet import (
    PayoutCreateSchema,
    PayoutRequestSchema,
    WalletSchema,
    WalletTransactionSchema,
)
from server.utils.auth import get_current_profile, retailer_required
from server.utils.errors import APIError, NotFound

bp = Blueprint("wallets", __name__)


@bp.route("/wallets/me", methods=["GET"])
@jwt_required()
def get_my_wallet():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        wallet = db.session.query(Wallet).filter_by(owner_id=profile.id).first()
        if not wallet:
            raise NotFound("Wallet not found")
        wallet.user_id = wallet.owner_id
        return jsonify(WalletSchema().dump(wallet)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/wallets/me/transactions", methods=["GET"])
@jwt_required()
def list_transactions():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = (
            db.session.query(WalletTransaction)
            .join(Wallet, WalletTransaction.wallet_id == Wallet.id)
            .filter(Wallet.owner_id == profile.id)
        )
        total = query.count()
        items = (
            query.order_by(WalletTransaction.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        schema = WalletTransactionSchema(many=True)
        return (
            jsonify(
                {
                    "items": schema.dump(items),
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page,
                }
            ),
            200,
        )
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/wallets/payout-request", methods=["POST"])
@jwt_required()
@retailer_required
def request_payout():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        schema = PayoutCreateSchema()
        validated = schema.load(data)
        wallet = db.session.query(Wallet).filter_by(owner_id=profile.id).first()
        if not wallet:
            raise NotFound("Wallet not found")
        if wallet.balance < validated["amount"]:
            raise APIError("Insufficient wallet balance", status_code=400)
        txn = WalletTransaction(
            wallet_id=wallet.id,
            type="payout",
            amount=validated["amount"],
            ref="payout-request",
            status="pending",
        )
        db.session.add(txn)
        db.session.commit()
        txn.note = validated.get("note")
        return jsonify(PayoutRequestSchema().dump(txn)), 201
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
