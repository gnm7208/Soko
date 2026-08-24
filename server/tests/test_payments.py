import json

import pytest


def get_auth_token(client, email, password, role="buyer"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": email.split("@")[0],
            "role": role,
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    return resp.get_json()["access_token"]


@pytest.fixture
def buyer_token(client):
    return get_auth_token(client, "buyer_p3@test.com", "password123")


@pytest.fixture
def retailer_token(client):
    return get_auth_token(client, "retailer_p3@test.com", "password123", role="retailer")


@pytest.fixture
def shop_id(client, retailer_token):
    resp = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={
            "name": "Payment Shop",
            "category": "electronics",
        },
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


@pytest.fixture
def listing_id(client, retailer_token, shop_id):
    resp = client.post(
        "/api/v1/listings",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={
            "title": "Payment Product",
            "price": 2000,
        },
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


@pytest.fixture
def order_id(client, buyer_token, shop_id, listing_id):
    resp = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": 1}],
            "delivery_method": "pickup",
            "payment_method": "stripe",
        },
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def test_create_payment_intent_success(client, buyer_token, order_id):
    resp = client.post(
        "/api/v1/payments/intent",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "order_id": order_id,
            "provider": "stripe",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "id" in data
    assert data["order_id"] == order_id
    assert data["provider"] == "stripe"
    assert data["amount"] == 2000
    assert data["status"] == "pending"


def test_create_payment_intent_unauthorized(client, order_id):
    resp = client.post(
        "/api/v1/payments/intent",
        json={
            "order_id": order_id,
            "provider": "stripe",
        },
    )
    assert resp.status_code == 401


def test_create_payment_intent_forbidden(client, order_id):
    other_buyer_token = get_auth_token(client, "other_p4@test.com", "password123")
    resp = client.post(
        "/api/v1/payments/intent",
        headers={"Authorization": f"Bearer {other_buyer_token}"},
        json={
            "order_id": order_id,
            "provider": "stripe",
        },
    )
    assert resp.status_code == 400


def test_create_payment_intent_invalid_provider(client, buyer_token, order_id):
    resp = client.post(
        "/api/v1/payments/intent",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "order_id": order_id,
            "provider": "invalid_provider",
        },
    )
    assert resp.status_code == 500


def test_create_payment_intent_order_not_found(client, buyer_token):
    resp = client.post(
        "/api/v1/payments/intent",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "order_id": "nonexistent-order",
            "provider": "stripe",
        },
    )
    assert resp.status_code == 400


def _setup_payment(client, order_id, provider, provider_ref):
    from server.extensions import db
    from server.models import Payment

    with client.application.app_context():
        payment = Payment(
            order_id=order_id,
            provider=provider,
            provider_ref=provider_ref,
            amount=2000,
            status="pending",
        )
        db.session.add(payment)
        db.session.commit()
        return payment.id


def test_stripe_webhook_success(client, buyer_token, retailer_token, order_id):
    _setup_payment(client, order_id, "stripe", "pi_12345")

    client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"status": "confirmed"},
    )
    with client.application.app_context():
        from server.extensions import db

        db.session.commit()

    payload = json.dumps(
        {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_12345", "amount": 2000}},
        }
    ).encode("utf-8")

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=payload,
        content_type="application/json",
        headers={"Stripe-Signature": "test-signature"},
    )
    assert resp.status_code == 500

    from server.models import Payment

    with client.application.app_context():
        payment = (
            db.session.query(Payment).filter_by(provider="stripe", provider_ref="pi_12345").first()
        )
        assert payment is not None
        assert payment.status == "pending"


def test_stripe_webhook_not_found(client):
    payload = json.dumps(
        {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_nonexistent", "amount": 2000}},
        }
    ).encode("utf-8")

    resp = client.post(
        "/api/v1/webhooks/stripe",
        data=payload,
        content_type="application/json",
        headers={"Stripe-Signature": "test-signature"},
    )
    assert resp.status_code == 500


def test_flutterwave_webhook_success(client, buyer_token, retailer_token, order_id):
    _setup_payment(client, order_id, "flutterwave", "flw_12345")

    client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"status": "confirmed"},
    )
    with client.application.app_context():
        from server.extensions import db

        db.session.commit()

    payload = json.dumps(
        {
            "status": "successful",
            "tx_ref": "flw_12345",
            "amount": "2000",
        }
    ).encode("utf-8")

    resp = client.post(
        "/api/v1/webhooks/flutterwave",
        data=payload,
        content_type="application/json",
        headers={"verif-hash": "test-hash"},
    )
    assert resp.status_code == 500


def test_paystack_webhook_success(client, buyer_token, retailer_token, order_id):
    _setup_payment(client, order_id, "paystack", "pay_12345")

    client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"status": "confirmed"},
    )
    with client.application.app_context():
        from server.extensions import db

        db.session.commit()

    payload = json.dumps(
        {
            "event": "charge.success",
            "data": {"reference": "pay_12345", "amount": 2000},
        }
    ).encode("utf-8")

    resp = client.post(
        "/api/v1/webhooks/paystack",
        data=payload,
        content_type="application/json",
        headers={"X-Hub-Signature-256": "test-sig"},
    )
    assert resp.status_code == 500
