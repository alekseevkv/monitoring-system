"""Create notifications table

Revision ID: b3e7f21a9c05
Revises: ca933d1c249d
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3e7f21a9c05"
down_revision: Union[str, None] = "e5a2d1b9c374"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("monitoring_task_id", sa.Integer(), nullable=False),
        sa.Column("recipient_email", sa.String(255), nullable=False),
        sa.Column("trigger_type", sa.String(50), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="pending"
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column(
            "archived", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["monitoring_task_id"],
            ["monitoring_tasks.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_notifications_monitoring_task_id", "notifications", ["monitoring_task_id"]
    )
    op.create_index(
        "ix_notifications_sent_at", "notifications", ["sent_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_sent_at", table_name="notifications")
    op.drop_index("ix_notifications_monitoring_task_id", table_name="notifications")
    op.drop_table("notifications")
