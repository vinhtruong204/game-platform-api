"""add ammo column to weapon

Revision ID: c1d2e3f4a5b6
Revises: 010a75238c4f
Create Date: 2026-04-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = '010a75238c4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'weapon',
        sa.Column('ammo', sa.Integer(), nullable=False, server_default='0'),
    )
    # weapon_type is the slot type (primary/secondary/melee/grenade) in this schema.
    op.execute("UPDATE weapon SET ammo = 30 WHERE weapon_type = 'primary'")
    op.execute("UPDATE weapon SET ammo = 12 WHERE weapon_type = 'secondary'")
    op.execute("UPDATE weapon SET ammo = 0  WHERE weapon_type = 'melee'")
    op.execute("UPDATE weapon SET ammo = 0  WHERE weapon_type = 'grenade'")
    # Per-weapon overrides
    op.execute("UPDATE weapon SET ammo = 5  WHERE name = 'AWP'")
    op.execute("UPDATE weapon SET ammo = 8  WHERE name ILIKE 'Shotgun%'")
    op.execute("UPDATE weapon SET ammo = 50 WHERE name IN ('P90', 'MP5')")
    op.alter_column('weapon', 'ammo', server_default=None)


def downgrade() -> None:
    op.drop_column('weapon', 'ammo')
