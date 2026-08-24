import pytest

from server.services.order_state_machine import OrderStateMachine
from server.utils.errors import APIError


class FakeOrder:
    def __init__(self, status):
        self.status = status


class TestOrderStateMachine:
    def test_valid_transitions(self):
        assert OrderStateMachine.can_transition("pending", "confirmed") is True
        assert OrderStateMachine.can_transition("pending", "cancelled") is True
        assert OrderStateMachine.can_transition("pending", "paid") is False

    def test_advance_success(self):
        order = FakeOrder("pending")
        OrderStateMachine.advance(order, "confirmed")
        assert order.status == "confirmed"

    def test_advance_invalid(self):
        order = FakeOrder("pending")
        with pytest.raises(APIError):
            OrderStateMachine.advance(order, "preparing")

    def test_advance_cancelled(self):
        order = FakeOrder("cancelled")
        with pytest.raises(APIError):
            OrderStateMachine.advance(order, "confirmed")

    def test_full_flow(self):
        flow = ["pending", "confirmed", "paid", "preparing", "out_for_delivery", "delivered"]
        order = FakeOrder("pending")
        for next_status in flow[1:]:
            OrderStateMachine.advance(order, next_status)
            assert order.status == next_status
