from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from server.extensions import db
from server.models import Conversation, Listing, Message, Shop
from server.schemas.chat import ConversationSchema, MessageSchema
from server.utils.auth import buyer_required, get_current_profile
from server.utils.errors import APIError, Forbidden, NotFound

bp = Blueprint("chat", __name__)


def _is_participant(conv, profile):
    if conv.buyer_id == profile.id:
        return True
    shop = db.session.query(Shop).filter_by(id=conv.shop_id, owner_id=profile.id).first()
    return shop is not None


def _decorate_conversation(conv, profile_id):
    last = (
        db.session.query(Message)
        .filter_by(conversation_id=conv.id)
        .order_by(Message.created_at.desc())
        .first()
    )
    unread = (
        db.session.query(Message)
        .filter_by(conversation_id=conv.id, read_at=None)
        .filter(Message.sender_id != profile_id)
        .count()
    )
    conv.last_message = last.body if last else None
    conv.unread_count = unread
    return conv


@bp.route("/conversations", methods=["GET"])
@jwt_required()
def list_conversations():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        conversations = (
            db.session.query(Conversation)
            .filter_by(buyer_id=profile.id)
            .order_by(Conversation.last_message_at.desc())
            .all()
        )
        for conv in conversations:
            _decorate_conversation(conv, profile.id)
        schema = ConversationSchema(many=True)
        return jsonify(schema.dump(conversations)), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/conversations/<conversation_id>", methods=["GET"])
@jwt_required()
def get_conversation(conversation_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        conv = db.session.query(Conversation).filter_by(id=conversation_id).first()
        if not conv:
            raise NotFound("Conversation not found")
        if not _is_participant(conv, profile):
            raise Forbidden("Not a participant in this conversation")
        messages = (
            db.session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        for m in messages:
            m.read = m.read_at is not None
        _decorate_conversation(conv, profile.id)
        data = ConversationSchema().dump(conv)
        data["messages"] = MessageSchema(many=True).dump(messages)
        return jsonify(data), 200
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/conversations", methods=["POST"])
@jwt_required()
@buyer_required
def start_conversation():
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        shop_id = data.get("shop_id")
        listing_id = data.get("listing_id")
        body = data.get("body")
        if not shop_id or not body:
            raise APIError("shop_id and body are required", status_code=400)
        shop = db.session.query(Shop).filter_by(id=shop_id).first()
        if not shop:
            raise NotFound("Shop not found")
        if listing_id:
            listing = db.session.query(Listing).filter_by(id=listing_id).first()
            if not listing:
                raise NotFound("Listing not found")
        conv = Conversation(
            buyer_id=profile.id,
            shop_id=shop_id,
            listing_id=listing_id,
        )
        db.session.add(conv)
        db.session.flush()
        message = Message(
            conversation_id=conv.id,
            sender_id=profile.id,
            body=body,
        )
        db.session.add(message)
        from datetime import datetime

        conv.last_message_at = datetime.utcnow()
        db.session.commit()
        conv.last_message = body
        conv.unread_count = 0
        return jsonify(ConversationSchema().dump(conv)), 201
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@bp.route("/conversations/<conversation_id>/messages", methods=["POST"])
@jwt_required()
def send_message(conversation_id):
    try:
        profile = get_current_profile()
        if not profile:
            raise NotFound("Profile not found")
        data = request.get_json() or {}
        body = data.get("body")
        if not body:
            raise APIError("body is required", status_code=400)
        conv = db.session.query(Conversation).filter_by(id=conversation_id).first()
        if not conv:
            raise NotFound("Conversation not found")
        if not _is_participant(conv, profile):
            raise Forbidden("Not a participant in this conversation")
        message = Message(
            conversation_id=conv.id,
            sender_id=profile.id,
            body=body,
        )
        db.session.add(message)
        from datetime import datetime

        conv.last_message_at = datetime.utcnow()
        db.session.commit()
        message.read = False
        return jsonify(MessageSchema().dump(message)), 201
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500
