import random
import uuid
from datetime import datetime, timedelta

import bcrypt

from server.app import create_app
from server.extensions import db
from server.models import (
    Category,
    Dispute,
    Listing,
    ListingImage,
    Order,
    OrderItem,
    Profile,
    Review,
    Shop,
    Wallet,
    WalletTransaction,
)


def unsplash(photo_id, w=800, h=None, q=75):
    dims = f"w={w}"
    if h:
        dims += f"&h={h}"
    return f"https://images.unsplash.com/photo-{photo_id}?{dims}&q={q}&auto=format&fit=crop"


# Verified (HTTP 200, visually checked) real, category-relevant Unsplash photos.
# Fallback pool per category — used only for shop logo/cover, never for listings
# (listings are matched explicitly by title in LISTING_IMAGE_BY_TITLE below, since
# cycling a shared pool by list index silently drifted out of sync with titles).
CATEGORY_IMAGES = {
    "Electronics": ["1546868871-7041f2a55e12", "1498049794561-7780e7231661", "1526170375885-4d8ecf77b99f", "1583394838336-acd977736f90", "1517336714731-489689fd1ca8"],
    "Fashion": ["1441986300917-64674bd600d8", "1445205170230-053b83016050", "1490481651871-ab68de25d43d", "1483985988355-763728e1935b", "1523381210434-271e8be1f52b", "1543163521-1bf539c55dd2"],
    "Home": ["1555041469-a586c61ea9bc", "1524758631624-e2822e304c36", "1493809842364-78817add7ffb", "1586023492125-27b2c045efd7", "1560448204-e02f11c3d0e2", "1567538096630-e0c55bd6374c"],
    "Groceries": ["1542838132-92c53300491e", "1610348725531-843dff563e2c", "1506617420156-8e4536971650", "1573246123716-6b1782bfc499", "1509440159596-0249088772ff"],
    "Beauty": ["1522335789203-aabd1fc54bc9", "1596462502278-27bfdc403348", "1571781926291-c477ebfd024b", "1512496015851-a90fb38ba796", "1580870069867-74c57ee1bb07", "1620916566398-39f1143ab7be"],
    "Vehicles": ["1502877338535-766e1452684a", "1503376780353-7e6692767b70", "1552519507-da3b142c6e3d", "1449965408869-eaa3f722e40d", "1571068316344-75bc76f77890"],
    "Services": ["1621905251189-08b45d6a269e", "1504328345606-18bbc8c9d7d1", "1581091226825-a6a2a5aee158", "1426927308491-6380b6a9936f"],
    "Kids": ["1522771930-78848d9293e8", "1560785496-3c9d27877182", "1503919545889-aef636e10ad4", "1519689680058-324335c77eba", "1476234251651-f353703a034d"],
}

# Each listing title mapped to a specific, verified, visually-confirmed photo —
# not just "the right category" but the right product. Every title in
# LISTING_TITLES must have an entry here.
LISTING_IMAGE_BY_TITLE = {
    # Electronics
    "Wireless Noise-Cancelling Headphones": "1583394838336-acd977736f90",
    "Smart Fitness Watch": "1546868871-7041f2a55e12",
    "Bluetooth Speaker": "1608043152269-423dbba4e7e1",
    "USB-C Fast Charger": "1498049794561-7780e7231661",
    "4K Action Camera": "1526170375885-4d8ecf77b99f",
    # Fashion
    "Handwoven Cotton Kitenge Dress": "1441986300917-64674bd600d8",
    "Men's Slim Fit Chinos": "1445205170230-053b83016050",
    "Leather Ankle Boots": "1490481651871-ab68de25d43d",
    "Wool Blend Overcoat": "1483985988355-763728e1935b",
    "Statement Silk Scarf": "1523381210434-271e8be1f52b",
    "Denim Jacket": "1543163521-1bf539c55dd2",
    # Home
    "Velvet Accent Armchair": "1555041469-a586c61ea9bc",
    "Ceramic Table Lamp": "1524758631624-e2822e304c36",
    "Handwoven Storage Basket": "1493809842364-78817add7ffb",
    "Oak Coffee Table": "1586023492125-27b2c045efd7",
    "Linen Throw Pillow Set": "1560448204-e02f11c3d0e2",
    "Wall Art Print Set": "1567538096630-e0c55bd6374c",
    # Groceries
    "Fresh Produce Basket (Weekly)": "1542838132-92c53300491e",
    "Organic Vegetable Bundle": "1610348725531-843dff563e2c",
    "Farm-Fresh Fruit Box": "1573246123716-6b1782bfc499",
    "Dairy Essentials Pack": "1506617420156-8e4536971650",
    "Whole Grain Bread Loaf": "1509440159596-0249088772ff",
    # Beauty
    "Everyday Makeup Brush Set": "1596462502278-27bfdc403348",
    "Vitamin C Serum": "1580870069867-74c57ee1bb07",
    "Rose Gold Eyeshadow Palette": "1503236823255-94609f598e71",
    "Hydrating Body Lotion": "1620916566398-39f1143ab7be",
    "Skincare Starter Kit": "1571781926291-c477ebfd024b",
    "Matte Lipstick Trio": "1571875257727-256c39da42af",
    # Vehicles
    "Alloy Wheel Rim Set": "1503376780353-7e6692767b70",
    "Car Phone Mount": "1502877338535-766e1452684a",
    "Leather Steering Wheel Cover": "1552519507-da3b142c6e3d",
    "Dash Cam with Night Vision": "1449965408869-eaa3f722e40d",
    "Commuter Bicycle": "1571068316344-75bc76f77890",
    # Services
    "Home Electrical Wiring Repair": "1621905251189-08b45d6a269e",
    "Appliance Installation Service": "1504328345606-18bbc8c9d7d1",
    "Plumbing Call-Out Visit": "1581091226825-a6a2a5aee158",
    "Furniture Assembly Service": "1426927308491-6380b6a9936f",
    # Kids
    "Fleece Baby Onesie": "1522771930-78848d9293e8",
    "Wooden Building Blocks Set": "1560785496-3c9d27877182",
    "Toddler Rain Jacket": "1503919545889-aef636e10ad4",
    "Kids' Storybook Bundle": "1519689680058-324335c77eba",
    "Inflatable Pool Float": "1476234251651-f353703a034d",
}

