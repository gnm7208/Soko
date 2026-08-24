from flask import Blueprint, jsonify

from server.extensions import db
from server.models import Profile

bp = Blueprint("profiles", __name__)


@bp.route("/profiles/<profile_id>", methods=["GET"])
def get_profile(profile_id):
    profile = db.session.query(Profile).filter_by(id=profile_id).first()
    if not profile:
        return jsonify({"error": "not_found", "message": "Profile not found"}), 404
    return jsonify(
        {
            "id": profile.id,
            "full_name": profile.full_name,
            "phone": profile.phone,
            "avatar_url": profile.avatar_url,
            "role": profile.role,
        }
    ), 200
