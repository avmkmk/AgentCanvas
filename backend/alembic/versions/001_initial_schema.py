"""Initial schema — all M1 tables, indexes, triggers, and functions.

Revision ID: 001
Revises: None
Create Date: 2026-03-05

Matches backend/app/db/migrations/001_initial.sql exactly, with the
addition of flows.is_active (BOOLEAN NOT NULL DEFAULT TRUE).

Tables created (in dependency order):
  flows → agents → flow_executions → step_executions →
  hitl_reviews → agent_execution_events → agent_analytics

Triggers:
  update_updated_at_column() — BEFORE UPDATE on flows, agent_analytics
  update_agent_analytics_on_event() — AFTER INSERT on agent_execution_events
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers used by Alembic
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Extension ────────────────────────────────────────────────────────────
    # uuid-ossp provides uuid_generate_v4() used as default for all PK columns
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ── flows ─────────────────────────────────────────────────────────────────
    op.create_table(
        "flows",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("flow_config", postgresql.JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(255), nullable=True),
        # is_active: soft-delete flag added in DB-08 / BA-02
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("TRUE"),
        ),
        sa.CheckConstraint("name <> ''", name="flow_name_not_empty"),
    )
    op.create_index(
        "idx_flows_created_at",
        "flows",
        [sa.text("created_at DESC")],
    )
    op.create_index("idx_flows_created_by", "flows", ["created_by"])
    # GIN index for full-text search on flow name
    op.execute(
        "CREATE INDEX idx_flows_name ON flows "
        "USING GIN (to_tsvector('english', name))"
    )

    # ── agents ────────────────────────────────────────────────────────────────
    op.create_table(
        "agents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "flow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("flows.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("system_prompt", sa.Text, nullable=False),
        sa.Column("role", sa.String(100), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.CheckConstraint("name <> ''", name="agent_name_not_empty"),
        sa.CheckConstraint(
            "type IN ('conversational')",
            name="agent_type_valid",
        ),
        sa.CheckConstraint(
            "role IN ('researcher','analyst','writer','critic','planner','custom')",
            name="agent_role_valid",
        ),
    )
    op.create_index("idx_agents_flow_id", "agents", ["flow_id"])
    op.create_index("idx_agents_type", "agents", ["type"])
    op.create_index("idx_agents_role", "agents", ["role"])

    # ── flow_executions ───────────────────────────────────────────────────────
    op.create_table(
        "flow_executions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "flow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("flows.id"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column(
            "started_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("total_steps", sa.Integer, nullable=False),
        sa.Column(
            "completed_steps",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "current_step",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("success_rate", sa.Numeric(5, 2), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("execution_metadata", postgresql.JSONB, nullable=True),
        sa.CheckConstraint(
            "status IN ('pending','running','paused_hitl','completed','failed','cancelled')",
            name="status_valid",
        ),
        sa.CheckConstraint(
            "success_rate >= 0 AND success_rate <= 100",
            name="success_rate_range",
        ),
    )
    op.create_index("idx_executions_flow_id", "flow_executions", ["flow_id"])
    op.create_index("idx_executions_status", "flow_executions", ["status"])
    op.create_index(
        "idx_executions_started_at",
        "flow_executions",
        [sa.text("started_at DESC")],
    )

    # ── step_executions ───────────────────────────────────────────────────────
    op.create_table(
        "step_executions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("flow_executions.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id"),
            nullable=True,
        ),
        sa.Column("step_number", sa.Integer, nullable=False),
        sa.Column("input_data", postgresql.JSONB, nullable=True),
        sa.Column("output_data", postgresql.JSONB, nullable=True),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("execution_time_ms", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "retry_count",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.CheckConstraint(
            "status IN ('pending','running','completed','failed','skipped','rerunning')",
            name="status_valid",
        ),
    )
    op.create_index(
        "idx_step_exec_execution_id", "step_executions", ["execution_id"]
    )
    op.create_index("idx_step_exec_agent_id", "step_executions", ["agent_id"])
    op.create_index(
        "idx_step_exec_step_number",
        "step_executions",
        ["execution_id", "step_number"],
    )

    # ── hitl_reviews ──────────────────────────────────────────────────────────
    op.create_table(
        "hitl_reviews",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("flow_executions.id"),
            nullable=True,
        ),
        sa.Column(
            "step_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("step_executions.id"),
            nullable=True,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id"),
            nullable=True,
        ),
        sa.Column("gate_type", sa.String(20), nullable=False),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("output_to_review", postgresql.JSONB, nullable=False),
        sa.Column("reviewer_comments", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.CheckConstraint(
            "gate_type IN ('before','after','on_demand')",
            name="gate_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="status_valid",
        ),
    )
    op.create_index("idx_hitl_execution_id", "hitl_reviews", ["execution_id"])
    op.create_index("idx_hitl_status", "hitl_reviews", ["status"])
    op.create_index(
        "idx_hitl_created_at",
        "hitl_reviews",
        [sa.text("created_at DESC")],
    )
    # Partial index — queries for pending reviews are the hot path
    op.execute(
        "CREATE INDEX idx_hitl_pending ON hitl_reviews (status) "
        "WHERE status = 'pending'"
    )

    # ── agent_execution_events ─────────────────────────────────────────────────
    op.create_table(
        "agent_execution_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("flow_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_number", sa.Integer, nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("execution_time_ms", sa.Integer, nullable=True),
        sa.Column(
            "llm_calls",
            sa.Integer,
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "hitl_reviews",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('completed','failed')",
            name="agent_exec_status_valid",
        ),
    )
    op.create_index(
        "idx_agent_exec_events_agent_id", "agent_execution_events", ["agent_id"]
    )
    op.create_index(
        "idx_agent_exec_events_execution_id",
        "agent_execution_events",
        ["execution_id"],
    )
    # UNIQUE prevents double-counting if a retry accidentally re-inserts
    op.create_index(
        "idx_agent_exec_events_unique",
        "agent_execution_events",
        ["agent_id", "execution_id", "step_number"],
        unique=True,
    )

    # ── agent_analytics ───────────────────────────────────────────────────────
    # AGGREGATE table — written only by the sync_agent_analytics DB trigger.
    # Application code must NOT INSERT or UPDATE this table directly.
    op.create_table(
        "agent_analytics",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "total_runs",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "successful_runs",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "failed_runs",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "avg_execution_time_ms",
            sa.Numeric(10, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("min_execution_time_ms", sa.Integer, nullable=True),
        sa.Column("max_execution_time_ms", sa.Integer, nullable=True),
        sa.Column(
            "total_llm_calls",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "total_hitl_reviews",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("last_run_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.create_index(
        "idx_analytics_agent_id", "agent_analytics", ["agent_id"]
    )

    # ── Trigger functions ─────────────────────────────────────────────────────

    # updated_at trigger — keeps flows.updated_at and agent_analytics.updated_at
    # in sync on every UPDATE without relying on the application layer.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_flows_updated_at
            BEFORE UPDATE ON flows
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_analytics_updated_at
            BEFORE UPDATE ON agent_analytics
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """
    )

    # sync_agent_analytics trigger — upserts the aggregate row in agent_analytics
    # whenever a new event is inserted into agent_execution_events.
    # Application code must NEVER write to agent_analytics directly.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_agent_analytics_on_event()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO agent_analytics (
                agent_id, total_runs, successful_runs, failed_runs,
                avg_execution_time_ms, min_execution_time_ms, max_execution_time_ms,
                total_llm_calls, total_hitl_reviews, last_run_at,
                created_at, updated_at
            )
            VALUES (
                NEW.agent_id,
                1,
                CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END,
                CASE WHEN NEW.status = 'failed'    THEN 1 ELSE 0 END,
                NEW.execution_time_ms,
                NEW.execution_time_ms,
                NEW.execution_time_ms,
                NEW.llm_calls,
                NEW.hitl_reviews,
                NEW.created_at,
                NOW(),
                NOW()
            )
            ON CONFLICT (agent_id) DO UPDATE SET
                total_runs            = agent_analytics.total_runs + 1,
                successful_runs       = agent_analytics.successful_runs +
                                            CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END,
                failed_runs           = agent_analytics.failed_runs +
                                            CASE WHEN NEW.status = 'failed'    THEN 1 ELSE 0 END,
                avg_execution_time_ms = (
                                            agent_analytics.avg_execution_time_ms
                                            * agent_analytics.total_runs
                                            + COALESCE(NEW.execution_time_ms, 0)
                                        ) / (agent_analytics.total_runs + 1),
                min_execution_time_ms = LEAST(
                                            agent_analytics.min_execution_time_ms,
                                            NEW.execution_time_ms
                                        ),
                max_execution_time_ms = GREATEST(
                                            agent_analytics.max_execution_time_ms,
                                            NEW.execution_time_ms
                                        ),
                total_llm_calls       = agent_analytics.total_llm_calls   + NEW.llm_calls,
                total_hitl_reviews    = agent_analytics.total_hitl_reviews + NEW.hitl_reviews,
                last_run_at           = NEW.created_at,
                updated_at            = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER sync_agent_analytics
            AFTER INSERT ON agent_execution_events
            FOR EACH ROW EXECUTE FUNCTION update_agent_analytics_on_event()
        """
    )


def downgrade() -> None:
    # ── Drop triggers first (depend on tables) ────────────────────────────────
    op.execute("DROP TRIGGER IF EXISTS sync_agent_analytics ON agent_execution_events")
    op.execute("DROP TRIGGER IF EXISTS update_analytics_updated_at ON agent_analytics")
    op.execute("DROP TRIGGER IF EXISTS update_flows_updated_at ON flows")

    # ── Drop trigger functions ─────────────────────────────────────────────────
    op.execute("DROP FUNCTION IF EXISTS update_agent_analytics_on_event()")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # ── Drop tables in reverse dependency order ────────────────────────────────
    op.drop_table("agent_analytics")
    op.drop_table("agent_execution_events")
    op.drop_table("hitl_reviews")
    op.drop_table("step_executions")
    op.drop_table("flow_executions")
    op.drop_table("agents")
    op.drop_table("flows")
