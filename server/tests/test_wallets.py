from server.extensions import db
from server.models import Profile, Wallet, WalletTransaction


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


class TestWallets:
    def test_get_wallet(self, client, app):
        retailer_token = get_auth_token(
            client, "wallet-retailer@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="wallet-retailer@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=5000, currency="KES")
            db.session.add(wallet)
            db.session.commit()

        response = client.get(
            "/api/v1/wallets/me", headers={"Authorization": f"Bearer {retailer_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "id" in data
        assert data["balance"] == 5000
        assert data["currency"] == "KES"
        assert "user_id" in data

    def test_get_wallet_not_found(self, client):
        retailer_token = get_auth_token(
            client, "wallet-retailer2@example.com", "password123", role="retailer"
        )

        response = client.get(
            "/api/v1/wallets/me", headers={"Authorization": f"Bearer {retailer_token}"}
        )
        assert response.status_code == 400

    def test_list_transactions(self, client, app):
        retailer_token = get_auth_token(
            client, "wallet-retailer3@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="wallet-retailer3@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=5000, currency="KES")
            db.session.add(wallet)
            db.session.commit()

            txn = WalletTransaction(
                wallet_id=wallet.id,
                type="credit",
                amount=5000,
                ref="order-payment",
                status="completed",
            )
            db.session.add(txn)
            db.session.commit()

        response = client.get(
            "/api/v1/wallets/me/transactions", headers={"Authorization": f"Bearer {retailer_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["amount"] == 5000
        assert data["items"][0]["type"] == "credit"
        assert data["total"] == 1

    def test_list_transactions_empty(self, client, app):
        retailer_token = get_auth_token(
            client, "wallet-retailer4@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="wallet-retailer4@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=0, currency="KES")
            db.session.add(wallet)
            db.session.commit()

        response = client.get(
            "/api/v1/wallets/me/transactions", headers={"Authorization": f"Bearer {retailer_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_request_payout(self, client, app):
        retailer_token = get_auth_token(
            client, "wallet-retailer5@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="wallet-retailer5@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=10000, currency="KES")
            db.session.add(wallet)
            db.session.commit()

        response = client.post(
            "/api/v1/wallets/payout-request",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"amount": 5000, "note": "Monthly payout"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["amount"] == 5000
        assert data["status"] == "pending"
        assert data["note"] == "Monthly payout"
        assert "wallet_id" in data

    def test_request_payout_insufficient_balance(self, client, app):
        retailer_token = get_auth_token(
            client, "wallet-retailer6@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="wallet-retailer6@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=1000, currency="KES")
            db.session.add(wallet)
            db.session.commit()

        response = client.post(
            "/api/v1/wallets/payout-request",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"amount": 5000},
        )
        assert response.status_code == 400

    def test_request_payout_buyer_forbidden(self, client, app):
        buyer_token = get_auth_token(
            client, "wallet-buyer@example.com", "password123", role="buyer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="wallet-buyer@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=5000, currency="KES")
            db.session.add(wallet)
            db.session.commit()

        response = client.post(
            "/api/v1/wallets/payout-request",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={"amount": 1000},
        )
        assert response.status_code == 403

    def test_request_payout_invalid_amount(self, client, app):
        retailer_token = get_auth_token(
            client, "wallet-retailer7@example.com", "password123", role="retailer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="wallet-retailer7@example.com").first()
            wallet = Wallet(owner_id=profile.id, balance=10000, currency="KES")
            db.session.add(wallet)
            db.session.commit()

        response = client.post(
            "/api/v1/wallets/payout-request",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"amount": 0},
        )
        assert response.status_code == 500
