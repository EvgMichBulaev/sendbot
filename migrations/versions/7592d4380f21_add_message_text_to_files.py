"""add_message_text_to_files

Revision ID: 7592d4380f21
Revises: 14f64fbd33be
Create Date: 2026-09-02 23:25:29.805512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7592d4380f21'
down_revision: Union[str, Sequence[str], None] = '14f64fbd33be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('files', sa.Column('message_text', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('files', 'message_text')
