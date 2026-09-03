"""initial schema - files table

Revision ID: 14f64fbd33be
Revises: 
Create Date: 2026-09-02 23:09:43.744093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '14f64fbd33be'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create files table."""
    op.create_table('files',
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('file_type', sa.String(length=20), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('caption', sa.Text(), nullable=True),
    sa.Column('original_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('original_message_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop files table."""
    op.drop_table('files')
