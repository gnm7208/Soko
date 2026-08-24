from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Notification
from server.schemas.notification import NotificationSchema
from server.utils.auth import get_current_profile
from server.utils.errors import APIError, NotFound

bp = Blueprint("notifications", __name__)


def _decorate(notif):
    payload = notif.payload or {}
    notif.title = payload.get("title")
    notif.body = payload.get("body")
    notif.read = notif.read_at is not None
    return notif


@bp.route("/notifications", methods=["GET"])
@jwt_required()
def list_notifications():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = db.session.query(Notification).filter_by(user_id=profile.id)
        total = query.count()
        items = (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        for n in items:
            _decorate(n)
        schema = NotificationSchema(many=True)
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


@bp.route("/notifications/<notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(notification_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        notif = (
            db.session.query(Notification).filter_by(id=notification_id, user_id=profile.id).first()
        )
        if not notif:
            raise NotFound("Notification not found")
        notif.read_at = datetime.utcnow()
        db.session.commit()
        _decorate(notif)
        return jsonify(NotificationSchema().dump(notif)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/notifications/mark-all-read", methods=["POST"])
@jwt_required()
def mark_all_read():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        db.session.query(Notification).filter_by(user_id=profile.id, read_at=None).update(
            {Notification.read_at: datetime.utcnow()}
        )
        db.session.commit()
        return jsonify({"message": "All notifications marked as read"}), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
