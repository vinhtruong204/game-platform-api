"""add matchmaking mode filters

Revision ID: b6c3f31e9d12
Revises: a1b2c3d4e5f6
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6c3f31e9d12'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('matchmaking_queue', sa.Column('game_mode', sa.String(), server_default='rank', nullable=False))
    op.add_column('matchmaking_queue', sa.Column('map_id', sa.Integer(), nullable=True))
    op.add_column('matchmaking_queue', sa.Column('mode_id', sa.Integer(), nullable=True))
    op.add_column('matchmaking_queue', sa.Column('players_per_team', sa.Integer(), server_default='1', nullable=False))
    op.create_foreign_key('fk_matchmaking_queue_map_id', 'matchmaking_queue', 'map', ['map_id'], ['map_id'])
    op.create_foreign_key('fk_matchmaking_queue_mode_id', 'matchmaking_queue', 'mode', ['mode_id'], ['mode_id'])


def downgrade() -> None:
    op.drop_constraint('fk_matchmaking_queue_mode_id', 'matchmaking_queue', type_='foreignkey')
    op.drop_constraint('fk_matchmaking_queue_map_id', 'matchmaking_queue', type_='foreignkey')
    op.drop_column('matchmaking_queue', 'players_per_team')
    op.drop_column('matchmaking_queue', 'mode_id')
    op.drop_column('matchmaking_queue', 'map_id')
    op.drop_column('matchmaking_queue', 'game_mode')
