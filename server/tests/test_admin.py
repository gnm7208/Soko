import uuid

from server.extensions import db
from server.models import (
    Profile,
    Wallet,
    WalletTransaction,
)


def get_auth_token(client, email, password, role="buyer"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": f"User {email}",
            "role": role,
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.get_json()["access_token"]


def get_admin_token(app, email="admin@example.com"):
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
            identity=email,
            additional_claims={"role": "admin", "profile_id": profile_id},
        )
    return token


def create_shop(client, token, name="Test Shop", category="Retail"):
    response = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": name,
            "category": category,
            "description": "A test shop",
        },
    )
    assert response.status_code == 201
    return response.get_json()["id"]


def create_listing(client, token, shop_id, title="Test Product", price=1000):
    response = client.post(
        "/api/v1/listings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "price": price,
            "stock": 10,
            "condition": "new",
        },
    )
    assert response.status_code == 201
    return response.get_json()["id"]


def create_order(client, token, shop_id, listing_id, qty=1, payment_method="cash"):
    response = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": qty}],
            "payment_method": payment_method,
        },
    )
    assert response.status_code == 201
    return response.get_json()["id"]


class TestAdmin:
    def test_get_metrics(self, client, app):
        admin_token = get_admin_token(app)
        retailer_token = get_auth_token(
            client, "metrics-retailer@example.com", "password123", role="retailer"
        )
        buyer_token = get_auth_token(
            client, "metrics-buyer@example.com", "password123", role="buyer"
        )
        shop_id = create_shop(client, retailer_token, name="Metrics Shop")
        listing_id = create_listing(client, retailer_token, shop_id, title="Metrics Product")
        order_id = create_order(client, buyer_token, shop_id, listing_id, payment_method="cash")

        response = client.get(
            "/api/v1/admin/metrics", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "total_orders" in data
        assert "total_revenue" in data
        assert "total_shops" in data
        assert "total_users" in data
        assert "total_listings" in data
        assert data["total_orders"] >= 1
        assert data["total_shops"] >= 1
        assert data["total_users"] >= 3
        assert data["total_listings"] >= 1

    def test_get_metrics_non_admin_forbidden(self, client):
        buyer_token = get_auth_token(
            client, "metrics-buyer2@example.com", "password123", role="buyer"
        )

        response = client.get(
            "/api/v1/admin/metrics", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert response.status_code == 403

    def test_approve_shop(self, client, app):
        admin_token = get_admin_token(app)
        retailer_token = get_auth_token(
            client, "approve-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Approve Shop")

        response = client.patch(
            f"/api/v1/admin/shops/{shop_id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "approved"
        assert data["id"] == shop_id

    def test_approve_shop_not_found(self, client, app):
        admin_token = get_admin_token(app, email="admin-notfound@example.com")

        response = client.patch(
            "/api/v1/admin/shops/nonexistent-shop-id/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    def test_suspend_shop(self, client, app):
        admin_token = get_admin_token(app, email="admin-suspend@example.com")
        retailer_token = get_auth_token(
            client, "suspend-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Suspend Shop")

        response = client.patch(
            f"/api/v1/admin/shops/{shop_id}/suspend",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "suspended"

    def test_admin_update_listing(self, client, app):
        admin_token = get_admin_token(app, email="admin-list@example.com")
        retailer_token = get_auth_token(
            client, "adminlist-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Admin List Shop")
        listing_id = create_listing(client, retailer_token, shop_id, title="Original Title")

        response = client.patch(
            f"/api/v1/admin/listings/{listing_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "Updated Title", "status": "active"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "active"

    def test_admin_update_payout(self, client, app):
        admin_token = get_admin_token(app, email="admin-payout@example.com")
        retailer_token = get_auth_token(
            client, "payout-retailer@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="payout-retailer@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=10000, currency="KES")
            db.session.add(wallet)
            db.session.commit()

            txn = WalletTransaction(
                wallet_id=wallet.id,
                type="payout",
                amount=5000,
                ref="payout-request",
                status="pending",
            )
            db.session.add(txn)
            db.session.commit()
            payout_id = txn.id

        response = client.patch(
            f"/api/v1/admin/payouts/{payout_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "approved"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "approved"
        assert data["amount"] == 5000

    def test_admin_non_admin_forbidden(self, client):
        retailer_token = get_auth_token(
            client, "admin-retailer@example.com", "password123", role="retailer"
        )

        response = client.get(
            "/api/v1/admin/metrics", headers={"Authorization": f"Bearer {retailer_token}"}
        )
        assert response.status_code == 403

    def test_list_shops_filters_by_status(self, client, app):
        admin_token = get_admin_token(app, email="admin-listshops@example.com")
        retailer_token = get_auth_token(
            client, "listshops-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Pending Shop")

        response = client.get(
            "/api/v1/admin/shops?status=pending",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert any(s["id"] == shop_id for s in data["items"])

    def test_list_shops_non_admin_forbidden(self, client):
        buyer_token = get_auth_token(
            client, "listshops-buyer@example.com", "password123", role="buyer"
        )
        response = client.get(
            "/api/v1/admin/shops", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert response.status_code == 403

    def test_list_users(self, client, app):
        admin_token = get_admin_token(app, email="admin-listusers@example.com")
        get_auth_token(client, "listusers-buyer@example.com", "password123", role="buyer")

        response = client.get(
            "/api/v1/admin/users?role=buyer", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] >= 1
        assert all(u["role"] == "buyer" for u in data["items"])

    def test_list_users_non_admin_forbidden(self, client):
        buyer_token = get_auth_token(
            client, "listusers-buyer2@example.com", "password123", role="buyer"
        )
        response = client.get(
            "/api/v1/admin/users", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert response.status_code == 403

    def test_list_admin_listings(self, client, app):
        admin_token = get_admin_token(app, email="admin-listlistings@example.com")
        retailer_token = get_auth_token(
            client, "listlistings-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Listings Shop")
        listing_id = create_listing(client, retailer_token, shop_id, title="Moderated Product")

        response = client.get(
            "/api/v1/admin/listings", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert any(item["id"] == listing_id for item in data["items"])

    def test_list_admin_listings_non_admin_forbidden(self, client):
        buyer_token = get_auth_token(
            client, "listlistings-buyer@example.com", "password123", role="buyer"
        )
        response = client.get(
            "/api/v1/admin/listings", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert response.status_code == 403

    def test_list_payouts(self, client, app):
        admin_token = get_admin_token(app, email="admin-listpayouts@example.com")
        retailer_token = get_auth_token(
            client, "listpayouts-retailer@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="listpayouts-retailer@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=10000, currency="KES")
            db.session.add(wallet)
            db.session.commit()
            txn = WalletTransaction(
                wallet_id=wallet.id,
                type="payout",
                amount=3000,
                ref="payout-request",
                status="pending",
            )
            db.session.add(txn)
            db.session.commit()
            payout_id = txn.id

        response = client.get(
            "/api/v1/admin/payouts?status=pending",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert any(p["id"] == payout_id for p in data["items"])
        assert all("owner_name" in p for p in data["items"])

    def test_list_payouts_non_admin_forbidden(self, client):
        buyer_token = get_auth_token(
            client, "listpayouts-buyer@example.com", "password123", role="buyer"
        )
        response = client.get(
            "/api/v1/admin/payouts", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert response.status_code == 403
