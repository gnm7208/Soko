from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt

from server.extensions import db
from server.models import Profile


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles:
                return jsonify({"error": "forbidden", "message": "Insufficient permissions"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_current_profile():
    claims = get_jwt()
    user_id = claims.get("sub")
    return db.session.query(Profile).filter_by(user_id=user_id).first()


buyer_required = role_required("buyer", "retailer", "rider", "admin")
retailer_required = role_required("retailer", "admin")
rider_required = role_required("rider", "admin")
admin_required = role_required("admin")
