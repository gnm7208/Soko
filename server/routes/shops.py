from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Shop
from server.schemas.shop import ShopCreateSchema, ShopSchema
from server.services.storage import upload_image
from server.utils.auth import get_current_profile, retailer_required
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("shops", __name__)


@bp.route("/shops", methods=["GET"])
def list_shops():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        category = request.args.get("category")
        query = db.session.query(Shop)
        if category:
            query = query.filter(Shop.category == category)
        total = query.count()
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        total_pages = (total + per_page - 1) // per_page
        schema = ShopSchema(many=True)
        return jsonify(
            {
                "items": schema.dump(items),
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            }
        ), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/shops/mine", methods=["GET"])
@jwt_required()
@retailer_required
def get_my_shop():
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        shop = db.session.query(Shop).filter_by(owner_id=profile.id).first()
        if not shop:
            raise NotFound("You don't have a shop yet")
        schema = ShopSchema()
        return jsonify(schema.dump(shop)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/shops/<shop_id>", methods=["GET"])
def get_shop(shop_id):
    try:
        shop = db.session.query(Shop).filter_by(id=shop_id).first()
        if not shop:
            raise NotFound("Shop not found")
        schema = ShopSchema()
        return jsonify(schema.dump(shop)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/shops/<shop_id>", methods=["PATCH"])
@jwt_required()
@retailer_required
def update_shop(shop_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        shop = db.session.query(Shop).filter_by(id=shop_id, owner_id=profile.id).first()
        if not shop:
            raise NotFound("Shop not found")
        data = request.get_json() or {}
        schema = ShopCreateSchema()
        validated = schema.load(data)
        for key, value in validated.items():
            setattr(shop, key, value)
        db.session.commit()
        schema_out = ShopSchema()
        return jsonify(schema_out.dump(shop)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/shops/<shop_id>/images", methods=["POST"])
@jwt_required()
@retailer_required
def upload_shop_image(shop_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        shop = db.session.query(Shop).filter_by(id=shop_id, owner_id=profile.id).first()
        if not shop:
            raise NotFound("Shop not found")
        kind = request.form.get("kind", "logo")
        if kind not in ("logo", "cover"):
            raise APIError("kind must be 'logo' or 'cover'", status_code=400)
        if "file" not in request.files:
            raise APIError("Image file is required", status_code=400)
        url = upload_image(request.files["file"], folder="shops")
        if kind == "logo":
            shop.logo_url = url
        else:
            shop.cover_url = url
        db.session.commit()
        schema_out = ShopSchema()
        return jsonify(schema_out.dump(shop)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/shops", methods=["POST"])
@jwt_required()
def create_shop():
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        data = request.get_json() or {}
        schema = ShopCreateSchema()
        validated = schema.load(data)
        shop = Shop(owner_id=profile.id, **validated)
        db.session.add(shop)
        db.session.commit()
        schema_out = ShopSchema()
        return jsonify(schema_out.dump(shop)), 201
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500
