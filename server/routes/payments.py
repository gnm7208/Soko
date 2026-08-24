from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db, limiter
from server.models import Order, Payment
from server.schemas.payment import PaymentIntentSchema, PaymentSchema
from server.services.payment_webhooks import PaymentWebhookService
from server.utils.auth import buyer_required, get_current_profile
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("payments", __name__)


@bp.route("/payments/intent", methods=["POST"])
@jwt_required()
@buyer_required
def create_payment_intent():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        schema = PaymentIntentSchema()
        validated = schema.load(data)
        order = db.session.query(Order).filter_by(id=validated["order_id"]).first()
        if not order:
            raise NotFound("Order not found")
        if order.buyer_id != profile.id:
            raise Forbidden("Not authorized")
        payment = Payment(
            order_id=order.id,
            provider=validated["provider"],
            amount=order.total,
            status="pending",
        )
        db.session.add(payment)
        db.session.commit()
        schema_out = PaymentSchema()
        return jsonify(schema_out.dump(payment)), 201
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/webhooks/stripe", methods=["POST"])
@limiter.limit("100 per minute")
def stripe_webhook():
    try:
        payload = request.get_data()
        sig_header = request.headers.get("Stripe-Signature")
        result = PaymentWebhookService.handle_stripe(payload, sig_header)
        return jsonify(result), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/webhooks/flutterwave", methods=["POST"])
@limiter.limit("100 per minute")
def flutterwave_webhook():
    try:
        payload = request.get_data()
        sig_header = request.headers.get("verif-hash")
        result = PaymentWebhookService.handle_flutterwave(payload, sig_header)
        return jsonify(result), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/webhooks/paystack", methods=["POST"])
@limiter.limit("100 per minute")
def paystack_webhook():
    try:
        payload = request.get_data()
        sig_header = request.headers.get("X-Hub-Signature-256") or request.headers.get(
            "x-hub-signature-256"
        )
        result = PaymentWebhookService.handle_paystack(payload, sig_header)
        return jsonify(result), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
