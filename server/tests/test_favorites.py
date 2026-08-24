def get_auth_token(
    client, email, password="password123", full_name="Test User", phone=None, role="buyer"
):
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role,
    }
    if phone:
        payload["phone"] = phone
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.get_json()["access_token"]


def create_retailer_with_shop(client, email, shop_name="Fav Shop", category="general"):
    token = get_auth_token(client, email, role="retailer", full_name="Retailer")
    shop = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": shop_name,
            "category": category,
        },
    ).get_json()
    return token, shop["id"]


def create_listing(client, token, shop_id, title="Fav Item", price=1500):
    return client.post(
        "/api/v1/listings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "price": price,
        },
    ).get_json()


def test_toggle_favorite_add(client):
    buyer_token = get_auth_token(client, "fav-buyer@example.com", role="buyer")
    seller_token, shop_id = create_retailer_with_shop(client, "fav-seller@example.com")
    listing = create_listing(client, seller_token, shop_id, title="Favoritable", price=100)
    resp = client.post(
        f"/api/v1/favorites/{listing['id']}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["favorited"] is True


def test_toggle_favorite_remove(client):
    buyer_token = get_auth_token(client, "fav-buyer2@example.com", role="buyer")
    seller_token, shop_id = create_retailer_with_shop(client, "fav-seller2@example.com")
    listing = create_listing(client, seller_token, shop_id, title="Toggle Me", price=100)
    client.post(
        f"/api/v1/favorites/{listing['id']}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    resp = client.post(
        f"/api/v1/favorites/{listing['id']}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["favorited"] is False


def test_toggle_favorite_retailer_allowed(client):
    seller_token, shop_id = create_retailer_with_shop(client, "fav-seller3@example.com")
    listing = create_listing(
        client, seller_token, shop_id, title="Retailer Can Favorite", price=100
    )
    resp = client.post(
        f"/api/v1/favorites/{listing['id']}", headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["favorited"] is True


def test_toggle_favorite_requires_auth(client):
    seller_token, shop_id = create_retailer_with_shop(client, "fav-seller4@example.com")
    listing = create_listing(client, seller_token, shop_id, title="No Auth Fav", price=100)
    resp = client.post(f"/api/v1/favorites/{listing['id']}")
    assert resp.status_code == 401


def test_list_favorites_empty(client):
    buyer_token = get_auth_token(client, "fav-empty@example.com", role="buyer")
    resp = client.get("/api/v1/favorites", headers={"Authorization": f"Bearer {buyer_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_favorites(client):
    buyer_token = get_auth_token(client, "fav-list@example.com", role="buyer")
    seller_token, shop_id = create_retailer_with_shop(client, "fav-seller5@example.com")
    listing = create_listing(client, seller_token, shop_id, title="My Favorite", price=100)
    client.post(
        f"/api/v1/favorites/{listing['id']}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    resp = client.get("/api/v1/favorites", headers={"Authorization": f"Bearer {buyer_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == listing["id"]
    assert data["items"][0]["title"] == "My Favorite"


def test_list_favorites_retailer_allowed(client):
    seller_token, shop_id = create_retailer_with_shop(client, "fav-seller6@example.com")
    resp = client.get("/api/v1/favorites", headers={"Authorization": f"Bearer {seller_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data
    assert data["items"] == []


def test_favorites_remove_from_list(client):
    buyer_token = get_auth_token(client, "fav-remove@example.com", role="buyer")
    seller_token, shop_id = create_retailer_with_shop(client, "fav-seller7@example.com")
    listing = create_listing(client, seller_token, shop_id, title="Temp Favorite", price=100)
    client.post(
        f"/api/v1/favorites/{listing['id']}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    client.post(
        f"/api/v1/favorites/{listing['id']}", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    resp = client.get("/api/v1/favorites", headers={"Authorization": f"Bearer {buyer_token}"})
    assert resp.get_json()["total"] == 0
