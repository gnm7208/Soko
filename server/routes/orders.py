from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Listing, Order, OrderItem, Shop
from server.schemas.order import OrderCreateSchema, OrderSchema
from server.services.order_state_machine import OrderStateMachine
from server.utils.auth import buyer_required, get_current_profile
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("orders", __name__)


@bp.route("/orders", methods=["GET"])
@jwt_required()
def list_orders():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        status = request.args.get("status")
        query = db.session.query(Order)
        if profile.role == "buyer":
            query = query.filter_by(buyer_id=profile.id)
        elif profile.role == "retailer":
            query = query.filter_by(shop_id=profile.shop.id if profile.shop else None)
        elif profile.role != "admin":
            raise Forbidden("Insufficient permissions")
        if status:
            query = query.filter_by(status=status)
        total = query.count()
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        schema = OrderSchema(many=True)
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


@bp.route("/orders/<order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise NotFound("Order not found")
        if (
            profile.role != "admin"
            and order.buyer_id != profile.id
            and order.shop.owner_id != profile.id
        ):
            raise Forbidden("Not authorized")
        schema = OrderSchema()
        return jsonify(schema.dump(order)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/orders", methods=["POST"])
@jwt_required()
@buyer_required
def create_order():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        schema = OrderCreateSchema()
        validated = schema.load(data)
        shop = db.session.query(Shop).filter_by(id=validated["shop_id"]).first()
        if not shop:
            raise NotFound("Shop not found")
        total = 0
        items = []
        for item in validated["items"]:
            listing = db.session.query(Listing).filter_by(id=item["listing_id"]).first()
            if not listing or listing.shop_id != shop.id:
                raise NotFound(f"Listing {item['listing_id']} not found in shop")
            item_total = listing.price * item["qty"]
            total += item_total
            items.append(
                OrderItem(
                    listing_id=listing.id,
                    title_snapshot=listing.title,
                    price_snapshot=listing.price,
                    qty=item["qty"],
                )
            )
        order = Order(
            buyer_id=profile.id,
            shop_id=shop.id,
            total=total,
            delivery_method=validated.get("delivery_method", "pickup"),
            delivery_address=validated.get("delivery_address"),
            delivery_lat=validated.get("delivery_lat"),
            delivery_lng=validated.get("delivery_lng"),
            payment_method=validated["payment_method"],
        )
        db.session.add(order)
        db.session.flush()
        for item in items:
            item.order_id = order.id
            db.session.add(item)
        db.session.commit()
        schema_out = OrderSchema()
        return jsonify(schema_out.dump(order)), 201
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/orders/<order_id>/status", methods=["PATCH"])
@jwt_required()
def update_order_status(order_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        status = data.get("status")
        if not status:
            raise APIError("status is required", status_code=400)
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise NotFound("Order not found")
        if profile.role != "admin" and order.shop.owner_id != profile.id:
            raise Forbidden("Not authorized")
        order = OrderStateMachine.advance(order, status)
        schema = OrderSchema()
        return jsonify(schema.dump(order)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/orders/<order_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_order(order_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise NotFound("Order not found")
        if (
            profile.role != "admin"
            and order.buyer_id != profile.id
            and order.shop.owner_id != profile.id
        ):
            raise Forbidden("Not authorized")
        order = OrderStateMachine.advance(order, "cancelled")
        schema = OrderSchema()
        return jsonify(schema.dump(order)), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500
