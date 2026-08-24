import uuid

from server.extensions import db
from server.models import Category, Listing, Profile


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


def create_listing(client, token, shop_id, title="Test Product", price=1000, category_id=None):
    payload = {
        "title": title,
        "price": price,
        "stock": 10,
        "condition": "new",
    }
    if category_id:
        payload["category_id"] = category_id
    response = client.post(
        "/api/v1/listings", headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    assert response.status_code == 201
    return response.get_json()["id"]


class TestSearch:
    def test_search_by_keyword(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop")
        create_listing(client, retailer_token, shop_id, title="Wireless Headphones", price=2500)
        create_listing(client, retailer_token, shop_id, title="Bluetooth Speaker", price=1500)
        create_listing(client, retailer_token, shop_id, title="USB Cable", price=500)

        response = client.get("/api/v1/search?q=wireless")
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Wireless Headphones"

    def test_search_by_keyword_multiple_matches(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer2@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 2")
        create_listing(client, retailer_token, shop_id, title="Red T-Shirt", price=800)
        create_listing(client, retailer_token, shop_id, title="Blue T-Shirt", price=800)
        create_listing(client, retailer_token, shop_id, title="Red Hat", price=400)

        response = client.get("/api/v1/search?q=red")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 2
        titles = [item["title"] for item in data["items"]]
        assert "Red T-Shirt" in titles
        assert "Red Hat" in titles

    def test_search_no_results(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer3@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 3")
        create_listing(client, retailer_token, shop_id, title="Laptop", price=50000)

        response = client.get("/api/v1/search?q=nonexistent-keyword-xyz")
        assert response.status_code == 200
        data = response.get_json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_search_empty_query(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer4@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 4")
        create_listing(client, retailer_token, shop_id, title="Product A", price=1000)
        create_listing(client, retailer_token, shop_id, title="Product B", price=2000)

        response = client.get("/api/v1/search")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 2

    def test_filter_by_category(self, client, app):
        admin_token = get_admin_token(app)
        with app.app_context():
            cat1 = Category(name="Electronics", slug="electronics")
            cat2 = Category(name="Clothing", slug="clothing")
            db.session.add_all([cat1, cat2])
            db.session.commit()
            cat1_id = cat1.id
            cat2_id = cat2.id

        retailer_token = get_auth_token(
            client, "search-retailer5@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 5")
        create_listing(
            client, retailer_token, shop_id, title="Phone", price=30000, category_id=cat1_id
        )
        create_listing(
            client, retailer_token, shop_id, title="Shirt", price=1500, category_id=cat2_id
        )
        create_listing(
            client, retailer_token, shop_id, title="Laptop", price=80000, category_id=cat1_id
        )

        response = client.get(f"/api/v1/search?category_id={cat1_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 2
        titles = [item["title"] for item in data["items"]]
        assert "Phone" in titles
        assert "Laptop" in titles
        assert "Shirt" not in titles

    def test_filter_by_price(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer6@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 6")
        create_listing(client, retailer_token, shop_id, title="Cheap Item", price=500)
        create_listing(client, retailer_token, shop_id, title="Mid Item", price=1500)
        create_listing(client, retailer_token, shop_id, title="Expensive Item", price=5000)

        response = client.get("/api/v1/search?min_price=1000&max_price=3000")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Mid Item"

    def test_filter_by_price_only_min(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer7@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 7")
        create_listing(client, retailer_token, shop_id, title="Cheap", price=500)
        create_listing(client, retailer_token, shop_id, title="Expensive", price=5000)

        response = client.get("/api/v1/search?min_price=1000")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Expensive"

    def test_filter_by_price_only_max(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer8@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 8")
        create_listing(client, retailer_token, shop_id, title="Cheap", price=500)
        create_listing(client, retailer_token, shop_id, title="Expensive", price=5000)

        response = client.get("/api/v1/search?max_price=1000")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Cheap"

    def test_search_combined_filters(self, client, app):
        admin_token = get_admin_token(app, email="admin-search@example.com")
        with app.app_context():
            cat = Category(name="Electronics", slug="electronics2")
            db.session.add(cat)
            db.session.commit()
            cat_id = cat.id

        retailer_token = get_auth_token(
            client, "search-retailer9@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 9")
        create_listing(
            client,
            retailer_token,
            shop_id,
            title="Wireless Earbuds",
            price=2000,
            category_id=cat_id,
        )
        create_listing(
            client, retailer_token, shop_id, title="Wired Earbuds", price=500, category_id=cat_id
        )
        create_listing(client, retailer_token, shop_id, title="Red Shirt", price=1500)

        response = client.get(f"/api/v1/search?q=earbuds&category_id={cat_id}&min_price=1000")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Wireless Earbuds"

    def test_search_pagination(self, client):
        retailer_token = get_auth_token(
            client, "search-retailer10@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 10")
        for i in range(5):
            create_listing(
                client, retailer_token, shop_id, title=f"Product {i}", price=1000 + i * 100
            )

        response = client.get("/api/v1/search?page=1&per_page=2")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3

    def test_search_excludes_inactive_listings(self, client, app):
        retailer_token = get_auth_token(
            client, "search-retailer11@example.com", "password123", role="retailer"
        )
        shop_id = create_shop(client, retailer_token, name="Search Shop 11")
        active_id = create_listing(
            client, retailer_token, shop_id, title="Active Product", price=1000
        )
        inactive_id = create_listing(
            client, retailer_token, shop_id, title="Inactive Product", price=2000
        )

        with app.app_context():
            listing = Listing.query.get(inactive_id)
            listing.status = "sold"
            db.session.commit()

        response = client.get("/api/v1/search")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Active Product"
