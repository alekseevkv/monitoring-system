"""Update notifications: replace monitoring_task_id with incident_id

Revision ID: f1a2b3c4d5e6
Revises: b3e7f21a9c05
Create Date: 2026-05-23 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "b3e7f21a9c05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_notifications_monitoring_task_id", table_name="notifications")
    op.drop_constraint("notifications_monitoring_task_id_fkey", "notifications", type_="foreignkey")
    op.drop_column("notifications", "monitoring_task_id")
    op.drop_column("notifications", "archived")

    op.add_column(
        "notifications",
        sa.Column("incident_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        "notifications_incident_id_fkey",
        "notifications",
        "incidents",
        ["incident_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_notifications_incident_id", "notifications", ["incident_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_incident_id", table_name="notifications")
    op.drop_constraint("notifications_incident_id_fkey", "notifications", type_="foreignkey")
    op.drop_column("notifications", "incident_id")

    op.add_column(
        "notifications",
        sa.Column("monitoring_task_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "notifications",
        sa.Column("archived", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_foreign_key(
        "notifications_monitoring_task_id_fkey",
        "notifications",
        "monitoring_tasks",
        ["monitoring_task_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_notifications_monitoring_task_id", "notifications", ["monitoring_task_id"]
    )
