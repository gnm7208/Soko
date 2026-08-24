from datetime import datetime, timedelta


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


class TestPromotions:
    def test_create_promotion(self, client):
        retailer_token = get_auth_token(
            client, "promo-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Promo Shop")
        listing_id = create_listing(
            client, retailer_token, shop_id, title="Promo Product", price=2000
        )

        now = datetime.utcnow()
        starts_at = (now - timedelta(hours=1)).isoformat()
        ends_at = (now + timedelta(days=7)).isoformat()

        response = client.post(
            "/api/v1/promotions",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={
                "listing_id": listing_id,
                "discount_pct": 20,
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["discount_pct"] == 20
        assert data["listing_id"] == listing_id
        assert data["shop_id"] == shop_id
        assert "active" in data

    def test_create_promotion_invalid_discount(self, client):
        retailer_token = get_auth_token(
            client, "promo-retailer2@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Promo Shop 2")
        listing_id = create_listing(client, retailer_token, shop_id, title="Promo Product 2")

        now = datetime.utcnow()
        starts_at = (now - timedelta(hours=1)).isoformat()
        ends_at = (now + timedelta(days=7)).isoformat()

        response = client.post(
            "/api/v1/promotions",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={
                "listing_id": listing_id,
                "discount_pct": 100,
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )
        assert response.status_code == 500

    def test_create_promotion_other_retailer_listing(self, client):
        retailer_token = get_auth_token(
            client, "promo-retailer3@example.com", "password123", role="retailer"
        )
        other_retailer_token = get_auth_token(
            client, "promo-other-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, other_retailer_token, name="Other Promo Shop")
        listing_id = create_listing(
            client, other_retailer_token, shop_id, title="Other Promo Product"
        )

        now = datetime.utcnow()
        starts_at = (now - timedelta(hours=1)).isoformat()
        ends_at = (now + timedelta(days=7)).isoformat()

        response = client.post(
            "/api/v1/promotions",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={
                "listing_id": listing_id,
                "discount_pct": 15,
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )
        assert response.status_code == 400

    def test_list_promotions(self, client):
        retailer_token = get_auth_token(
            client, "promo-retailer4@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Promo Shop 4")
        listing_id = create_listing(client, retailer_token, shop_id, title="Promo Product 4")

        now = datetime.utcnow()
        starts_at = (now - timedelta(hours=1)).isoformat()
        ends_at = (now + timedelta(days=7)).isoformat()

        client.post(
            "/api/v1/promotions",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={
                "listing_id": listing_id,
                "discount_pct": 10,
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )

        response = client.get(
            "/api/v1/promotions", headers={"Authorization": f"Bearer {retailer_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["discount_pct"] == 10
        assert data["total"] == 1

    def test_list_promotions_empty(self, client):
        retailer_token = get_auth_token(
            client, "promo-retailer5@example.com", "password123", role="retailer"
        )
        create_shop(client, retailer_token, name="Promo Shop 5")

        response = client.get(
            "/api/v1/promotions", headers={"Authorization": f"Bearer {retailer_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_cancel_promotion(self, client):
        retailer_token = get_auth_token(
            client, "promo-retailer6@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Promo Shop 6")
        listing_id = create_listing(client, retailer_token, shop_id, title="Promo Product 6")

        now = datetime.utcnow()
        starts_at = (now - timedelta(hours=1)).isoformat()
        ends_at = (now + timedelta(days=7)).isoformat()

        create_resp = client.post(
            "/api/v1/promotions",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={
                "listing_id": listing_id,
                "discount_pct": 25,
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )
        assert create_resp.status_code == 201
        promo_id = create_resp.get_json()["id"]

        response = client.delete(
            f"/api/v1/promotions/{promo_id}",
            headers={"Authorization": f"Bearer {retailer_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Promotion cancelled"

    def test_create_promotion_buyer_forbidden(self, client):
        buyer_token = get_auth_token(client, "promo-buyer@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "promo-retailer7@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Promo Shop 7")
        listing_id = create_listing(client, retailer_token, shop_id, title="Promo Product 7")

        now = datetime.utcnow()
        starts_at = (now - timedelta(hours=1)).isoformat()
        ends_at = (now + timedelta(days=7)).isoformat()

        response = client.post(
            "/api/v1/promotions",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "listing_id": listing_id,
                "discount_pct": 10,
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
        )
        assert response.status_code == 403
