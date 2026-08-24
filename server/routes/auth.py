from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required, set_access_cookies, unset_jwt_cookies

from server.extensions import db, limiter
from server.schemas.auth import ProfileUpdateSchema, UpgradeRetailerSchema
from server.services.auth_service import AuthService
from server.services.storage import upload_image
from server.utils.auth import get_current_profile
from server.utils.errors import APIError

bp = Blueprint("auth", __name__)


@bp.route("/auth/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    try:
        data = request.get_json() or {}
        result = AuthService.register(data)
        response = make_response(jsonify(result), 201)
        set_access_cookies(response, result["access_token"])
        return response
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json() or {}
        result = AuthService.login(data)
        response = make_response(jsonify(result), 200)
        set_access_cookies(response, result["access_token"])
        return response
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    response = make_response(jsonify({"message": "logged out"}), 200)
    unset_jwt_cookies(response)
    return response


@bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_me():
    try:
        profile = get_current_profile()
        if not profile:
            return jsonify({"error": "not_found", "message": "Profile not found"}), 404
        return jsonify(
            {
                "id": profile.id,
                "user_id": profile.user_id,
                "role": profile.role,
                "full_name": profile.full_name,
                "phone": profile.phone,
                "avatar_url": profile.avatar_url,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/auth/me", methods=["PATCH"])
@jwt_required()
def update_me():
    try:
        data = request.get_json() or {}
        schema = ProfileUpdateSchema()
        validated = schema.load(data)
        profile = get_current_profile()
        if not profile:
            return jsonify({"error": "not_found", "message": "Profile not found"}), 404
        profile = AuthService.update_profile(profile.id, validated)
        return jsonify(
            {
                "id": profile.id,
                "user_id": profile.user_id,
                "role": profile.role,
                "full_name": profile.full_name,
                "phone": profile.phone,
                "avatar_url": profile.avatar_url,
            }
        ), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/auth/me/avatar", methods=["POST"])
@jwt_required()
def upload_my_avatar():
    try:
        profile = get_current_profile()
        if not profile:
            return jsonify({"error": "not_found", "message": "Profile not found"}), 404
        if "file" not in request.files:
            raise APIError("Image file is required", status_code=400)
        profile.avatar_url = upload_image(request.files["file"], folder="avatars")
        db.session.commit()
        return jsonify(
            {
                "id": profile.id,
                "user_id": profile.user_id,
                "role": profile.role,
                "full_name": profile.full_name,
                "phone": profile.phone,
                "avatar_url": profile.avatar_url,
            }
        ), 200
    except APIError as e:
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/auth/upgrade-retailer", methods=["POST"])
@jwt_required()
def upgrade_retailer():
    try:
        data = request.get_json() or {}
        schema = UpgradeRetailerSchema()
        validated = schema.load(data)
        profile = get_current_profile()
        if not profile:
            return jsonify({"error": "not_found", "message": "Profile not found"}), 404
        shop = AuthService.upgrade_to_retailer(profile.id, validated)
        return jsonify({"id": shop.id, "name": shop.name, "status": shop.status}), 201
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
