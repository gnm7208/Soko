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