AVATAR_IDS = [
    "1633332755192-727a05c4013d", "1494790108377-be9c29b29330", "1507003211169-0a1dd7228f2d",
    "1500648767791-00dcc994a43e", "1531123897727-8f129e1688ce", "1544005313-94ddf0286df2",
    "1500917293891-ef795e70e1f6", "1489980557514-251d61e3eeb6", "1573497019940-1c28c88b4f3e",
    "1517841905240-472988babdf9",
]

CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "icon": "Smartphone"},
    {"name": "Fashion", "slug": "fashion", "icon": "Shirt"},
    {"name": "Home", "slug": "home", "icon": "Sofa"},
    {"name": "Groceries", "slug": "groceries", "icon": "Apple"},
    {"name": "Beauty", "slug": "beauty", "icon": "Sparkles"},
    {"name": "Vehicles", "slug": "vehicles", "icon": "Car"},
    {"name": "Services", "slug": "services", "icon": "Wrench"},
    {"name": "Kids", "slug": "kids", "icon": "Baby"},
]

SHOPS = [
    {"category": "Electronics", "name": "Mama Njeri Electronics", "owner": "Grace Njeri", "address": "Biashara St, Nairobi CBD", "lat": -1.2841, "lng": 36.8233, "status": "active"},
    {"category": "Fashion", "name": "Threadline Fashion House", "owner": "Wanjiru Kamau", "address": "Westgate Mall, Westlands", "lat": -1.2578, "lng": 36.8027, "status": "active"},
    {"category": "Home", "name": "Kilimani Home & Living", "owner": "Peter Ochieng", "address": "Yaya Centre, Kilimani", "lat": -1.2921, "lng": 36.7872, "status": "active"},
    {"category": "Groceries", "name": "Kilimani Fresh Grocers", "owner": "Faith Wambui", "address": "Argwings Kodhek Rd, Kilimani", "lat": -1.2933, "lng": 36.7856, "status": "active"},
    {"category": "Beauty", "name": "Glow Beauty Bar", "owner": "Amina Hassan", "address": "Sarit Centre, Westlands", "lat": -1.2611, "lng": 36.8039, "status": "active"},
    {"category": "Vehicles", "name": "Ngong Road Auto Parts", "owner": "David Kiprotich", "address": "Ngong Road, Nairobi", "lat": -1.3012, "lng": 36.7789, "status": "pending"},
    {"category": "Services", "name": "FixIt Nairobi Services", "owner": "Samuel Mutiso", "address": "Industrial Area, Nairobi", "lat": -1.3103, "lng": 36.8511, "status": "active"},
    {"category": "Kids", "name": "Little Ones Kids Store", "owner": "Esther Achieng", "address": "Lavington Mall, Lavington", "lat": -1.2789, "lng": 36.7683, "status": "pending"},
]

