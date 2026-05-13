"""Fix merge conflict

Revision ID: 884b3b52a7b7
Revises: 62f288a99201, c7f3e2a1b9d4
Create Date: 2026-05-13 21:30:24.888734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '884b3b52a7b7'
down_revision: Union[str, Sequence[str], None] = ('62f288a99201', 'c7f3e2a1b9d4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
