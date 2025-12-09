"""add_pending_review_to_article_status

Revision ID: b2bf36751ced
Revises: cbdf10e7aff4
Create Date: 2025-12-01 15:43:41.486337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2bf36751ced'
down_revision: Union[str, Sequence[str], None] = 'cbdf10e7aff4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
