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
# not just "the right category" but the right product. Every title used in a
# SHOPS entry's "titles" list below must have an entry here.
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
    # Second shop per category — new titles, each individually verified
    # (HTTP 200 + visual check) the same way as the set above.
    "Wireless Earbuds": "1590658268037-6bf12165a8df",
    "Compact USB Keyboard": "1541140532154-b024d705b90a",
    "Smart Speaker": "1543512214-318c7553f230",
    "Vintage Baseball Cap": "1521369909029-2afed882baee",
    "Floral Print Leather Handbag": "1591561954557-26941169b49e",
    "Classic White Sneakers": "1600185365483-26d7a4cc7519",
    "Woven Area Rug": "1600166898405-da9535204843",
    "Round Wall Mirror": "1618220179428-22790b461013",
    "Roasted Coffee Beans (1kg)": "1447933601403-0c6688de566e",
    "Spice Rack Bundle": "1596040033229-a9821ebd058d",
    "Extra Virgin Olive Oil": "1474979266404-7eaacbcd87c5",
    "Perfume Gift Set": "1541643600914-78b084683601",
    "Organic Body Oil": "1595515106969-1ce29566ff1c",
    "House Cleaning Service": "1581578731548-c64695cc6952",
    "Garden Landscaping Visit": "1523348837708-15d4a09cfac2",
    "Remote IT Support Visit": "1517430816045-df4b7de11d1d",
    "Kids' Backpack": "1553062407-98eeb64c6a62",
    "Alphabet Learning Blocks": "1587654780291-39c9404d746b",
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

# Two shops per category. Each shop lists its own titles directly (rather than
# one shared list per category) so two shops in the same category never end up
# with identical listings — the second shop mixes a few titles unique to it
# with some carried over from the first, like real marketplaces where several
# sellers carry the same generic product.
SHOPS = [
    {"category": "Electronics", "name": "Mama Njeri Electronics", "owner": "Grace Njeri", "address": "Biashara St, Nairobi CBD", "lat": -1.2841, "lng": 36.8233, "status": "active",
     "titles": ["Wireless Noise-Cancelling Headphones", "Smart Fitness Watch", "Bluetooth Speaker", "USB-C Fast Charger", "4K Action Camera"]},
    {"category": "Electronics", "name": "TechBazaar Nairobi", "owner": "Daniel Kariuki", "address": "Moi Avenue, Nairobi CBD", "lat": -1.2864, "lng": 36.8172, "status": "active",
     "titles": ["Wireless Earbuds", "Compact USB Keyboard", "Smart Speaker", "USB-C Fast Charger", "Bluetooth Speaker"]},
    {"category": "Fashion", "name": "Threadline Fashion House", "owner": "Wanjiru Kamau", "address": "Westgate Mall, Westlands", "lat": -1.2578, "lng": 36.8027, "status": "active",
     "titles": ["Handwoven Cotton Kitenge Dress", "Men's Slim Fit Chinos", "Leather Ankle Boots", "Wool Blend Overcoat", "Statement Silk Scarf", "Denim Jacket"]},
    {"category": "Fashion", "name": "Eastleigh Style Boutique", "owner": "Halima Abdi", "address": "Eastleigh, Nairobi", "lat": -1.2762, "lng": 36.8422, "status": "active",
     "titles": ["Vintage Baseball Cap", "Floral Print Leather Handbag", "Classic White Sneakers", "Denim Jacket", "Leather Ankle Boots"]},
    {"category": "Home", "name": "Kilimani Home & Living", "owner": "Peter Ochieng", "address": "Yaya Centre, Kilimani", "lat": -1.2921, "lng": 36.7872, "status": "active",
     "titles": ["Velvet Accent Armchair", "Ceramic Table Lamp", "Handwoven Storage Basket", "Oak Coffee Table", "Linen Throw Pillow Set", "Wall Art Print Set"]},
    {"category": "Home", "name": "Karen Home Interiors", "owner": "Susan Wairimu", "address": "Karen Shopping Centre, Karen", "lat": -1.3192, "lng": 36.7076, "status": "active",
     "titles": ["Woven Area Rug", "Round Wall Mirror", "Ceramic Table Lamp", "Oak Coffee Table", "Linen Throw Pillow Set"]},
    {"category": "Groceries", "name": "Kilimani Fresh Grocers", "owner": "Faith Wambui", "address": "Argwings Kodhek Rd, Kilimani", "lat": -1.2933, "lng": 36.7856, "status": "active",
     "titles": ["Fresh Produce Basket (Weekly)", "Organic Vegetable Bundle", "Farm-Fresh Fruit Box", "Dairy Essentials Pack", "Whole Grain Bread Loaf"]},
    {"category": "Groceries", "name": "Ngong Road Grocers", "owner": "James Muriuki", "address": "Adams Arcade, Ngong Road", "lat": -1.3009, "lng": 36.7822, "status": "active",
     "titles": ["Roasted Coffee Beans (1kg)", "Spice Rack Bundle", "Extra Virgin Olive Oil", "Organic Vegetable Bundle", "Dairy Essentials Pack"]},
    {"category": "Beauty", "name": "Glow Beauty Bar", "owner": "Amina Hassan", "address": "Sarit Centre, Westlands", "lat": -1.2611, "lng": 36.8039, "status": "active",
     "titles": ["Everyday Makeup Brush Set", "Vitamin C Serum", "Rose Gold Eyeshadow Palette", "Hydrating Body Lotion", "Skincare Starter Kit", "Matte Lipstick Trio"]},
    {"category": "Beauty", "name": "Radiance Beauty Studio", "owner": "Zainab Omar", "address": "The Hub, Karen", "lat": -1.3172, "lng": 36.7101, "status": "pending",
     "titles": ["Perfume Gift Set", "Organic Body Oil", "Everyday Makeup Brush Set", "Skincare Starter Kit"]},
    {"category": "Vehicles", "name": "Ngong Road Auto Parts", "owner": "David Kiprotich", "address": "Ngong Road, Nairobi", "lat": -1.3012, "lng": 36.7789, "status": "pending",
     "titles": ["Alloy Wheel Rim Set", "Car Phone Mount", "Leather Steering Wheel Cover", "Dash Cam with Night Vision", "Commuter Bicycle"]},
    {"category": "Vehicles", "name": "Industrial Area Auto Spares", "owner": "Joseph Kamande", "address": "Enterprise Road, Industrial Area", "lat": -1.3134, "lng": 36.8467, "status": "active",
     "titles": ["Alloy Wheel Rim Set", "Car Phone Mount", "Dash Cam with Night Vision", "Commuter Bicycle"]},
    {"category": "Services", "name": "FixIt Nairobi Services", "owner": "Samuel Mutiso", "address": "Industrial Area, Nairobi", "lat": -1.3103, "lng": 36.8511, "status": "active",
     "titles": ["Home Electrical Wiring Repair", "Appliance Installation Service", "Plumbing Call-Out Visit", "Furniture Assembly Service"]},
    {"category": "Services", "name": "Nairobi Home Helpers", "owner": "Grace Atieno", "address": "Kawangware, Nairobi", "lat": -1.2799, "lng": 36.7517, "status": "active",
     "titles": ["House Cleaning Service", "Garden Landscaping Visit", "Remote IT Support Visit", "Home Electrical Wiring Repair"]},
    {"category": "Kids", "name": "Little Ones Kids Store", "owner": "Esther Achieng", "address": "Lavington Mall, Lavington", "lat": -1.2789, "lng": 36.7683, "status": "pending",
     "titles": ["Fleece Baby Onesie", "Wooden Building Blocks Set", "Toddler Rain Jacket", "Kids' Storybook Bundle", "Inflatable Pool Float"]},
    {"category": "Kids", "name": "TinyTots Nairobi", "owner": "Caroline Njoki", "address": "Village Market, Gigiri", "lat": -1.2306, "lng": 36.8009, "status": "pending",
     "titles": ["Kids' Backpack", "Alphabet Learning Blocks", "Wooden Building Blocks Set", "Fleece Baby Onesie"]},
]

