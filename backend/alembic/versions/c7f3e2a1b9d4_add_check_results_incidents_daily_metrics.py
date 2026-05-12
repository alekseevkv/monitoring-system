"""Add check_results, incidents, daily_metrics tables

Revision ID: c7f3e2a1b9d4
Revises: a35f8a4bbfc9
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c7f3e2a1b9d4"
down_revision: Union[str, Sequence[str], None] = "a35f8a4bbfc9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "check_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("monitoring_task_id", sa.Integer(), nullable=False),
        sa.Column("is_success", sa.Boolean(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_time_s", sa.Float(), nullable=True),
        sa.Column("response_headers", sa.JSON(), nullable=True),
        sa.Column("response_body_preview", sa.String(length=2048), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["monitoring_task_id"],
            ["monitoring_tasks.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_check_results_task_created",
        "check_results",
        ["monitoring_task_id", "created_at"],
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("monitoring_task_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("открыт", "закрыт", name="incidentstatus"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("started_by_check_id", sa.Integer(), nullable=True),
        sa.Column("resolved_by_check_id", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["monitoring_task_id"],
            ["monitoring_tasks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["started_by_check_id"],
            ["check_results.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["resolved_by_check_id"],
            ["check_results.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_incidents_task_id", "incidents", ["monitoring_task_id"]
    )

    op.create_table(
        "daily_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("monitoring_task_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_checks", sa.Integer(), nullable=False),
        sa.Column("successful_checks", sa.Integer(), nullable=False),
        sa.Column("failed_checks", sa.Integer(), nullable=False),
        sa.Column("avg_response_time_s", sa.Float(), nullable=True),
        sa.Column("min_response_time_s", sa.Float(), nullable=True),
        sa.Column("max_response_time_s", sa.Float(), nullable=True),
        sa.Column("uptime_percentage", sa.Float(), nullable=False),
        sa.Column("sla_met", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["monitoring_task_id"],
            ["monitoring_tasks.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "monitoring_task_id", "date", name="uq_daily_metric_task_date"
        ),
    )
    op.create_index(
        "ix_daily_metrics_task_id", "daily_metrics", ["monitoring_task_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_daily_metrics_task_id", table_name="daily_metrics")
    op.drop_table("daily_metrics")

    op.drop_index("ix_incidents_task_id", table_name="incidents")
    op.drop_table("incidents")
    op.execute("DROP TYPE IF EXISTS incidentstatus")

    op.drop_index("ix_check_results_task_created", table_name="check_results")
    op.drop_table("check_results")
