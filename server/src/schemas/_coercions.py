"""Shared ``field_validator`` helpers for the request schemas.

Plain functions (like ``project._normalize_color``) so the thin validators
across schemas share one definition of each coercion instead of repeating it.
"""


def strip_if_str(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


def empty_to_none(value: object) -> object:
    """Treat an empty form string as "not provided" for an optional field."""
    return None if value == "" else value


def reject_null(value: object) -> object:
    if value is None:
        raise ValueError("Input should not be null")
    return value
