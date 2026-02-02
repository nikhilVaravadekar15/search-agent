"""Add cascade to messages_conversation_id_fkey migration

Revision ID: cccebd9922d6
Revises: ea20eb076e92
Create Date: 2026-02-02 15:10:11.482936

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cccebd9922d6"
down_revision: Union[str, Sequence[str], None] = "ea20eb076e92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "messages_conversation_id_fkey",
        "messages",
        type_="foreignkey",
        if_exists=True,
    )

    # 2. Recreate with ON DELETE CASCADE
    op.create_foreign_key(
        "messages_conversation_id_fkey",
        "messages",
        "conversation_threads",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "messages_conversation_id_fkey",
        "messages",
        type_="foreignkey",
        if_exists=True,
    )

    op.create_foreign_key(
        "messages_conversation_id_fkey",
        "messages",
        "conversation_threads",
        ["conversation_id"],
        ["id"],
    )
