from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Favorite, Listing
from server.schemas.listing import ListingSchema
from server.utils.auth import buyer_required, get_current_profile
from server.utils.errors import APIError, NotFound

bp = Blueprint("favorites", __name__)


@bp.route("/favorites/<listing_id>", methods=["POST"])
@jwt_required()
@buyer_required
def toggle_favorite(listing_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        favorite = (
            db.session.query(Favorite).filter_by(user_id=profile.id, listing_id=listing_id).first()
        )
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"favorited": False}), 200
        favorite = Favorite(user_id=profile.id, listing_id=listing_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"favorited": True}), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/favorites", methods=["GET"])
@jwt_required()
@buyer_required
def list_favorites():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = db.session.query(Listing).join(Favorite).filter(Favorite.user_id == profile.id)
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
