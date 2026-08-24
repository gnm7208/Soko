from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Listing, ListingImage
from server.schemas.listing import ListingCreateSchema, ListingImageSchema, ListingSchema
from server.utils.auth import get_current_profile, retailer_required
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("listings", __name__)


@bp.route("/listings", methods=["GET"])
def list_listings():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        category_id = request.args.get("category_id")
        shop_id = request.args.get("shop_id")
        q = request.args.get("q")
        min_price = request.args.get("min_price", type=int)
        max_price = request.args.get("max_price", type=int)
        condition = request.args.get("condition")
        query = db.session.query(Listing)
        if category_id:
            query = query.filter(Listing.category_id == category_id)
        if shop_id:
            query = query.filter(Listing.shop_id == shop_id)
        if q:
            query = query.filter(Listing.title.ilike(f"%{q}%"))
        if min_price is not None:
            query = query.filter(Listing.price >= min_price)
        if max_price is not None:
            query = query.filter(Listing.price <= max_price)
        if condition:
            query = query.filter(Listing.condition == condition)
        total = query.count()
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        total_pages = (total + per_page - 1) // per_page
        schema = ListingSchema(many=True)
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


@bp.route("/listings/<listing_id>", methods=["GET"])
def get_listing(listing_id):
    try:
        listing = db.session.query(Listing).filter_by(id=listing_id).first()
        if not listing:
            raise NotFound("Listing not found")
        schema = ListingSchema()
        return jsonify(schema.dump(listing)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/listings", methods=["POST"])
@jwt_required()
@retailer_required
def create_listing():
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        data = request.get_json() or {}
        schema = ListingCreateSchema()
        validated = schema.load(data)
        listing = Listing(shop_id=profile.shop.id, **validated)
        db.session.add(listing)
        db.session.commit()
        schema_out = ListingSchema()
        return jsonify(schema_out.dump(listing)), 201
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/listings/<listing_id>", methods=["PATCH"])
@jwt_required()
@retailer_required
def update_listing(listing_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        listing = db.session.query(Listing).filter_by(id=listing_id).first()
        if not listing or listing.shop_id != profile.shop.id:
            raise NotFound("Listing not found")
        data = request.get_json() or {}
        schema = ListingCreateSchema(partial=True)
        validated = schema.load(data)
        for key, value in validated.items():
            setattr(listing, key, value)
        db.session.commit()
        schema_out = ListingSchema()
        return jsonify(schema_out.dump(listing)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/listings/<listing_id>", methods=["DELETE"])
@jwt_required()
@retailer_required
def delete_listing(listing_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        listing = db.session.query(Listing).filter_by(id=listing_id).first()
        if not listing or listing.shop_id != profile.shop.id:
            raise NotFound("Listing not found")
        listing.status = "deleted"
        db.session.commit()
        return jsonify({"message": "Listing deleted"}), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/listings/<listing_id>/images", methods=["POST"])
@jwt_required()
@retailer_required
def upload_listing_image(listing_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise Forbidden("Profile not found")
        listing = db.session.query(Listing).filter_by(id=listing_id).first()
        if not listing or listing.shop_id != profile.shop.id:
            raise NotFound("Listing not found")
        data = request.get_json() or {}
        if "url" not in data:
            raise APIError("Image URL is required", status_code=400)
        image = ListingImage(
            listing_id=listing_id,
            url=data["url"],
            position=data.get("position", 0),
        )
        db.session.add(image)
        db.session.commit()
        schema = ListingImageSchema()
        return jsonify(schema.dump(image)), 201
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500
