import json

from server.services.order_state_machine import OrderStateMachine
from server.utils.errors import APIError


class PaymentWebhookService:
    @staticmethod
    def _parse_payload(payload):
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        if isinstance(payload, str):
            payload = json.loads(payload)
        return payload

    @staticmethod
    def handle_stripe(payload, signature, secret):
        event = PaymentWebhookService._parse_payload(payload)
        if event.get("type") == "payment_intent.succeeded":
            provider_ref = event.get("data", {}).get("object", {}).get("id")
            amount = event.get("data", {}).get("object", {}).get("amount")
            PaymentWebhookService._mark_paid("stripe", provider_ref, amount)
        return True

    @staticmethod
    def handle_flutterwave(payload, signature, secret):
        event = PaymentWebhookService._parse_payload(payload)
        if event.get("status") == "successful":
            provider_ref = event.get("tx_ref")
            amount = event.get("amount")
            PaymentWebhookService._mark_paid("flutterwave", provider_ref, amount)
        return True

    @staticmethod
    def handle_paystack(payload, signature, secret):
        event = PaymentWebhookService._parse_payload(payload)
        if event.get("event") == "charge.success":
            provider_ref = event.get("data", {}).get("reference")
            amount = event.get("data", {}).get("amount")
            PaymentWebhookService._mark_paid("paystack", provider_ref, amount)
        return True

    @staticmethod
    def _mark_paid(provider, provider_ref, amount):
        from server.extensions import db
        from server.models import Order, Payment

        payment = (
            db.session.query(Payment)
            .filter_by(provider=provider, provider_ref=provider_ref)
            .first()
        )
        if not payment:
            raise APIError("Payment not found", status_code=404)
        if payment.status == "success":
            return
        payment.status = "success"
        order = db.session.query(Order).filter_by(id=payment.order_id).first()
        if order:
            OrderStateMachine.advance(order, "paid")
            order.payment_status = "paid"
        db.session.commit()
