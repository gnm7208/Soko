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


def get_rider_token(client, email, password):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": email.split("@")[0],
        },
    )
    with client.application.app_context():
        from server.extensions import db
        from server.models import Profile

        profile = db.session.query(Profile).filter_by(user_id=email).first()
        profile.role = "rider"
        db.session.commit()
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
    return get_auth_token(client, "buyer_d3@test.com", "password123")


@pytest.fixture
def retailer_token(client):
    return get_auth_token(client, "retailer_d3@test.com", "password123", role="retailer")


@pytest.fixture
def rider_token(client):
    return get_rider_token(client, "rider_d3@test.com", "password123")


@pytest.fixture
def rider_profile_id(client, rider_token):
    return get_profile_id(client, "rider_d3@test.com")


@pytest.fixture
def shop_id(client, retailer_token):
    resp = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={
            "name": "Delivery Shop",
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
            "title": "Delivery Product",
            "price": 1500,
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
            "delivery_method": "delivery",
            "delivery_address": "456 Oak Ave",
            "payment_method": "stripe",
        },
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def _create_delivery(client, order_id, status="pending"):
    from server.extensions import db
    from server.models import Delivery

    with client.application.app_context():
        delivery = Delivery(order_id=order_id, status=status)
        db.session.add(delivery)
        db.session.commit()
        return delivery.id


def test_list_deliveries_as_buyer(client, buyer_token, order_id):
    delivery_id = _create_delivery(client, order_id)
    resp = client.get("/api/v1/deliveries", headers={"Authorization": f"Bearer {buyer_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == delivery_id
    assert data["items"][0]["order_id"] == order_id


def test_list_deliveries_as_retailer(client, retailer_token, order_id):
    delivery_id = _create_delivery(client, order_id)
    resp = client.get("/api/v1/deliveries", headers={"Authorization": f"Bearer {retailer_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == delivery_id


def test_list_deliveries_unauthorized(client):
    resp = client.get("/api/v1/deliveries")
    assert resp.status_code == 401


def test_assign_rider_success(client, retailer_token, rider_token, order_id):
    delivery_id = _create_delivery(client, order_id)
    resp = client.post(
        f"/api/v1/deliveries/{delivery_id}/assign",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={
            "rider_id": "dummy-rider-id",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["rider_id"] == "dummy-rider-id"
    assert data["status"] == "assigned"


def test_assign_rider_unauthorized(client, order_id):
    delivery_id = _create_delivery(client, order_id)
    resp = client.post(
        f"/api/v1/deliveries/{delivery_id}/assign",
        json={
            "rider_id": "dummy-rider-id",
        },
    )
    assert resp.status_code == 401


def test_assign_rider_forbidden(client, buyer_token, retailer_token, shop_id, listing_id, order_id):
    other_retailer_token = get_auth_token(
        client, "other_d4@test.com", "password123", role="retailer"
    )
    other_shop_resp = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {other_retailer_token}"},
        json={
            "name": "Other Shop",
            "category": "electronics",
        },
    )
    assert other_shop_resp.status_code == 201

    delivery_id = _create_delivery(client, order_id)
    resp = client.post(
        f"/api/v1/deliveries/{delivery_id}/assign",
        headers={"Authorization": f"Bearer {other_retailer_token}"},
        json={
            "rider_id": "dummy-rider-id",
        },
    )
    assert resp.status_code == 400


def test_assign_rider_missing_rider_id(client, retailer_token, order_id):
    delivery_id = _create_delivery(client, order_id)
    resp = client.post(
        f"/api/v1/deliveries/{delivery_id}/assign",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={},
    )
    assert resp.status_code == 400


def test_update_delivery_status_rider(client, rider_token, rider_profile_id, order_id):
    delivery_id = _create_delivery(client, order_id, status="assigned")
    from server.extensions import db
    from server.models import Delivery

    with client.application.app_context():
        delivery = db.session.query(Delivery).filter_by(id=delivery_id).first()
        delivery.rider_id = rider_profile_id
        db.session.commit()

    resp = client.patch(
        f"/api/v1/deliveries/{delivery_id}",
        headers={"Authorization": f"Bearer {rider_token}"},
        json={
            "status": "picked_up",
        },
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "picked_up"


def test_update_delivery_status_retailer(client, retailer_token, order_id):
    delivery_id = _create_delivery(client, order_id, status="assigned")
    resp = client.patch(
        f"/api/v1/deliveries/{delivery_id}",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={
            "status": "in_transit",
        },
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "in_transit"


def test_update_delivery_forbidden(client, buyer_token, order_id):
    delivery_id = _create_delivery(client, order_id, status="assigned")
    resp = client.patch(
        f"/api/v1/deliveries/{delivery_id}",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "status": "picked_up",
        },
    )
    assert resp.status_code == 400


def test_update_delivery_unauthorized(client, order_id):
    delivery_id = _create_delivery(client, order_id)
    resp = client.patch(f"/api/v1/deliveries/{delivery_id}", json={"status": "picked_up"})
    assert resp.status_code == 401


def test_update_delivery_not_found(client, retailer_token):
    resp = client.patch(
        "/api/v1/deliveries/nonexistent-delivery",
        headers={"Authorization": f"Bearer {retailer_token}"},
        json={
            "status": "picked_up",
        },
    )
    assert resp.status_code == 400
