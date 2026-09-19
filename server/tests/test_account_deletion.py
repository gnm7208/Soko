"""In-app account deletion: password re-check, in-flight guards, and what survives."""

from server.tests.test_orders import get_auth_token  # noqa: F401  (fixtures below reuse it)


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(client, email, role="buyer", password="password123"):
    return get_auth_token(client, email, password, role=role)


def _shop_with_listing(client, retailer_token):
    shop = client.post(
        "/api/v1/shops",
        headers=_auth(retailer_token),
        json={"name": "Deleting Shop", "category": "electronics"},
    ).get_json()
    listing = client.post(
        "/api/v1/listings", headers=_auth(retailer_token), json={"title": "Kettle", "price": 1500}
    ).get_json()
    return shop["id"], listing["id"]


def _order(client, buyer_token, shop_id, listing_id):
    resp = client.post(
        "/api/v1/orders",
        headers=_auth(buyer_token),
        json={
            "shop_id": shop_id,
            "items": [{"listing_id": listing_id, "qty": 1}],
            "delivery_method": "pickup",
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def test_wrong_password_is_403_and_keeps_the_session(client):
    token = _register_and_login(client, "del1@test.com")
    resp = client.delete("/api/v1/auth/me", headers=_auth(token), json={"password": "nope"})
    assert resp.status_code == 403, "must not be 401 — the client treats that as an expired session"
    assert client.get("/api/v1/auth/me", headers=_auth(token)).status_code == 200


def test_refused_while_an_order_is_in_progress(client):
    retailer = _register_and_login(client, "del2r@test.com", role="retailer")
    buyer = _register_and_login(client, "del2b@test.com")
    shop_id, listing_id = _shop_with_listing(client, retailer)
    _order(client, buyer, shop_id, listing_id)  # pending

    for token in (buyer, retailer):
        resp = client.delete(
            "/api/v1/auth/me", headers=_auth(token), json={"password": "password123"}
        )
        assert resp.status_code == 409
        assert "in progress" in resp.get_json()["error"]


def test_buyer_deletion_erases_them_but_keeps_the_shop(client):
    from server.extensions import db
    from server.models import Order, Profile, Shop

    retailer = _register_and_login(client, "del3r@test.com", role="retailer")
    buyer = _register_and_login(client, "del3b@test.com")
    shop_id, listing_id = _shop_with_listing(client, retailer)
    order_id = _order(client, buyer, shop_id, listing_id)

    # Cancel the order so nothing is in flight.
    resp = client.post(f"/api/v1/orders/{order_id}/cancel", headers=_auth(buyer))
    assert resp.status_code in (200, 201), resp.get_json()

    resp = client.delete("/api/v1/auth/me", headers=_auth(buyer), json={"password": "password123"})
    assert resp.status_code == 200, resp.get_json()

    with client.application.app_context():
        assert db.session.query(Profile).filter_by(user_id="del3b@test.com").first() is None
        assert db.session.get(Order, order_id) is None
        assert db.session.get(Shop, shop_id) is not None
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "del3b@test.com", "password": "password123"}
        ).status_code
        == 401
    )


def test_retailer_deletion_takes_the_shop_and_its_listings(client):
    from server.extensions import db
    from server.models import Listing, Shop

    retailer = _register_and_login(client, "del4r@test.com", role="retailer")
    shop_id, listing_id = _shop_with_listing(client, retailer)

    resp = client.delete(
        "/api/v1/auth/me", headers=_auth(retailer), json={"password": "password123"}
    )
    assert resp.status_code == 200

    with client.application.app_context():
        assert db.session.get(Shop, shop_id) is None
        assert db.session.get(Listing, listing_id) is None
