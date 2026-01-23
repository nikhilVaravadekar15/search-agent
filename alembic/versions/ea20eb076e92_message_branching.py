"""message branching

Revision ID: ea20eb076e92
Revises: 20e5c9ad9ae0
Create Date: 2026-01-19 16:29:46.371949

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea20eb076e92"
down_revision: Union[str, Sequence[str], None] = "20e5c9ad9ae0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add parent_id (explicit NULL default)
    op.add_column(
        "messages",
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            server_default=None,
        ),
    )

    op.create_foreign_key(
        "fk_messages_parent_id",
        "messages",
        "messages",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # 2. Add follow_context (explicit NULL default)
    op.add_column(
        "messages",
        sa.Column(
            "follow_context",
            postgresql.JSONB(),
            nullable=True,
            server_default=None,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("messages", "follow_context")
    op.drop_constraint(
        "fk_messages_parent_id",
        "messages",
        type_="foreignkey",
    )
    op.drop_column("messages", "parent_id")