LISTING_TITLES = {
    "Electronics": ["Wireless Noise-Cancelling Headphones", "Smart Fitness Watch", "Bluetooth Speaker", "USB-C Fast Charger", "4K Action Camera"],
    "Fashion": ["Handwoven Cotton Kitenge Dress", "Men's Slim Fit Chinos", "Leather Ankle Boots", "Wool Blend Overcoat", "Statement Silk Scarf", "Denim Jacket"],
    "Home": ["Velvet Accent Armchair", "Ceramic Table Lamp", "Handwoven Storage Basket", "Oak Coffee Table", "Linen Throw Pillow Set", "Wall Art Print Set"],
    "Groceries": ["Fresh Produce Basket (Weekly)", "Organic Vegetable Bundle", "Farm-Fresh Fruit Box", "Dairy Essentials Pack", "Whole Grain Bread Loaf"],
    "Beauty": ["Everyday Makeup Brush Set", "Vitamin C Serum", "Rose Gold Eyeshadow Palette", "Hydrating Body Lotion", "Skincare Starter Kit", "Matte Lipstick Trio"],
    "Vehicles": ["Alloy Wheel Rim Set", "Car Phone Mount", "Leather Steering Wheel Cover", "Dash Cam with Night Vision", "Commuter Bicycle"],
    "Services": ["Home Electrical Wiring Repair", "Appliance Installation Service", "Plumbing Call-Out Visit", "Furniture Assembly Service"],
    "Kids": ["Fleece Baby Onesie", "Wooden Building Blocks Set", "Toddler Rain Jacket", "Kids' Storybook Bundle", "Inflatable Pool Float"],
}

NAIROBI_BUYERS = [
    "Brian Otieno", "Faith Wanjiru", "Kevin Kamau", "Mercy Adhiambo", "John Mwangi", "Lucy Njeri",
]

ORDER_STATUSES = ["pending", "confirmed", "paid", "preparing", "out_for_delivery", "delivered", "delivered", "delivered"]
PAYMENT_METHODS = ["cash", "stripe", "flutterwave", "paystack"]


