import uuid

import bcrypt
from flask_jwt_extended import create_access_token

from server.extensions import db
from server.models import Profile, Shop
from server.schemas.auth import (
    LoginSchema,
    ProfileUpdateSchema,
    RegisterSchema,
    UpgradeRetailerSchema,
)
from server.utils.errors import APIError, NotFound


class AuthService:
    @staticmethod
    def register(data):
        schema = RegisterSchema()
        validated = schema.load(data)
        existing = db.session.query(Profile).filter_by(user_id=validated["email"]).first()
        if existing:
            raise APIError("User already exists", status_code=409)

        password_hash = bcrypt.hashpw(
            validated["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        profile = Profile(
            id=str(uuid.uuid4()),
            user_id=validated["email"],
            role=validated.get("role", "buyer"),
            full_name=validated["full_name"],
            phone=validated.get("phone"),
            password_hash=password_hash,
        )
        db.session.add(profile)
        db.session.commit()

        access_token = create_access_token(
            identity=profile.user_id,
            additional_claims={"role": profile.role, "profile_id": profile.id},
        )
        return {
            "access_token": access_token,
            "profile": {"id": profile.id, "role": profile.role, "full_name": profile.full_name},
        }

    @staticmethod
    def login(data):
        schema = LoginSchema()
        validated = schema.load(data)
        profile = db.session.query(Profile).filter_by(user_id=validated["email"]).first()
        if not profile or not bcrypt.checkpw(
            validated["password"].encode("utf-8"), profile.password_hash.encode("utf-8")
        ):
            raise APIError("Invalid credentials", status_code=401)

        access_token = create_access_token(
            identity=profile.user_id,
            additional_claims={"role": profile.role, "profile_id": profile.id},
        )
        return {
            "access_token": access_token,
            "profile": {"id": profile.id, "role": profile.role, "full_name": profile.full_name},
        }

    @staticmethod
    def get_profile(profile_id):
        profile = db.session.query(Profile).filter_by(id=profile_id).first()
        if not profile:
            raise NotFound("Profile not found")
        return profile

    @staticmethod
    def update_profile(profile_id, data):
        schema = ProfileUpdateSchema()
        validated = schema.load(data)
        profile = db.session.query(Profile).filter_by(id=profile_id).first()
        if not profile:
            raise NotFound("Profile not found")
        if "full_name" in validated:
            profile.full_name = validated["full_name"]
        if "phone" in validated:
            profile.phone = validated["phone"]
        db.session.commit()
        return profile

    @staticmethod
    def upgrade_to_retailer(profile_id, data):
        schema = UpgradeRetailerSchema()
        validated = schema.load(data)
        profile = db.session.query(Profile).filter_by(id=profile_id).first()
        if not profile:
            raise NotFound("Profile not found")
        if profile.role != "buyer":
            raise APIError("Only buyers can upgrade to retailer", status_code=400)

        shop = Shop(
            id=str(uuid.uuid4()),
            owner_id=profile.id,
            name=validated["shop_name"],
            category=validated["category"],
            address=validated.get("address"),
            status="pending",
        )
        profile.role = "retailer"
        db.session.add(shop)
        db.session.commit()
        return shop

    # Orders in these states still have goods or money moving.
    ACTIVE_ORDER_STATUSES = ("pending", "confirmed", "paid", "preparing", "out_for_delivery")

    @staticmethod
    def delete_account(profile, password):
        """Erase a profile and everything only it owns, once nothing is in flight.

        Refused while the person has orders in progress (as buyer, as the shop
        behind them, or as the rider carrying them) or a wallet balance, so a
        deletion never strands goods or money. A retailer's shop goes with them —
        listings, promotions, conversations and finished orders included.
        Dependent rows are removed explicitly: SQLite (dev/tests) does not
        enforce ON DELETE CASCADE and the ORM would otherwise NULL columns that
        are NOT NULL.
        """
        from server.models import (
            Conversation,
            Delivery,
            Dispute,
            Favorite,
            Notification,
            Order,
            Review,
            Shop,
            Wallet,
        )

        if not password or not bcrypt.checkpw(
            password.encode("utf-8"), profile.password_hash.encode("utf-8")
        ):
            # 403, not 401: the session is valid, only the confirmation failed,
            # and the client signs the user out on any 401.
            raise APIError("Incorrect password", status_code=403)
        if profile.role == "admin":
            raise APIError(
                "Administrator accounts are removed by another administrator", status_code=403
            )

        shop = db.session.query(Shop).filter_by(owner_id=profile.id).first()
        shop_id = shop.id if shop else None

        involved = Order.buyer_id == profile.id
        if shop_id:
            involved = involved | (Order.shop_id == shop_id)
        involved = involved | (Order.rider_id == profile.id)
        active = (
            db.session.query(Order)
            .filter(involved, Order.status.in_(AuthService.ACTIVE_ORDER_STATUSES))
            .count()
        )
        if active:
            raise APIError(
                "Finish or cancel your orders in progress before deleting your account",
                status_code=409,
            )
        wallet = db.session.query(Wallet).filter_by(owner_id=profile.id).first()
        if wallet and wallet.balance > 0:
            raise APIError(
                "Withdraw your wallet balance before deleting your account", status_code=409
            )

        # Finished deliveries this rider carried stay on the buyer's order, unlinked.
        db.session.query(Delivery).filter(Delivery.rider_id == profile.id).update(
            {Delivery.rider_id: None}, synchronize_session=False
        )
        db.session.query(Order).filter(Order.rider_id == profile.id).update(
            {Order.rider_id: None}, synchronize_session=False
        )
        db.session.query(Dispute).filter(Dispute.resolved_by == profile.id).update(
            {Dispute.resolved_by: None}, synchronize_session=False
        )

        # Their own orders, and every order placed with their shop; items,
        # payment, delivery, review and disputes cascade from each order.
        own_orders = Order.buyer_id == profile.id
        if shop_id:
            own_orders = own_orders | (Order.shop_id == shop_id)
        for order in db.session.query(Order).filter(own_orders).all():
            db.session.delete(order)
        db.session.flush()

        # Chats they started, and every chat with their shop (messages cascade).
        chats = Conversation.buyer_id == profile.id
        if shop_id:
            chats = chats | (Conversation.shop_id == shop_id)
        for conversation in db.session.query(Conversation).filter(chats).all():
            db.session.delete(conversation)

        db.session.query(Favorite).filter(Favorite.user_id == profile.id).delete(
            synchronize_session=False
        )
        db.session.query(Notification).filter(Notification.user_id == profile.id).delete(
            synchronize_session=False
        )
        if shop:
            db.session.query(Review).filter(Review.shop_id == shop_id).delete(
                synchronize_session=False
            )
            db.session.delete(shop)  # listings and promotions cascade
        if wallet:
            db.session.delete(wallet)  # transactions cascade
        db.session.flush()

        db.session.delete(profile)
        db.session.commit()
