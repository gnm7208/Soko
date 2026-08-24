from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Delivery, Order
from server.schemas.delivery import DeliverySchema
from server.utils.auth import get_current_profile
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("deliveries", __name__)


@bp.route("/deliveries", methods=["GET"])
@jwt_required()
def list_deliveries():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        status = request.args.get("status")
        query = db.session.query(Delivery)
        if profile.role == "rider":
            query = query.filter_by(rider_id=profile.id)
        elif profile.role == "retailer":
            query = query.join(Order).filter(
                Order.shop_id == (profile.shop.id if profile.shop else None)
            )
        elif profile.role == "admin":
            pass
        else:
            query = query.join(Order).filter(Order.buyer_id == profile.id)
        if status:
            query = query.filter_by(status=status)
        total = query.count()
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        schema = DeliverySchema(many=True)
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


@bp.route("/deliveries/<delivery_id>", methods=["PATCH"])
@jwt_required()
def update_delivery(delivery_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        delivery = db.session.query(Delivery).filter_by(id=delivery_id).first()
        if not delivery:
            raise NotFound("Delivery not found")
        if profile.role == "rider" and delivery.rider_id != profile.id:
            raise Forbidden("Not authorized")
        if profile.role == "retailer" and delivery.order.shop.owner_id != profile.id:
            raise Forbidden("Not authorized")
        if profile.role not in ("rider", "retailer", "admin"):
            raise Forbidden("Not authorized")
        if "status" in data:
            delivery.status = data["status"]
        if "tracking_updates" in data:
            delivery.tracking_updates = data["tracking_updates"]
        db.session.commit()
        schema = DeliverySchema()
        return jsonify(schema.dump(delivery)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/deliveries/<delivery_id>/assign", methods=["POST"])
@jwt_required()
def assign_rider(delivery_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        rider_id = data.get("rider_id")
        if not rider_id:
            raise APIError("rider_id is required", status_code=400)
        delivery = db.session.query(Delivery).filter_by(id=delivery_id).first()
        if not delivery:
            raise NotFound("Delivery not found")
        if profile.role != "admin" and delivery.order.shop.owner_id != profile.id:
            raise Forbidden("Not authorized")
        delivery.rider_id = rider_id
        if delivery.status == "pending":
            delivery.status = "assigned"
        db.session.commit()
        schema = DeliverySchema()
        return jsonify(schema.dump(delivery)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500
