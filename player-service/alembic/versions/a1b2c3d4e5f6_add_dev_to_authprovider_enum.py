"""add dev to authprovider enum

Revision ID: a1b2c3d4e5f6
Revises: ec1144b0f3d1
Create Date: 2026-03-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ec1144b0f3d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE authprovider ADD VALUE IF NOT EXISTS 'dev'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type.
    # A full migration would require recreating the type, which is out of scope.
    pass
