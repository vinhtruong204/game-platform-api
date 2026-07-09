"""add matchmaking system

Revision ID: a1b2c3d4e5f6
Revises: 86b84e9318a5
Create Date: 2026-03-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '86b84e9318a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction in PostgreSQL
    op.execute("COMMIT")
    op.execute("ALTER TYPE matchstatus ADD VALUE IF NOT EXISTS 'pending' BEFORE 'finished'")
    op.execute("BEGIN")

    # Make end_time nullable
    op.alter_column('match_history', 'end_time', existing_type=sa.DateTime(), nullable=True)

    # Add players_per_team to mode
    op.add_column('mode', sa.Column('players_per_team', sa.Integer(), nullable=False, server_default='1'))

    # Create matchmaking_queue table (queuestatus enum is created automatically)
    op.create_table(
        'matchmaking_queue',
        sa.Column('queue_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('rank_point', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('waiting', 'matched', name='queuestatus'), nullable=False, server_default='waiting'),
        sa.Column('matched_match_id', sa.Integer(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('matched_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['matched_match_id'], ['match_history.match_id']),
        sa.PrimaryKeyConstraint('queue_id'),
        sa.UniqueConstraint('player_id'),
    )


def downgrade() -> None:
    op.drop_table('matchmaking_queue')

    sa.Enum('waiting', 'matched', name='queuestatus').drop(op.get_bind(), checkfirst=True)

    op.drop_column('mode', 'players_per_team')

    op.alter_column('match_history', 'end_time', existing_type=sa.DateTime(), nullable=False)

    # Note: Cannot remove 'pending' from matchstatus enum in PostgreSQL without recreating it
