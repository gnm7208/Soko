from server.models import Profile


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


def create_notification(user_id, type="order", title="Test Notification", body="Test body"):
    from server.services.notifications import create_notification

    return create_notification(user_id, type, {"title": title, "body": body})


class TestNotifications:
    def test_list_notifications(self, client, app):
        user_token = get_auth_token(client, "notif-user@example.com", "password123", role="buyer")
        with app.app_context():
            profile = Profile.query.filter_by(user_id="notif-user@example.com").first()
            create_notification(profile.id, "order", "Order Update", "Your order has been shipped")
            create_notification(profile.id, "message", "New Message", "You have a new message")

        response = client.get(
            "/api/v1/notifications", headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2
        titles = [item["title"] for item in data["items"]]
        assert "Order Update" in titles
        assert "New Message" in titles

    def test_list_notifications_empty(self, client):
        user_token = get_auth_token(client, "notif-empty@example.com", "password123", role="buyer")

        response = client.get(
            "/api/v1/notifications", headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_notifications_pagination(self, client, app):
        user_token = get_auth_token(client, "notif-page@example.com", "password123", role="buyer")
        with app.app_context():
            profile = Profile.query.filter_by(user_id="notif-page@example.com").first()
            for i in range(5):
                create_notification(profile.id, "system", f"Notification {i}", f"Body {i}")

        response = client.get(
            "/api/v1/notifications?page=1&per_page=2",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3

    def test_mark_notification_read(self, client, app):
        user_token = get_auth_token(client, "notif-read@example.com", "password123", role="buyer")
        with app.app_context():
            profile = Profile.query.filter_by(user_id="notif-read@example.com").first()
            notif = create_notification(profile.id, "promotion", "Sale", "50% off everything")
            notif_id = notif.id

        response = client.patch(
            f"/api/v1/notifications/{notif_id}/read",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["read"] is True
        assert data["id"] == notif_id

    def test_mark_notification_read_not_found(self, client):
        user_token = get_auth_token(
            client, "notif-read404@example.com", "password123", role="buyer"
        )

        response = client.patch(
            "/api/v1/notifications/nonexistent-id/read",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400

    def test_mark_notification_read_wrong_user(self, client, app):
        user_token = get_auth_token(client, "notif-wrong@example.com", "password123", role="buyer")
        other_token = get_auth_token(client, "notif-other@example.com", "password123", role="buyer")
        with app.app_context():
            other_profile = Profile.query.filter_by(user_id="notif-other@example.com").first()
            notif = create_notification(other_profile.id, "order", "Test", "Test body")
            notif_id = notif.id

        response = client.patch(
            f"/api/v1/notifications/{notif_id}/read",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400

    def test_mark_all_read(self, client, app):
        user_token = get_auth_token(
            client, "notif-allread@example.com", "password123", role="buyer"
        )
        with app.app_context():
            profile = Profile.query.filter_by(user_id="notif-allread@example.com").first()
            create_notification(profile.id, "system", "N1", "B1")
            create_notification(profile.id, "system", "N2", "B2")

        response = client.post(
            "/api/v1/notifications/mark-all-read",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "All notifications marked as read"

        list_resp = client.get(
            "/api/v1/notifications", headers={"Authorization": f"Bearer {user_token}"}
        )
        assert list_resp.status_code == 200
        data = list_resp.get_json()
        for item in data["items"]:
            assert item["read"] is True
