import uuid

from server.extensions import db
from server.models import Profile


def get_auth_token(client, email, password="password123", role="buyer"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": f"User {email}", "role": role},
    )
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.get_json()["access_token"]


def get_admin_token(app, email="dispute-admin@example.com"):
    from flask_jwt_extended import create_access_token

    with app.app_context():
        profile_id = str(uuid.uuid4())
        admin = Profile(
            id=profile_id,
            user_id=email,
            role="admin",
            full_name="Admin User",
            password_hash="hashed",
        )
        db.session.add(admin)
        db.session.commit()
        token = create_access_token(
            identity=email, additional_claims={"role": "admin", "profile_id": profile_id}
        )
    return token


def create_shop(client, token, name="Dispute Shop"):
    resp = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "category": "electronics"},
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def create_listing(client, token, title="Dispute Product", price=1000):
    resp = client.post(
        "/api/v1/listings",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": title, "price": price, "stock": 10, "condition": "new"},
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def create_order(client, token, shop_id, listing_id):
    resp = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": 1}],
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


class TestDisputes:
    def test_buyer_can_raise_dispute(self, client):
        retailer_token = get_auth_token(client, "dispute-retailer1@example.com", role="retailer")
        buyer_token = get_auth_token(client, "dispute-buyer1@example.com", role="buyer")
        shop_id = create_shop(client, retailer_token)
        listing_id = create_listing(client, retailer_token)
        order_id = create_order(client, buyer_token, shop_id, listing_id)

        resp = client.post(
            "/api/v1/disputes",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={"order_id": order_id, "reason": "Item arrived damaged"},
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["order_id"] == order_id
        assert data["status"] == "open"
        assert data["reason"] == "Item arrived damaged"

    def test_shop_owner_can_raise_dispute(self, client):
        retailer_token = get_auth_token(client, "dispute-retailer2@example.com", role="retailer")
        buyer_token = get_auth_token(client, "dispute-buyer2@example.com", role="buyer")
        shop_id = create_shop(client, retailer_token)
        listing_id = create_listing(client, retailer_token)
        order_id = create_order(client, buyer_token, shop_id, listing_id)

        resp = client.post(
            "/api/v1/disputes",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"order_id": order_id, "reason": "Buyer refuses delivery"},
        )
        assert resp.status_code == 201

    def test_unrelated_user_forbidden(self, client):
        retailer_token = get_auth_token(client, "dispute-retailer3@example.com", role="retailer")
        buyer_token = get_auth_token(client, "dispute-buyer3@example.com", role="buyer")
        other_token = get_auth_token(client, "dispute-other3@example.com", role="buyer")
        shop_id = create_shop(client, retailer_token)
        listing_id = create_listing(client, retailer_token)
        order_id = create_order(client, buyer_token, shop_id, listing_id)

        resp = client.post(
            "/api/v1/disputes",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"order_id": order_id, "reason": "Not my order"},
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_list_my_disputes(self, client):
        retailer_token = get_auth_token(client, "dispute-retailer4@example.com", role="retailer")
        buyer_token = get_auth_token(client, "dispute-buyer4@example.com", role="buyer")
        shop_id = create_shop(client, retailer_token)
        listing_id = create_listing(client, retailer_token)
        order_id = create_order(client, buyer_token, shop_id, listing_id)
        client.post(
            "/api/v1/disputes",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={"order_id": order_id, "reason": "Wrong item"},
        )

        resp = client.get(
            "/api/v1/disputes/mine", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] >= 1
        assert any(d["order_id"] == order_id for d in data["items"])

    def test_admin_list_and_resolve_dispute(self, client, app):
        retailer_token = get_auth_token(client, "dispute-retailer5@example.com", role="retailer")
        buyer_token = get_auth_token(client, "dispute-buyer5@example.com", role="buyer")
        shop_id = create_shop(client, retailer_token)
        listing_id = create_listing(client, retailer_token)
        order_id = create_order(client, buyer_token, shop_id, listing_id)
        created = client.post(
            "/api/v1/disputes",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={"order_id": order_id, "reason": "Needs admin review"},
        ).get_json()

        admin_token = get_admin_token(app)
        list_resp = client.get(
            "/api/v1/admin/disputes?status=open",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert list_resp.status_code == 200
        assert any(d["id"] == created["id"] for d in list_resp.get_json()["items"])

        resolve_resp = client.patch(
            f"/api/v1/admin/disputes/{created['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "resolved", "resolution_note": "Refund issued"},
        )
        assert resolve_resp.status_code == 200
        data = resolve_resp.get_json()
        assert data["status"] == "resolved"
        assert data["resolution_note"] == "Refund issued"

    def test_admin_disputes_non_admin_forbidden(self, client):
        buyer_token = get_auth_token(client, "dispute-buyer6@example.com", role="buyer")
        resp = client.get(
            "/api/v1/admin/disputes", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert resp.status_code == 403
