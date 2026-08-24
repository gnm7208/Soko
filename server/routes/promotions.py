from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Listing, Promotion, Shop
from server.schemas.promotion import PromotionCreateSchema, PromotionSchema
from server.utils.auth import get_current_profile, retailer_required
from server.utils.errors import APIError, NotFound

bp = Blueprint("promotions", __name__)


def _shop_for_profile(profile):
    shop = db.session.query(Shop).filter_by(owner_id=profile.id).first()
    if not shop:
        raise NotFound("Shop not found for this retailer")
    return shop


def _decorate(promo):
    promo.active = promo.starts_at <= datetime.utcnow() <= promo.ends_at
    return promo


@bp.route("/promotions", methods=["POST"])
@jwt_required()
@retailer_required
def create_promotion():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        schema = PromotionCreateSchema()
        validated = schema.load(data)
        shop = _shop_for_profile(profile)
        if validated.get("listing_id"):
            listing = (
                db.session.query(Listing)
                .filter_by(id=validated["listing_id"], shop_id=shop.id)
                .first()
            )
            if not listing:
                raise NotFound("Listing not found")
        promo = Promotion(
            shop_id=shop.id,
            listing_id=validated.get("listing_id"),
            type="percentage",
            starts_at=validated["starts_at"],
            ends_at=validated["ends_at"],
            discount_pct=validated["discount_pct"],
        )
        db.session.add(promo)
        db.session.commit()
        _decorate(promo)
        return jsonify(PromotionSchema().dump(promo)), 201
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/promotions", methods=["GET"])
@jwt_required()
@retailer_required
def list_promotions():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        shop = _shop_for_profile(profile)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = db.session.query(Promotion).filter_by(shop_id=shop.id)
        total = query.count()
        items = (
            query.order_by(Promotion.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        for p in items:
            _decorate(p)
        schema = PromotionSchema(many=True)
        return (
            jsonify(
                {
                    "items": schema.dump(items),
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page,
                }
            ),
            200,
        )
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/promotions/<promotion_id>", methods=["DELETE"])
@jwt_required()
@retailer_required
def cancel_promotion(promotion_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        shop = _shop_for_profile(profile)
        promo = db.session.query(Promotion).filter_by(id=promotion_id, shop_id=shop.id).first()
        if not promo:
            raise NotFound("Promotion not found")
        db.session.delete(promo)
        db.session.commit()
        return jsonify({"message": "Promotion cancelled"}), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
