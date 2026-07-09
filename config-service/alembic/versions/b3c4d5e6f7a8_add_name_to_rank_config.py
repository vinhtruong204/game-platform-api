"""add name to rank_config

Revision ID: b3c4d5e6f7a8
Revises: 62dfad56692c
Create Date: 2026-04-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = '62dfad56692c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('rank_config', sa.Column('name', sa.String(length=100), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('rank_config', 'name')
