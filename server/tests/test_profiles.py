import io


def get_auth_token(client, email, password="password123", role="buyer"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": f"User {email}", "role": role},
    )
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.get_json()["access_token"]


class TestProfiles:
    def test_upload_avatar_success(self, client):
        token = get_auth_token(client, "profile-avatar@example.com")
        resp = client.post(
            "/api/v1/auth/me/avatar",
            headers={"Authorization": f"Bearer {token}"},
            data={"file": (io.BytesIO(b"fake-image-bytes"), "avatar.png")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["avatar_url"]
        assert data["avatar_url"].startswith("/static/uploads/avatars/")

    def test_upload_avatar_requires_auth(self, client):
        resp = client.post(
            "/api/v1/auth/me/avatar",
            data={"file": (io.BytesIO(b"fake-image-bytes"), "avatar.png")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 401

    def test_upload_avatar_rejects_unsupported_type(self, client):
        token = get_auth_token(client, "profile-avatar-bad@example.com")
        resp = client.post(
            "/api/v1/auth/me/avatar",
            headers={"Authorization": f"Bearer {token}"},
            data={"file": (io.BytesIO(b"not-an-image"), "avatar.txt")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_upload_avatar_rejects_oversized_file(self, client):
        token = get_auth_token(client, "profile-avatar-big@example.com")
        oversized = io.BytesIO(b"0" * (5 * 1024 * 1024 + 1))
        resp = client.post(
            "/api/v1/auth/me/avatar",
            headers={"Authorization": f"Bearer {token}"},
            data={"file": (oversized, "avatar.png")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_get_profile_by_id(self, client):
        token = get_auth_token(client, "profile-getid@example.com")
        me = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        ).get_json()
        resp = client.get(f"/api/v1/profiles/{me['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == me["id"]
