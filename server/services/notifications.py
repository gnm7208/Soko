import os
import uuid

import resend

from server.extensions import db
from server.models import Notification

resend.api_key = ""


def send_email(to, subject, body):
    if not resend.api_key:
        return False
    try:
        resend.Emails.send(
            {
                "from": "noreply@soko.app",
                "to": to,
                "subject": subject,
                "html": body,
            }
        )
        return True
    except Exception:
        return False


def send_push(user_id, title, body):
    token = os.getenv("EXPO_PUSH_ACCESS_TOKEN")
    if not token:
        return False
    return False


def create_notification(user_id, type, payload):
    notification = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=type,
        payload=payload,
    )
    db.session.add(notification)
    db.session.commit()
    return notification
