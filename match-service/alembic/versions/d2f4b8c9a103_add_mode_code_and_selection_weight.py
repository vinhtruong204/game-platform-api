"""add mode code and selection weight

Revision ID: d2f4b8c9a103
Revises: b6c3f31e9d12
Create Date: 2026-05-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2f4b8c9a103"
down_revision: Union[str, None] = "b6c3f31e9d12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("mode", sa.Column("code", sa.String(), nullable=True))
    op.add_column(
        "mode",
        sa.Column("selection_weight", sa.Integer(), nullable=False, server_default="0"),
    )

    op.execute(
        """
        UPDATE mode
        SET code = CASE
            WHEN lower(name) IN ('search & destroy', 'search and destroy') AND type = 'rank' THEN 'ranked_search_destroy'
            WHEN lower(name) IN ('search & destroy', 'search and destroy') THEN 'search_destroy'
            WHEN type = 'rank' THEN 'ranked_free_for_all'
            WHEN lower(name) IN ('free for all', 'normal') THEN 'free_for_all'
            ELSE lower(regexp_replace(name, '[^a-zA-Z0-9]+', '_', 'g'))
        END
        WHERE code IS NULL
        """
    )
    op.execute(
        """
        UPDATE mode
        SET selection_weight = CASE
            WHEN code = 'ranked_search_destroy' THEN 80
            WHEN code = 'ranked_free_for_all' THEN 20
            ELSE 0
        END
        """
    )


def downgrade() -> None:
    op.drop_column("mode", "selection_weight")
    op.drop_column("mode", "code")
