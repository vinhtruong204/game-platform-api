"""add image to weapon and rename avatar_image to texture in character

Revision ID: 010a75238c4f
Revises: b3c4d5e6f7a8
Create Date: 2026-04-09 22:33:26.187026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010a75238c4f'
down_revision: Union[str, None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename avatar_image -> texture in character (preserves existing data)
    op.alter_column('character', 'avatar_image', new_column_name='texture')

    # Add image column to weapon with temporary default for existing rows
    op.add_column('weapon', sa.Column('image', sa.String(length=255), nullable=False, server_default=''))
    op.execute("UPDATE weapon SET image = LOWER(REPLACE(name, ' ', '-')) || '.png'")
    op.alter_column('weapon', 'image', server_default=None)


def downgrade() -> None:
    op.drop_column('weapon', 'image')
    op.alter_column('character', 'texture', new_column_name='avatar_image')
