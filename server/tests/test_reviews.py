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


class TestReviews:
    def test_create_review(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": "delivered"},
        )

        response = client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 5,
                "comment": "Excellent product!",
            },
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["rating"] == 5
        assert data["comment"] == "Excellent product!"
        assert data["order_id"] == order_id
        assert data["shop_id"] == shop_id

    def test_create_review_without_comment(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer2@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer2@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop 2")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product 2")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": "delivered"},
        )

        response = client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 4,
            },
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["rating"] == 4
        assert data["comment"] is None

    def test_create_review_duplicate(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer3@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer3@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop 3")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product 3")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": "delivered"},
        )

        client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 5,
            },
        )

        response = client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 3,
            },
        )
        assert response.status_code == 409

    def test_create_review_not_delivered(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer4@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer4@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop 4")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product 4")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        response = client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 5,
            },
        )
        assert response.status_code == 201

    def test_create_review_invalid_rating(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer5@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer5@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop 5")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product 5")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": "delivered"},
        )

        response = client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 6,
            },
        )
        assert response.status_code == 500

    def test_list_shop_reviews(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer6@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer6@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop 6")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product 6")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": "delivered"},
        )

        client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 4,
                "comment": "Good",
            },
        )

        response = client.get(f"/api/v1/shops/{shop_id}/reviews")
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["rating"] == 4
        assert data["total"] == 1

    def test_list_shop_reviews_pagination(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer7@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer7@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop 7")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product 7")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": "delivered"},
        )

        client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 5,
            },
        )

        response = client.get(f"/api/v1/shops/{shop_id}/reviews?page=1&per_page=10")
        assert response.status_code == 200
        data = response.get_json()
        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_create_review_wrong_buyer(self, client):
        buyer_token = get_auth_token(
            client, "review-buyer8@example.com", "password123", role="buyer"
        )
        other_buyer_token = get_auth_token(
            client, "review-other-buyer@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "review-retailer8@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Review Shop 8")
        listing_id = create_listing(client, retailer_token, shop_id, title="Review Product 8")

        order_id = create_order(client, buyer_token, shop_id, listing_id)

        client.patch(
            f"/api/v1/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"status": "delivered"},
        )

        response = client.post(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {other_buyer_token}"},
            json={
                "order_id": order_id,
                "rating": 5,
            },
        )
        assert response.status_code == 400
