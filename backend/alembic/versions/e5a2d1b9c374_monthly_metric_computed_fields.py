"""monthly_metric: rename date to metric_date, make total_checks/success_rate/sla_month computed

Revision ID: e5a2d1b9c374
Revises: b1ea2a2ef425
Create Date: 2026-05-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5a2d1b9c374"
down_revision: Union[str, Sequence[str], None] = "b1ea2a2ef425"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("monthly_metrics", "date", new_column_name="metric_date")

    op.drop_column("monthly_metrics", "total_checks")
    op.drop_column("monthly_metrics", "success_rate")
    op.drop_column("monthly_metrics", "sla_month")

    op.add_column(
        "monthly_metrics",
        sa.Column(
            "total_checks",
            sa.Integer(),
            sa.Computed("successful_checks + failed_checks", persisted=True),
        ),
    )
    op.add_column(
        "monthly_metrics",
        sa.Column(
            "success_rate",
            sa.Float(),
            sa.Computed(
                "CASE WHEN successful_checks + failed_checks = 0 THEN 100.0 "
                "ELSE successful_checks * 100.0 / (successful_checks + failed_checks) END",
                persisted=True,
            ),
        ),
    )
    op.add_column(
        "monthly_metrics",
        sa.Column(
            "sla_month",
            sa.Float(),
            sa.Computed(
                "CASE WHEN total_uptime_seconds IS NULL OR total_downtime_seconds IS NULL THEN NULL "
                "WHEN total_uptime_seconds + total_downtime_seconds = 0 THEN 100.0 "
                "ELSE total_uptime_seconds * 100.0 / (total_uptime_seconds + total_downtime_seconds) END",
                persisted=True,
            ),
        ),
    )


def downgrade() -> None:
    op.drop_column("monthly_metrics", "sla_month")
    op.drop_column("monthly_metrics", "success_rate")
    op.drop_column("monthly_metrics", "total_checks")

    op.add_column("monthly_metrics", sa.Column("total_checks", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("monthly_metrics", sa.Column("success_rate", sa.Float(), nullable=False, server_default="100.0"))
    op.add_column("monthly_metrics", sa.Column("sla_month", sa.Float(), nullable=True))

    op.alter_column("monthly_metrics", "metric_date", new_column_name="date")
