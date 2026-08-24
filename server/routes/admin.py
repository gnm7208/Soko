from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.schemas.admin import MetricsSchema
from server.schemas.dispute import DisputeResolveSchema, DisputeSchema
from server.schemas.listing import ListingSchema
from server.schemas.shop import ShopSchema
from server.services import admin_service
from server.utils.auth import admin_required, get_current_profile
from server.utils.errors import APIError, NotFound

bp = Blueprint("admin", __name__)


def _page_args():
    return request.args.get("page", 1, type=int), request.args.get("per_page", 20, type=int)


def _paginated(items, page, per_page, total, total_pages):
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


@bp.route("/admin/metrics", methods=["GET"])
@jwt_required()
@admin_required
def get_metrics():
    try:
        return jsonify(MetricsSchema().dump(admin_service.get_metrics())), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/shops", methods=["GET"])
@jwt_required()
@admin_required
def list_shops():
    try:
        page, per_page = _page_args()
        status = request.args.get("status")
        items, total, total_pages = admin_service.list_shops(status, page, per_page)
        return jsonify(
            _paginated(ShopSchema(many=True).dump(items), page, per_page, total, total_pages)
        ), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/shops/<shop_id>/approve", methods=["PATCH"])
@jwt_required()
@admin_required
def approve_shop(shop_id):
    try:
        shop = admin_service.approve_shop(shop_id)
        return jsonify({"id": shop.id, "name": shop.name, "status": shop.status}), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/shops/<shop_id>/suspend", methods=["PATCH"])
@jwt_required()
@admin_required
def suspend_shop(shop_id):
    try:
        shop = admin_service.suspend_shop(shop_id)
        return jsonify({"id": shop.id, "name": shop.name, "status": shop.status}), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    try:
        page, per_page = _page_args()
        role = request.args.get("role")
        items, total, total_pages = admin_service.list_users(role, page, per_page)
        dumped = [admin_service.dump_user(profile) for profile in items]
        return jsonify(_paginated(dumped, page, per_page, total, total_pages)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/listings", methods=["GET"])
@jwt_required()
@admin_required
def list_listings():
    try:
        page, per_page = _page_args()
        status = request.args.get("status")
        shop_id = request.args.get("shop_id")
        items, total, total_pages = admin_service.list_admin_listings(
            status, shop_id, page, per_page
        )
        return jsonify(
            _paginated(ListingSchema(many=True).dump(items), page, per_page, total, total_pages)
        ), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/listings/<listing_id>", methods=["PATCH"])
@jwt_required()
@admin_required
def update_listing_admin(listing_id):
    try:
        data = request.get_json() or {}
        listing = admin_service.update_listing(listing_id, data)
        return jsonify({"id": listing.id, "title": listing.title, "status": listing.status}), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/payouts", methods=["GET"])
@jwt_required()
@admin_required
def list_payouts():
    try:
        page, per_page = _page_args()
        status = request.args.get("status", "pending")
        items, total, total_pages = admin_service.list_payouts(status, page, per_page)
        return jsonify(_paginated(items, page, per_page, total, total_pages)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/payouts/<payout_id>", methods=["PATCH"])
@jwt_required()
@admin_required
def update_payout(payout_id):
    try:
        data = request.get_json() or {}
        status = data.get("status")
        if not status:
            raise APIError("status is required", status_code=400)
        txn = admin_service.update_payout(payout_id, status)
        return (
            jsonify(
                {
                    "id": txn.id,
                    "wallet_id": txn.wallet_id,
                    "type": txn.type,
                    "amount": txn.amount,
                    "status": txn.status,
                }
            ),
            200,
        )
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/disputes", methods=["GET"])
@jwt_required()
@admin_required
def list_disputes():
    try:
        page, per_page = _page_args()
        status = request.args.get("status")
        items, total, total_pages = admin_service.list_disputes(status, page, per_page)
        return jsonify(
            _paginated(DisputeSchema(many=True).dump(items), page, per_page, total, total_pages)
        ), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/admin/disputes/<dispute_id>", methods=["PATCH"])
@jwt_required()
@admin_required
def resolve_dispute(dispute_id):
    try:
        admin_profile = get_current_profile()
        if not admin_profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        validated = DisputeResolveSchema().load(data)
        dispute = admin_service.resolve_dispute(
            dispute_id,
            admin_profile.id,
            validated["status"],
            validated.get("resolution_note"),
        )
        return jsonify(DisputeSchema().dump(dispute)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