NAIROBI_BUYERS = [
    "Brian Otieno", "Faith Wanjiru", "Kevin Kamau", "Mercy Adhiambo", "John Mwangi", "Lucy Njeri",
    "Peter Kariuki", "Grace Muthoni", "Dennis Omondi", "Sarah Chebet", "Michael Njoroge",
    "Winnie Auma", "Collins Kiplagat", "Ann Wangui",
]

ORDER_STATUSES = ["pending", "confirmed", "paid", "preparing", "out_for_delivery", "delivered", "delivered", "delivered"]
PAYMENT_METHODS = ["cash", "stripe", "flutterwave", "paystack"]
ORDER_COUNT = 45
MAX_DISPUTES = 6


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
        category_shop_counts = {}
        for index, spec in enumerate(SHOPS):
            if index == 0:
                owner = retailer_main
            else:
                email = f"{spec['owner'].split()[0].lower()}.{spec['owner'].split()[1].lower()}@example.com"
                owner = make_profile(email, "retailer", spec["owner"], f"+2547{20000000 + index * 111111}", AVATAR_IDS[index % len(AVATAR_IDS)], "password123")
                db.session.add(owner)
                db.session.flush()

            # Offset into the category's image pool by how many shops of this
            # category came before it, so two shops in the same category never
            # show the identical logo/cover.
            seen = category_shop_counts.get(spec["category"], 0)
            category_shop_counts[spec["category"]] = seen + 1
            images = CATEGORY_IMAGES[spec["category"]]
            shop = Shop(
                id=str(uuid.uuid4()), owner_id=owner.id, name=spec["name"],
                description=f"{spec['name']} — trusted {spec['category'].lower()} retailer serving Nairobi.",
                logo_url=unsplash(images[(seen * 2) % len(images)], w=200, h=200, q=70),
                cover_url=unsplash(images[(seen * 2 + 1) % len(images)], w=900, h=340, q=75),
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
        for shop, spec in zip(shops, SHOPS, strict=True):
            for title in spec["titles"]:
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
        for i in range(ORDER_COUNT):
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

            if disputes_created < MAX_DISPUTES and status in ("delivered", "out_for_delivery") and rng.random() > 0.7:
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
        print(f"  {len(listings)} listings across {len(CATEGORIES)} categories, {ORDER_COUNT} orders, {disputes_created} disputes")
        print("Admin:    admin@soko.local / admin123")
        print("Buyer:    buyer@example.com / buyer123")
        print("Retailer: retailer@example.com / retailer123")
        print("Rider:    rider@example.com / rider123")
        print("(all other seeded accounts use password: password123)")


if __name__ == "__main__":
    seed()
