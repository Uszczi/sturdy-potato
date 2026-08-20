"""Shared position helpers for the manually-ordered repositories.

Tasks and projects both keep a per-user ``position`` and append new rows after
the current last one. Computing that slot as a subquery lets the INSERT assign
it atomically, so two concurrent creates can't read the same max and collide.
"""

from sqlalchemy import ScalarSelect, func
from sqlalchemy.orm import Mapped
from sqlmodel import select


def next_position_subquery(
    position_col: Mapped[int], user_col: Mapped[int], user_id: int
) -> ScalarSelect[int]:
    """Subquery for the slot after the user's current last row (0 when none)."""
    return (
        select(func.coalesce(func.max(position_col), -1) + 1)
        .where(user_col == user_id)
        .scalar_subquery()
    )
