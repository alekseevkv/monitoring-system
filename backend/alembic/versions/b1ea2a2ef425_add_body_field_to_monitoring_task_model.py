"""Add body field to monitoring task model

Revision ID: b1ea2a2ef425
Revises: 884b3b52a7b7
Create Date: 2026-05-15 19:29:40.506162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1ea2a2ef425'
down_revision: Union[str, Sequence[str], None] = '884b3b52a7b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('monitoring_tasks', sa.Column('body', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('monitoring_tasks', 'body')
