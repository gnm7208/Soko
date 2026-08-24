import io


def get_auth_token(
    client, email, password="password123", full_name="Shop Owner", phone=None, role="retailer"
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


def test_create_shop_success(client):
    token = get_auth_token(client, "shop-create@example.com")
    resp = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Nairobi Books",
            "description": "Sells books",
            "category": "books",
            "address": "Nairobi",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Nairobi Books"
    assert data["category"] == "books"
    assert data["owner_id"]
    assert data["status"] == "pending"


def test_create_shop_requires_auth(client):
    resp = client.post(
        "/api/v1/shops",
        json={
            "name": "No Auth Shop",
            "category": "books",
        },
    )
    assert resp.status_code == 401


def test_create_shop_validation_error(client):
    token = get_auth_token(client, "shop-bad@example.com")
    resp = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "x",
            "category": "",
        },
    )
    assert resp.status_code == 500
    assert "error" in resp.get_json()


def test_list_shops(client):
    token = get_auth_token(client, "shop-list@example.com")
    client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Listed Shop",
            "category": "electronics",
        },
    )
    resp = client.get("/api/v1/shops")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data
    assert data["total"] >= 1
    assert any(s["name"] == "Listed Shop" for s in data["items"])


def test_get_shop_detail(client):
    token = get_auth_token(client, "shop-detail@example.com")
    created = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Detail Shop",
            "category": "fashion",
        },
    ).get_json()
    resp = client.get(f"/api/v1/shops/{created['id']}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == created["id"]
    assert data["name"] == "Detail Shop"


def test_get_shop_detail_not_found(client):
    resp = client.get("/api/v1/shops/nonexistent-id")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_update_shop_success(client):
    token = get_auth_token(client, "shop-update@example.com")
    created = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Old Name",
            "category": "home",
        },
    ).get_json()
    resp = client.patch(
        f"/api/v1/shops/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Name",
            "description": "Updated description",
            "category": "updated-cat",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "New Name"
    assert data["description"] == "Updated description"
    assert data["category"] == "updated-cat"


def test_update_shop_not_owner(client):
    owner_token = get_auth_token(client, "shop-owner@example.com")
    created = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Owner Shop",
            "category": "toys",
        },
    ).get_json()
    other_token = get_auth_token(client, "shop-other@example.com")
    resp = client.patch(
        f"/api/v1/shops/{created['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={
            "name": "Hijacked",
            "category": "toys",
        },
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_update_shop_requires_retailer(client):
    buyer_token = get_auth_token(client, "shop-buyer@example.com", role="buyer")
    resp = client.patch(
        "/api/v1/shops/some-id",
        headers={"Authorization": f"Bearer {buyer_token}"},
        json={
            "name": "Nope",
        },
    )
    assert resp.status_code in (403, 404)


def test_update_shop_sets_logo_and_cover_urls(client):
    token = get_auth_token(client, "shop-pictures@example.com")
    created = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Picture Shop", "category": "electronics"},
    ).get_json()
    resp = client.patch(
        f"/api/v1/shops/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Picture Shop",
            "category": "electronics",
            "logo_url": "https://images.unsplash.com/logo.jpg",
            "cover_url": "https://images.unsplash.com/cover.jpg",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["logo_url"] == "https://images.unsplash.com/logo.jpg"
    assert data["cover_url"] == "https://images.unsplash.com/cover.jpg"

    # Re-fetch on a separate request to confirm this actually persisted to the DB
    # column, not just the in-memory response object from the PATCH itself.
    refetched = client.get(f"/api/v1/shops/{created['id']}").get_json()
    assert refetched["logo_url"] == "https://images.unsplash.com/logo.jpg"
    assert refetched["cover_url"] == "https://images.unsplash.com/cover.jpg"


def test_upload_shop_image_success(client):
    token = get_auth_token(client, "shop-image@example.com")
    created = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Image Shop", "category": "fashion"},
    ).get_json()
    resp = client.post(
        f"/api/v1/shops/{created['id']}/images",
        headers={"Authorization": f"Bearer {token}"},
        data={"kind": "cover", "file": (io.BytesIO(b"fake-image-bytes"), "cover.jpg")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["cover_url"].startswith("/static/uploads/shops/")

    # Re-fetch on a separate request to confirm this actually persisted.
    refetched = client.get(f"/api/v1/shops/{created['id']}").get_json()
    assert refetched["cover_url"] == data["cover_url"]


def test_upload_shop_image_not_owner(client):
    owner_token = get_auth_token(client, "shop-image-owner@example.com")
    created = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Owned Image Shop", "category": "beauty"},
    ).get_json()
    other_token = get_auth_token(client, "shop-image-other@example.com")
    resp = client.post(
        f"/api/v1/shops/{created['id']}/images",
        headers={"Authorization": f"Bearer {other_token}"},
        data={"kind": "logo", "file": (io.BytesIO(b"fake-image-bytes"), "logo.jpg")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_upload_shop_image_rejects_unsupported_type(client):
    token = get_auth_token(client, "shop-image-badtype@example.com")
    created = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Badtype Shop", "category": "home"},
    ).get_json()
    resp = client.post(
        f"/api/v1/shops/{created['id']}/images",
        headers={"Authorization": f"Bearer {token}"},
        data={"kind": "logo", "file": (io.BytesIO(b"not-an-image"), "logo.txt")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
