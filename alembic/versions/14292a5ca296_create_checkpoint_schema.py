"""create_checkpoint_schema

Revision ID: 14292a5ca296
Revises: cccebd9922d6
Create Date: 2026-02-03 16:55:35.519427

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "14292a5ca296"
down_revision: Union[str, Sequence[str], None] = "cccebd9922d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS checkpoint")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SCHEMA IF EXISTS checkpoint CASCADE")