def make_profile(email, role, full_name, phone, avatar_id, password):
    return Profile(
        id=str(uuid.uuid4()),
        user_id=email,
        role=role,
        full_name=full_name,
        phone=phone,
        avatar_url=unsplash(avatar_id, w=200, h=200, q=70),
        password_hash=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
    )


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        rng = random.Random(42)

        admin = Profile(
            id=str(uuid.uuid4()), user_id="admin@soko.local", role="admin", full_name="Admin User",
            phone="+254700000000", avatar_url=unsplash(AVATAR_IDS[0], w=200, h=200, q=70),
            password_hash=bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8"),
        )
        db.session.add(admin)

        buyer_main = make_profile("buyer@example.com", "buyer", "Buyer User", "+254711111111", AVATAR_IDS[1], "buyer123")
        retailer_main = make_profile("retailer@example.com", "retailer", "Retailer User", "+254722222222", AVATAR_IDS[2], "retailer123")
        db.session.add(buyer_main)
        db.session.add(retailer_main)

        rider = make_profile("rider@example.com", "rider", "Peter Mutua", "+254733333333", AVATAR_IDS[3], "rider123")
        db.session.add(rider)

        buyers = [buyer_main]
        for i, name in enumerate(NAIROBI_BUYERS):
            email = f"{name.split()[0].lower()}.{name.split()[1].lower()}@example.com"
            buyer = make_profile(email, "buyer", name, f"+2547{10000000 + i * 111111}", AVATAR_IDS[(i + 4) % len(AVATAR_IDS)], "password123")
            db.session.add(buyer)
            buyers.append(buyer)
        db.session.flush()

        # Categories
        category_rows = {}
        for cat in CATEGORIES:
            row = Category(id=str(uuid.uuid4()), name=cat["name"], slug=cat["slug"], icon=cat["icon"])
            db.session.add(row)
            category_rows[cat["name"]] = row
        db.session.flush()

        # Shops + retailers (first shop uses the convenience retailer@example.com account)
        shops = []
        for index, spec in enumerate(SHOPS):
            if index == 0:
                owner = retailer_main
            else:
                email = f"{spec['owner'].split()[0].lower()}.{spec['owner'].split()[1].lower()}@example.com"
                owner = make_profile(email, "retailer", spec["owner"], f"+2547{20000000 + index * 111111}", AVATAR_IDS[index % len(AVATAR_IDS)], "password123")
                db.session.add(owner)
                db.session.flush()

            images = CATEGORY_IMAGES[spec["category"]]
            shop = Shop(
                id=str(uuid.uuid4()), owner_id=owner.id, name=spec["name"],
                description=f"{spec['name']} — trusted {spec['category'].lower()} retailer serving Nairobi.",
                logo_url=unsplash(images[0], w=200, h=200, q=70),
                cover_url=unsplash(images[1 % len(images)], w=900, h=340, q=75),
                category=spec["category"], address=spec["address"], lat=spec["lat"], lng=spec["lng"],
                status=spec["status"], rating_avg=round(rng.uniform(4.2, 5.0), 1), rating_count=rng.randint(20, 320),
            )
            db.session.add(shop)
            shops.append(shop)

            wallet = Wallet(id=str(uuid.uuid4()), owner_id=owner.id, balance=rng.randint(5000, 60000), currency="KES")
            db.session.add(wallet)
            db.session.flush()
            db.session.add(WalletTransaction(wallet_id=wallet.id, type="credit", amount=rng.randint(2000, 15000), ref="order-payout", status="completed"))
            if index % 3 == 0:
                db.session.add(WalletTransaction(wallet_id=wallet.id, type="payout", amount=rng.randint(1000, 8000), ref="payout-request", status="pending"))

        db.session.flush()

        # Listings — each title gets its own specifically-matched photo via
        # LISTING_IMAGE_BY_TITLE (not a cycled category pool), so the image always
        # matches what the listing actually is, not just its broad category.
        listings = []
        for shop, spec in zip(shops, SHOPS):
            titles = LISTING_TITLES[spec["category"]]
            for title in titles:
                listing = Listing(
                    id=str(uuid.uuid4()), shop_id=shop.id, title=title,
                    description=f"{title} from {shop.name}. Genuine quality, ships from {shop.address}.",
                    price=rng.randint(500, 45000), category_id=category_rows[spec["category"]].id,
                    condition="new" if rng.random() > 0.15 else "used", stock=rng.randint(0, 40),
                    status="active", lat=shop.lat, lng=shop.lng,
                )
                db.session.add(listing)
                db.session.flush()
                photo_id = LISTING_IMAGE_BY_TITLE[title]
                db.session.add(ListingImage(id=str(uuid.uuid4()), listing_id=listing.id, url=unsplash(photo_id), position=0))
                listings.append((listing, shop))

        db.session.flush()

        # Orders + reviews
        disputes_created = 0
        for i in range(18):
            buyer = rng.choice(buyers)
            listing, shop = rng.choice(listings)
            status = ORDER_STATUSES[i % len(ORDER_STATUSES)]
            qty = rng.randint(1, 2)
            order = Order(
                id=str(uuid.uuid4()), buyer_id=buyer.id, shop_id=shop.id, status=status,
                total=listing.price * qty, payment_method=rng.choice(PAYMENT_METHODS),
                payment_status="paid" if status not in ("pending",) else "pending",
                delivery_method="delivery" if rng.random() > 0.3 else "pickup",
                delivery_address="Kilimani, Nairobi", delivery_lat=-1.2921, delivery_lng=36.7872,
                created_at=datetime.utcnow() - timedelta(days=rng.randint(0, 21)),
            )
            db.session.add(order)
            db.session.flush()
            db.session.add(OrderItem(order_id=order.id, listing_id=listing.id, title_snapshot=listing.title, price_snapshot=listing.price, qty=qty))

            if status == "delivered" and rng.random() > 0.4:
                db.session.add(Review(order_id=order.id, shop_id=shop.id, buyer_id=buyer.id, rating=rng.randint(4, 5), comment=rng.choice([
                    "Fast delivery and exactly as described.",
                    "Great quality, will order again.",
                    "Good service, minor delay but worth it.",
                    "Excellent packaging and communication.",
                ])))

            if disputes_created < 3 and status in ("delivered", "out_for_delivery") and rng.random() > 0.7:
                db.session.add(Dispute(
                    id=str(uuid.uuid4()), order_id=order.id, raised_by=buyer.id,
                    reason=rng.choice([
                        "Item arrived damaged in transit.",
                        "Received the wrong item from my order.",
                        "Order is significantly delayed with no updates.",
                    ]),
                    status="open",
                ))
                disputes_created += 1

        db.session.commit()

        print("Seed data created successfully")
        print(f"  {len(buyers)} buyers, {len(SHOPS)} shops/retailers, 1 rider, 1 admin")
        print(f"  {len(listings)} listings across {len(CATEGORIES)} categories, 18 orders, {disputes_created} disputes")
        print("Admin:    admin@soko.local / admin123")
        print("Buyer:    buyer@example.com / buyer123")
        print("Retailer: retailer@example.com / retailer123")
        print("Rider:    rider@example.com / rider123")
        print("(all other seeded accounts use password: password123)")


if __name__ == "__main__":
    seed()
