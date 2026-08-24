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


def create_retailer_with_shop(client, email, shop_name="Test Shop", category="general"):
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


def create_listing(client, token, shop_id, title="Test Item", price=1000, **extra):
    payload = {"title": title, "price": price}
    payload.update(extra)
    return client.post(
        "/api/v1/listings", headers={"Authorization": f"Bearer {token}"}, json=payload
    )


def test_create_listing_success(client):
    token, shop_id = create_retailer_with_shop(client, "listing-create@example.com")
    resp = create_listing(
        client,
        token,
        shop_id,
        title="Vintage Chair",
        price=2500,
        description="Nice chair",
        condition="used",
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Vintage Chair"
    assert data["price"] == 2500
    assert data["shop_id"] == shop_id
    assert data["status"] == "active"
    assert data["currency"] == "KES"


def test_create_listing_requires_auth(client):
    resp = create_listing(client, "invalid-token", "shop-id")
    assert resp.status_code == 422


def test_create_listing_requires_retailer(client):
    buyer_token = get_auth_token(client, "listing-buyer@example.com", role="buyer")
    resp = create_listing(client, buyer_token, "shop-id")
    assert resp.status_code == 403


def test_create_listing_validation_error(client):
    token, shop_id = create_retailer_with_shop(client, "listing-bad@example.com")
    resp = create_listing(client, token, shop_id, title="x", price=0)
    assert resp.status_code == 500
    assert "error" in resp.get_json()


def test_list_listings(client):
    token, shop_id = create_retailer_with_shop(client, "listing-list@example.com")
    create_listing(client, token, shop_id, title="Listing One", price=100)
    create_listing(client, token, shop_id, title="Listing Two", price=200)
    resp = client.get("/api/v1/listings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data
    assert data["total"] >= 2
    titles = {l["title"] for l in data["items"]}
    assert "Listing One" in titles
    assert "Listing Two" in titles


def test_get_listing_detail(client):
    token, shop_id = create_retailer_with_shop(client, "listing-detail@example.com")
    created = create_listing(client, token, shop_id, title="Detail Item", price=500).get_json()
    resp = client.get(f"/api/v1/listings/{created['id']}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == created["id"]
    assert data["title"] == "Detail Item"


def test_get_listing_detail_not_found(client):
    resp = client.get("/api/v1/listings/nonexistent-id")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_update_listing_success(client):
    token, shop_id = create_retailer_with_shop(client, "listing-update@example.com")
    created = create_listing(client, token, shop_id, title="Old Title", price=100).get_json()
    resp = client.patch(
        f"/api/v1/listings/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "New Title",
            "price": 999,
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "New Title"
    assert data["price"] == 999


def test_update_listing_not_owner(client):
    owner_token, shop_id = create_retailer_with_shop(client, "listing-owner@example.com")
    created = create_listing(client, owner_token, shop_id, title="Owned", price=100).get_json()
    other_token, _ = create_retailer_with_shop(client, "listing-other@example.com")
    resp = client.patch(
        f"/api/v1/listings/{created['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={
            "title": "Hijacked",
        },
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_soft_delete_listing(client):
    token, shop_id = create_retailer_with_shop(client, "listing-delete@example.com")
    created = create_listing(client, token, shop_id, title="To Delete", price=100).get_json()
    resp = client.delete(
        f"/api/v1/listings/{created['id']}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["message"]
    detail = client.get(f"/api/v1/listings/{created['id']}").get_json()
    assert detail["status"] == "deleted"


def test_soft_delete_listing_not_owner(client):
    owner_token, shop_id = create_retailer_with_shop(client, "listing-del-owner@example.com")
    created = create_listing(client, owner_token, shop_id, title="Owned Del", price=100).get_json()
    other_token, _ = create_retailer_with_shop(client, "listing-del-other@example.com")
    resp = client.delete(
        f"/api/v1/listings/{created['id']}", headers={"Authorization": f"Bearer {other_token}"}
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_upload_listing_image(client):
    token, shop_id = create_retailer_with_shop(client, "listing-img@example.com")
    created = create_listing(client, token, shop_id, title="With Image", price=100).get_json()
    resp = client.post(
        f"/api/v1/listings/{created['id']}/images",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "url": "https://example.com/img.jpg",
            "position": 0,
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["url"] == "https://example.com/img.jpg"
    assert data["position"] == 0


def test_upload_listing_image_missing_url(client):
    token, shop_id = create_retailer_with_shop(client, "listing-img-bad@example.com")
    created = create_listing(client, token, shop_id, title="Img Bad", price=100).get_json()
    resp = client.post(
        f"/api/v1/listings/{created['id']}/images",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert resp.status_code == 400


def test_upload_listing_image_not_owner(client):
    owner_token, shop_id = create_retailer_with_shop(client, "listing-img-owner@example.com")
    created = create_listing(client, owner_token, shop_id, title="Img Owned", price=100).get_json()
    other_token, _ = create_retailer_with_shop(client, "listing-img-other@example.com")
    resp = client.post(
        f"/api/v1/listings/{created['id']}/images",
        headers={"Authorization": f"Bearer {other_token}"},
        json={
            "url": "https://example.com/x.jpg",
        },
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()
