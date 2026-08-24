import uuid
from datetime import datetime

from server.extensions import db
from server.models import (
    Conversation,
    Message,
    Profile,
)


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


def get_admin_token(app, email="admin@example.com"):
    from flask_jwt_extended import create_access_token

    with app.app_context():
        profile_id = str(uuid.uuid4())
        admin = Profile(
            id=profile_id,
            user_id=email,
            role="admin",
            full_name="Admin User",
            password_hash="hashed",
        )
        db.session.add(admin)
        db.session.commit()
        token = create_access_token(
            identity=email,
            additional_claims={"role": "admin", "profile_id": profile_id},
        )
    return token


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


def _create_conversation_direct(app, buyer_id, shop_id, listing_id=None):
    with app.app_context():
        conv = Conversation(
            buyer_id=buyer_id,
            shop_id=shop_id,
            listing_id=listing_id,
            last_message_at=datetime.utcnow(),
        )
        db.session.add(conv)
        db.session.flush()
        message = Message(
            conversation_id=conv.id,
            sender_id=buyer_id,
            body="Hello",
        )
        db.session.add(message)
        conv.last_message_at = message.created_at or datetime.utcnow()
        db.session.commit()
        return conv.id


class TestChat:
    def test_start_conversation(self, client, app):
        buyer_token = get_auth_token(client, "chat-buyer@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "chat-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop")

        response = client.post(
            "/api/v1/conversations",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "shop_id": shop_id,
                "body": "Hello, is this item available?",
            },
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "id" in data
        assert data["shop_id"] == shop_id
        assert data["buyer_id"] is not None

    def test_start_conversation_with_listing(self, client, app):
        buyer_token = get_auth_token(client, "chat-buyer2@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "chat-retailer2@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop 2")
        listing_id = create_listing(client, retailer_token, shop_id, title="Widget")

        response = client.post(
            "/api/v1/conversations",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "shop_id": shop_id,
                "listing_id": listing_id,
                "body": "I'm interested in the Widget",
            },
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["listing_id"] == listing_id

    def test_start_conversation_missing_shop_id(self, client):
        buyer_token = get_auth_token(client, "chat-buyer3@example.com", "password123", role="buyer")

        response = client.post(
            "/api/v1/conversations",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "body": "Hello",
            },
        )
        assert response.status_code == 400

    def test_start_conversation_missing_body(self, client):
        buyer_token = get_auth_token(client, "chat-buyer4@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "chat-retailer4@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop 4")

        response = client.post(
            "/api/v1/conversations",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "shop_id": shop_id,
            },
        )
        assert response.status_code == 400

    def test_start_conversation_invalid_shop(self, client):
        buyer_token = get_auth_token(client, "chat-buyer5@example.com", "password123", role="buyer")

        response = client.post(
            "/api/v1/conversations",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={
                "shop_id": "nonexistent-shop-id",
                "body": "Hello",
            },
        )
        assert response.status_code == 400

    def test_send_message(self, client, app):
        buyer_token = get_auth_token(client, "chat-buyer6@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "chat-retailer6@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop 6")

        with app.app_context():
            buyer_profile = Profile.query.filter_by(user_id="chat-buyer6@example.com").first()
            conv_id = _create_conversation_direct(app, buyer_profile.id, shop_id)

        response = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={"body": "Yes, it is available"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["body"] == "Yes, it is available"
        assert data["conversation_id"] == conv_id
        assert data["sender_id"] is not None

    def test_send_message_missing_body(self, client, app):
        buyer_token = get_auth_token(client, "chat-buyer7@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "chat-retailer7@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop 7")

        with app.app_context():
            buyer_profile = Profile.query.filter_by(user_id="chat-buyer7@example.com").first()
            conv_id = _create_conversation_direct(app, buyer_profile.id, shop_id)

        response = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {retailer_token}"},
            json={},
        )
        assert response.status_code == 400

    def test_send_message_invalid_conversation(self, client):
        buyer_token = get_auth_token(client, "chat-buyer8@example.com", "password123", role="buyer")

        response = client.post(
            "/api/v1/conversations/invalid-conv-id/messages",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={"body": "Hello"},
        )
        assert response.status_code == 400

    def test_get_conversation(self, client, app):
        buyer_token = get_auth_token(client, "chat-buyer9@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "chat-retailer9@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop 9")

        with app.app_context():
            buyer_profile = Profile.query.filter_by(user_id="chat-buyer9@example.com").first()
            conv_id = _create_conversation_direct(app, buyer_profile.id, shop_id)

        response = client.get(
            f"/api/v1/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "messages" in data
        assert len(data["messages"]) == 1
        assert data["messages"][0]["body"] == "Hello"

    def test_get_conversation_not_participant(self, client, app):
        buyer_token = get_auth_token(
            client, "chat-buyer10@example.com", "password123", role="buyer"
        )
        other_token = get_auth_token(client, "chat-other@example.com", "password123", role="buyer")
        retailer_token = get_auth_token(
            client, "chat-retailer10@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop 10")

        with app.app_context():
            buyer_profile = Profile.query.filter_by(user_id="chat-buyer10@example.com").first()
            conv_id = _create_conversation_direct(app, buyer_profile.id, shop_id)

        response = client.get(
            f"/api/v1/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 400

    def test_list_conversations(self, client, app):
        buyer_token = get_auth_token(
            client, "chat-buyer11@example.com", "password123", role="buyer"
        )
        retailer_token = get_auth_token(
            client, "chat-retailer11@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Chat Shop 11")

        with app.app_context():
            buyer_profile = Profile.query.filter_by(user_id="chat-buyer11@example.com").first()
            _create_conversation_direct(app, buyer_profile.id, shop_id)

        response = client.get(
            "/api/v1/conversations", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["shop_id"] == shop_id
