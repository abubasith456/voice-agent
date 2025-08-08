from __future__ import annotations

from loguru import logger

SENSITIVE_KEYWORDS = {
    "password", "passcode", "otp", "pin", "secret",
}


def contains_sensitive_request(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in SENSITIVE_KEYWORDS)


def refusal_message() -> str:
    return (
        "I can't help with passwords, PINs, or other secrets. If you need to reset your password, "
        "please use the official mobile app or website."
    )


def log_sensitive_attempt(user_id: str | None, text: str) -> None:
    logger.warning(
        "Sensitive info request blocked | user_id={}, text={}", user_id, text
    )