import io


def test_register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "phone": "+254700000000",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "access_token" in data
    assert data["profile"]["role"] == "buyer"
    assert data["profile"]["full_name"] == "Test User"


def test_register_retailer_has_no_shop_until_they_create_one(client):
    # Registering with role="retailer" only sets the role — it does not create
    # a shop (POST /shops does that, and Shop.owner_id is unique, so we can't
    # auto-create one at registration without breaking that flow for anyone
    # who already owns a shop). /shops/mine should clearly say "none yet"
    # rather than a route elsewhere silently defaulting to someone else's shop.
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new-retailer@example.com",
            "password": "password123",
            "full_name": "New Retailer",
            "role": "retailer",
        },
    )
    assert response.status_code == 201
    token = response.get_json()["access_token"]

    shop_response = client.get(
        "/api/v1/shops/mine", headers={"Authorization": f"Bearer {token}"}
    )
    assert shop_response.status_code == 400

    create_response = client.post(
        "/api/v1/shops",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New Retailer's Shop", "category": "General"},
    )
    assert create_response.status_code == 201

    shop_response = client.get(
        "/api/v1/shops/mine", headers={"Authorization": f"Bearer {token}"}
    )
    assert shop_response.status_code == 200
    assert shop_response.get_json()["name"] == "New Retailer's Shop"


def test_register_buyer_cannot_access_shops_mine(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new-buyer@example.com",
            "password": "password123",
            "full_name": "New Buyer",
        },
    )
    token = response.get_json()["access_token"]
    shop_response = client.get(
        "/api/v1/shops/mine", headers={"Authorization": f"Bearer {token}"}
    )
    assert shop_response.status_code == 403


def test_register_duplicate(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "password123",
            "full_name": "Dup User",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "password123",
            "full_name": "Dup User",
        },
    )
    assert response.status_code == 409


def test_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
            "full_name": "Login User",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


def test_login_invalid(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrong",
        },
    )
    assert response.status_code == 401


def test_get_me(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "password123",
            "full_name": "Me User",
        },
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "me@example.com",
            "password": "password123",
        },
    )
    token = login_resp.get_json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["user_id"] == "me@example.com"


def test_update_me(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "update@example.com",
            "password": "password123",
            "full_name": "Update User",
        },
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "update@example.com",
            "password": "password123",
        },
    )
    token = login_resp.get_json()["access_token"]
    response = client.patch(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Updated Name",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["full_name"] == "Updated Name"


def test_upload_avatar_is_actually_servable(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "avatar@example.com",
            "password": "password123",
            "full_name": "Avatar User",
        },
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "avatar@example.com", "password": "password123"},
    )
    token = login_resp.get_json()["access_token"]

    resp = client.post(
        "/api/v1/auth/me/avatar",
        headers={"Authorization": f"Bearer {token}"},
        data={"file": (io.BytesIO(b"fake-avatar-bytes"), "avatar.png")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    avatar_url = resp.get_json()["avatar_url"]
    assert avatar_url.startswith("/static/uploads/avatars/")

    # The URL handed back must actually be servable, not just a path string
    # stored on the profile — a STORAGE_PATH resolution mismatch between the
    # upload (cwd-relative) and the static route (app-root-relative) would
    # silently 404 this while the upload response itself still looks fine.
    served = client.get(avatar_url)
    assert served.status_code == 200
    assert served.data == b"fake-avatar-bytes"

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.get_json()["avatar_url"] == avatar_url
