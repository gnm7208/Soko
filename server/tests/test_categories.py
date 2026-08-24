import uuid

from flask_jwt_extended import create_access_token

from server.extensions import db
from server.models import Profile


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


def get_admin_token(app):
    with app.app_context():
        profile_id = str(uuid.uuid4())
        admin = Profile(
            id=profile_id,
            user_id="admin@example.com",
            role="admin",
            full_name="Admin User",
            password_hash="hashed",
        )
        db.session.add(admin)
        db.session.commit()
        token = create_access_token(
            identity="admin@example.com",
            additional_claims={"role": "admin", "profile_id": profile_id},
        )
    return token


def test_list_categories_empty(client):
    resp = client.get("/api/v1/categories")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_categories_with_data(client, app):
    admin_token = get_admin_token(app)
    client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Electronics",
            "slug": "electronics",
        },
    )
    client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Phones",
            "slug": "phones",
        },
    )
    resp = client.get("/api/v1/categories")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    names = {c["name"] for c in data}
    assert names == {"Electronics", "Phones"}


def test_create_category_success(client, app):
    admin_token = get_admin_token(app)
    resp = client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Books",
            "slug": "books",
            "icon": "book",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Books"
    assert data["slug"] == "books"
    assert data["id"]


def test_create_category_requires_admin(client):
    token = get_auth_token(client, "cat-buyer@example.com", role="buyer")
    resp = client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "No Perm",
            "slug": "no-perm",
        },
    )
    assert resp.status_code == 403


def test_create_category_validation_error(client, app):
    admin_token = get_admin_token(app)
    resp = client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "",
            "slug": "bad",
        },
    )
    assert resp.status_code == 500
    assert "error" in resp.get_json()


def test_create_category_duplicate(client, app):
    admin_token = get_admin_token(app)
    payload = {"name": "Unique", "slug": "unique"}
    client.post(
        "/api/v1/categories", headers={"Authorization": f"Bearer {admin_token}"}, json=payload
    )
    resp = client.post(
        "/api/v1/categories", headers={"Authorization": f"Bearer {admin_token}"}, json=payload
    )
    assert resp.status_code == 500
    assert "error" in resp.get_json()


def test_update_category_success(client, app):
    admin_token = get_admin_token(app)
    created = client.post(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Old Cat",
            "slug": "old-cat",
        },
    ).get_json()
    resp = client.patch(
        f"/api/v1/categories/{created['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "New Cat",
            "icon": "star",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "New Cat"
    assert data["icon"] == "star"


def test_update_category_not_found(client, app):
    admin_token = get_admin_token(app)
    resp = client.patch(
        "/api/v1/categories/nonexistent-id",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Ghost",
        },
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_update_category_requires_admin(client):
    token = get_auth_token(client, "cat-buyer2@example.com", role="buyer")
    resp = client.patch(
        "/api/v1/categories/some-id",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Nope",
        },
    )
    assert resp.status_code == 403
