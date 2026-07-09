"""add player_purchase_tokens table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'player_purchase_tokens',
        sa.Column('player_id', sa.UUID(), nullable=False),
        sa.Column('purchase_token', sa.String(length=512), nullable=False),
        sa.Column('sku', sa.String(length=128), nullable=False),
        sa.Column('platform', sa.String(length=32), nullable=False),
        sa.Column('credited_amount', sa.Integer(), nullable=False),
        sa.Column(
            'currency_type',
            postgresql.ENUM('gold', 'diamond', name='currencytype', create_type=False),
            nullable=False,
        ),
        sa.Column(
            'verified_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['player_id'], ['player_profile.player_id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('player_id', 'purchase_token'),
    )
    op.create_index(
        'ix_player_purchase_tokens_token',
        'player_purchase_tokens',
        ['purchase_token'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_player_purchase_tokens_token', table_name='player_purchase_tokens')
    op.drop_table('player_purchase_tokens')
