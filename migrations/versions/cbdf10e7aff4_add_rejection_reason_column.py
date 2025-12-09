"""add_rejection_reason_column

Revision ID: cbdf10e7aff4
Revises: 06c467a6a193
Create Date: 2025-12-01 15:25:39.310160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbdf10e7aff4'
down_revision: Union[str, Sequence[str], None] = '06c467a6a193'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add rejection_reason column to articles table
    op.add_column('articles', sa.Column('rejection_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove rejection_reason column from articles table
    op.drop_column('articles', 'rejection_reason')
