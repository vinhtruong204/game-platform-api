"""add item to itemtype enum

Revision ID: a8b9c0d1e2f3
Revises: 7b25e16a29f9
Create Date: 2026-04-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, None] = '7b25e16a29f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'item'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type.
    pass
