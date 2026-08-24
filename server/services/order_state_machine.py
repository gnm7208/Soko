from server.utils.errors import APIError


class OrderStateMachine:
    TRANSITIONS = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["paid", "cancelled"],
        "paid": ["preparing", "refunded"],
        "preparing": ["out_for_delivery"],
        "out_for_delivery": ["delivered", "cancelled"],
        "delivered": ["refunded"],
        "cancelled": [],
        "refunded": [],
    }

    @classmethod
    def advance(cls, order, new_status):
        allowed = cls.TRANSITIONS.get(order.status, [])
        if new_status not in allowed:
            raise APIError(
                f"Cannot transition from {order.status} to {new_status}", status_code=409
            )
        order.status = new_status
        return order

    @classmethod
    def can_transition(cls, current, next_status):
        return next_status in cls.TRANSITIONS.get(current, [])
