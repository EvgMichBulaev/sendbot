"""add_expires_at_to_files

Revision ID: 617daa1347cb
Revises: 7592d4380f21
Create Date: 2026-09-02 23:56:04.680240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '617daa1347cb'
down_revision: Union[str, Sequence[str], None] = '7592d4380f21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('files', sa.Column('expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('files', 'expires_at')
