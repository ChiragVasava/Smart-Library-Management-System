"""
payment.py

Handles fine payments and integrates with an external (mockable)
payment gateway.

Demonstrates: ABC, inheritance, try/except/finally, while loop,
raise statements, custom decorators, external dependency for mocking.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Optional

from constants import MAX_PAYMENT_RETRIES
from decorators import retry, timed
from exceptions import InsufficientFundsError, PaymentGatewayTimeoutError
from logger import get_logger

logger = get_logger()


class PaymentGateway:
    """
    Represents an external payment processing service.

    This class is intentionally simple so that it can be easily mocked
    or patched in unit tests (e.g. via unittest.mock.patch).
    """

    def charge(self, amount: float, card_token: str) -> bool:
        """
        Simulate charging a card through an external network call.

        In production this would call out to a real payment provider.
        Here it randomly succeeds to emulate network flakiness, which
        is useful for exercising retry logic in tests.
        """
        if not card_token:
            raise PaymentGatewayTimeoutError(attempts=1)
        return random.random() > 0.2


class PaymentMethod(ABC):
    """Abstract base class for all supported payment methods."""

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """Process a payment of the given amount. Returns True on success."""
        raise NotImplementedError

    @abstractmethod
    def method_name(self) -> str:
        """Return a human-readable name for this payment method."""
        raise NotImplementedError


class CreditCardPayment(PaymentMethod):
    """Payment method backed by a credit card and an external gateway."""

    def __init__(self, card_token: str, gateway: Optional[PaymentGateway] = None) -> None:
        self.card_token = card_token
        self.gateway = gateway or PaymentGateway()

    def method_name(self) -> str:
        return "credit_card"

    @timed
    @retry(max_attempts=MAX_PAYMENT_RETRIES)
    def pay(self, amount: float) -> bool:
        """
        Attempt to charge the credit card, retrying on failure.

        Demonstrates: try/except/finally, while loop, raise.
        """
        attempts = 0
        succeeded = False
        try:
            while attempts < MAX_PAYMENT_RETRIES and not succeeded:
                attempts += 1
                succeeded = self.gateway.charge(amount, self.card_token)
                if not succeeded:
                    logger.warning(
                        "Charge attempt %d/%d failed", attempts, MAX_PAYMENT_RETRIES
                    )
            if not succeeded:
                raise PaymentGatewayTimeoutError(attempts=attempts)
            return succeeded
        except PaymentGatewayTimeoutError:
            raise
        finally:
            logger.info(
                "Payment attempt finished for token=%s amount=%.2f",
                self.card_token,
                amount,
            )


class CashPayment(PaymentMethod):
    """Payment method representing a cash transaction at the front desk."""

    def __init__(self, cash_available: float) -> None:
        self.cash_available = cash_available

    def method_name(self) -> str:
        return "cash"

    def pay(self, amount: float) -> bool:
        """
        Process a cash payment.

        Raises:
            InsufficientFundsError: if not enough cash is available.
        """
        if amount > self.cash_available:
            raise InsufficientFundsError(amount)
        self.cash_available -= amount
        return True


class PaymentProcessor:
    """Coordinates fine payments using a pluggable PaymentMethod."""

    def process_fine(self, method: PaymentMethod, amount: float) -> bool:
        """
        Process a fine payment through the given payment method.

        Demonstrates: if statement, return, polymorphism via ABC.
        """
        if amount <= 0:
            return True
        return method.pay(amount)
