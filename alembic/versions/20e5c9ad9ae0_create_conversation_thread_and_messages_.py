"""create conversation_thread and messages tables

Revision ID: 20e5c9ad9ae0
Revises:
Create Date: 2026-01-02 16:43:21.786871

"""

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20e5c9ad9ae0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type for message roles
    message_role_enum = postgresql.ENUM(
        "user", "assistant", "system", name="message_role"
    )
    message_role_enum.create(op.get_bind(), checkfirst=True)

    # Create conversation_threads table
    op.create_table(
        "conversation_threads",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            index=True,
        ),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create messages table
    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("conversation_threads.id"),
            nullable=False,
        ),
        sa.Column(
            "role",
             postgresql.ENUM(
                "user", "assistant", "system", 
                name="message_role", 
                create_type=False
            ),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("sources", postgresql.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop messages table first (foreign key dependency)
    op.drop_table("messages")

    # Drop conversation_threads table
    op.drop_table("conversation_threads")

    # Drop enum type
    message_role_enum = postgresql.ENUM(
        "user", "assistant", "system", name="message_role"
    )
    message_role_enum.drop(op.get_bind())
