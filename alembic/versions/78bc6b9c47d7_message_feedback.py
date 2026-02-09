"""message feedback

Revision ID: 78bc6b9c47d7
Revises: 14292a5ca296
Create Date: 2026-02-09 12:44:32.238315

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "78bc6b9c47d7"
down_revision: Union[str, Sequence[str], None] = "14292a5ca296"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create ENUM type (Postgres-specific)
    feedback_reaction_enum = postgresql.ENUM(
        "like",
        "dislike",
        name="message_feedback_reaction",
    )
    feedback_reaction_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create table
    op.create_table(
        "message_feedback",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        ),
        sa.Column(
            "thread_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversation_threads.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reaction",
            postgresql.ENUM(
                "like", "dislike", name="message_feedback_reaction", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "thread_id",
            "message_id",
            name="uq_thread_message_feedback",
        ),
        if_not_exists=True,
    )

    # 3. Indexes (important for performance)
    op.create_index(
        "ix_message_feedback_id",
        "message_feedback",
        ["id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_message_feedback_thread_id",
        "message_feedback",
        ["thread_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_message_feedback_message_id",
        "message_feedback",
        ["message_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 1. Drop indexes
    op.drop_index(
        "ix_message_feedback_id",
        table_name="message_feedback",
        if_exists=True,
    )
    op.drop_index(
        "ix_message_feedback_thread_id",
        table_name="message_feedback",
        if_exists=True,
    )
    op.drop_index(
        "ix_message_feedback_message_id",
        table_name="message_feedback",
        if_exists=True,
    )

    # 2. Drop table
    op.drop_table("message_feedback", if_exists=True)

    # 3. Drop ENUM type
    feedback_reaction_enum = postgresql.ENUM(
        "like",
        "dislike",
        name="message_feedback_reaction",
    )
    feedback_reaction_enum.drop(op.get_bind(), checkfirst=True)
