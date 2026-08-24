from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Dispute, Order
from server.schemas.dispute import DisputeCreateSchema, DisputeSchema
from server.utils.auth import get_current_profile
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("disputes", __name__)


@bp.route("/disputes", methods=["POST"])
@jwt_required()
def create_dispute():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        schema = DisputeCreateSchema()
        validated = schema.load(data)
        order = db.session.query(Order).filter_by(id=validated["order_id"]).first()
        if not order:
            raise NotFound("Order not found")
        if order.buyer_id != profile.id and order.shop.owner_id != profile.id:
            raise Forbidden("Not authorized to raise a dispute on this order")
        dispute = Dispute(
            order_id=order.id,
            raised_by=profile.id,
            reason=validated["reason"],
        )
        db.session.add(dispute)
        db.session.commit()
        return jsonify(DisputeSchema().dump(dispute)), 201
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/disputes/mine", methods=["GET"])
@jwt_required()
def list_my_disputes():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = db.session.query(Dispute).filter_by(raised_by=profile.id)
        total = query.count()
        items = (
            query.order_by(Dispute.created_at.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )
        schema = DisputeSchema(many=True)
        return jsonify(
            {
                "items": schema.dump(items),
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
            }
        ), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
