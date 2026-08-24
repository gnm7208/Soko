from flask_jwt_extended import verify_jwt_in_request
from flask_socketio import Namespace, emit, join_room

from server.extensions import db
from server.models import Conversation, Message


class ChatNamespace(Namespace):
    def on_connect(self, auth):
        try:
            verify_jwt_in_request()
            return True
        except Exception:
            return False

    def on_join(self, data):
        conversation_id = data.get("conversation_id")
        conv = db.session.query(Conversation).filter_by(id=conversation_id).first()
        if not conv:
            emit("error", {"message": "Conversation not found"})
            return
        join_room(f"conversation_{conversation_id}")
        emit("joined", {"conversation_id": conversation_id})

    def on_send_message(self, data):
        conversation_id = data.get("conversation_id")
        body = data.get("body")
        if not body:
            emit("error", {"message": "body is required"})
            return

        conv = db.session.query(Conversation).filter_by(id=conversation_id).first()
        if not conv:
            emit("error", {"message": "Conversation not found"})
            return

        message = Message(
            conversation_id=conversation_id,
            sender_id=data.get("sender_id"),
            body=body,
        )
        db.session.add(message)
        from datetime import datetime

        conv.last_message_at = datetime.utcnow()
        db.session.commit()

        emit(
            "receive_message",
            {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "sender_id": message.sender_id,
                "body": message.body,
                "read_at": message.read_at,
                "created_at": message.created_at.isoformat() if message.created_at else None,
            },
            room=f"conversation_{conversation_id}",
        )
