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


def get_profile_id(client, email):
    from server.extensions import db
    from server.models import Profile

    with client.application.app_context():
        return db.session.query(Profile).filter_by(user_id=email).first().id


@pytest.fixture
def buyer_token(client):
    return get_auth_token(client, "buyer_o3@test.com", "password123")


@pytest.fixture
def retailer_token(client):
    return get_auth_token(client, "retailer_o3@test.com", "password123", role="retailer")


@pytest.fixture
def shop_id(client, retailer_token):
    resp = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={
            "name": "Order Shop",
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
            "title": "Order Product",
            "price": 1000,
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
            "items": [{"listing_id": listing_id, "qty": 2}],
            "delivery_method": "pickup",
            "payment_method": "stripe",
        },
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def test_create_order_success(client, buyer_token, shop_id, listing_id):
    resp = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": 1}],
            "delivery_method": "pickup",
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "id" in data
    assert data["shop_id"] == shop_id
    assert data["total"] == 1000
    assert data["status"] == "pending"
    assert data["payment_method"] == "cash"
    assert data["delivery_method"] == "pickup"
    assert data["payment_status"] == "pending"


def test_create_order_unauthorized(client, shop_id, listing_id):
    resp = client.post(
        "/api/v1/orders",
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": 1}],
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 401


def test_create_order_invalid_shop(client, buyer_token, listing_id):
    resp = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "shop_id": "invalid-shop-id",
            "items": [{"listing_id": listing_id, "qty": 1}],
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 400


def test_create_order_missing_items(client, buyer_token, shop_id):
    resp = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "shop_id": shop_id,
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 500


def test_get_order_success(client, buyer_token, order_id):
    resp = client.get(
        f"/api/v1/orders/{order_id}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == order_id
    assert "status" in data
    assert "total" in data


def test_get_order_not_found(client, buyer_token):
    resp = client.get(
        "/api/v1/orders/nonexistent-id", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert resp.status_code == 400


def test_get_order_forbidden(client, buyer_token, retailer_token, shop_id, listing_id):
    other_buyer_token = get_auth_token(client, "other_o5@test.com", "password123")
    resp = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {other_buyer_token}"},
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": 1}],
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 201
    other_order_id = resp.get_json()["id"]

    resp = client.get(
        f"/api/v1/orders/{other_order_id}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert resp.status_code == 400


def test_advance_order_status_flow(client, retailer_token, order_id):
    from server.extensions import db
    from server.models import Order

    transitions = [
        ("confirmed", "confirmed"),
        ("paid", "paid"),
        ("preparing", "preparing"),
        ("out_for_delivery", "out_for_delivery"),
        ("delivered", "delivered"),
    ]

    for patch_status, expected_status in transitions:
        resp = client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": patch_status},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == expected_status
        with client.application.app_context():
            order = db.session.query(Order).filter_by(id=order_id).first()
            order.status = expected_status
            db.session.commit()


def test_advance_invalid_transition(client, retailer_token, order_id):
    resp = client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={"status": "delivered"},
    )
    assert resp.status_code == 409


def test_cancel_order_success(client, buyer_token, order_id):
    resp = client.post(
        f"/api/v1/orders/{order_id}/cancel", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "cancelled"


def test_cancel_order_forbidden(client, buyer_token, retailer_token, shop_id, listing_id):
    other_buyer_token = get_auth_token(client, "other_o6@test.com", "password123")
    resp = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {other_buyer_token}"},
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": 1}],
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 201
    other_order_id = resp.get_json()["id"]

    resp = client.post(
        f"/api/v1/orders/{other_order_id}/cancel",
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert resp.status_code == 400


def test_cancel_order_unauthorized(client, order_id):
    resp = client.post(f"/api/v1/orders/{order_id}/cancel")
    assert resp.status_code == 401
