from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Order, Review
from server.schemas.review import ReviewCreateSchema, ReviewSchema
from server.utils.auth import buyer_required, get_current_profile
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("reviews", __name__)


@bp.route("/reviews", methods=["POST"])
@jwt_required()
@buyer_required
def create_review():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        schema = ReviewCreateSchema()
        validated = schema.load(data)
        order = db.session.query(Order).filter_by(id=validated["order_id"]).first()
        if not order:
            raise NotFound("Order not found")
        if order.buyer_id != profile.id:
            raise Forbidden("You can only review your own orders")
        existing = db.session.query(Review).filter_by(order_id=validated["order_id"]).first()
        if existing:
            raise APIError("Review already exists for this order", status_code=409)
        review = Review(
            order_id=validated["order_id"],
            shop_id=order.shop_id,
            buyer_id=profile.id,
            rating=validated["rating"],
            comment=validated.get("comment"),
        )
        db.session.add(review)
        db.session.commit()
        review.reviewer_id = review.buyer_id
        return jsonify(ReviewSchema().dump(review)), 201
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/shops/<shop_id>/reviews", methods=["GET"])
def list_shop_reviews(shop_id):
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = db.session.query(Review).filter_by(shop_id=shop_id)
        total = query.count()
        items = (
            query.order_by(Review.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        for r in items:
            r.reviewer_id = r.buyer_id
        schema = ReviewSchema(many=True)
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
