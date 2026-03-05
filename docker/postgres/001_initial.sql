-- AgentCanvas — PostgreSQL Initial Schema
-- Mounted into postgres container at /docker-entrypoint-initdb.d/001_initial.sql
-- Runs automatically on first docker-compose up
-- Issues: DB-01 (flows, agents, flow_executions, step_executions)
--         DB-02 (hitl_reviews, agent_analytics, agent_execution_events)
--         DB-03 (triggers: sync_agent_analytics, update_updated_at_column)

-- Drop tables in reverse dependency order (safe for clean reinstall)
DROP TABLE IF EXISTS agent_execution_events CASCADE;
DROP TABLE IF EXISTS agent_analytics CASCADE;
DROP TABLE IF EXISTS hitl_reviews CASCADE;
DROP TABLE IF EXISTS step_executions CASCADE;
DROP TABLE IF EXISTS flow_executions CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS flows CASCADE;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Flows table ───────────────────────────────────────────────────────────────
CREATE TABLE flows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    flow_config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),
    CONSTRAINT flow_name_not_empty CHECK (name <> '')
);
CREATE INDEX idx_flows_created_at ON flows(created_at DESC);
CREATE INDEX idx_flows_created_by ON flows(created_by);
CREATE INDEX idx_flows_name ON flows USING GIN (to_tsvector('english', name));

-- ── Agents table ──────────────────────────────────────────────────────────────
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID REFERENCES flows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    system_prompt TEXT NOT NULL,
    role VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT agent_name_not_empty CHECK (name <> ''),
    CONSTRAINT agent_type_valid CHECK (type IN ('conversational')),
    CONSTRAINT agent_role_valid CHECK (role IN (
        'researcher', 'analyst', 'writer', 'critic', 'planner', 'custom'
    ))
);
CREATE INDEX idx_agents_flow_id ON agents(flow_id);
CREATE INDEX idx_agents_type ON agents(type);
CREATE INDEX idx_agents_role ON agents(role);

-- ── Flow executions table ─────────────────────────────────────────────────────
CREATE TABLE flow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID REFERENCES flows(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    total_steps INTEGER NOT NULL,
    completed_steps INTEGER DEFAULT 0,
    current_step INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    error_message TEXT,
    execution_metadata JSONB,
    CONSTRAINT execution_status_valid CHECK (status IN (
        'pending', 'running', 'paused_hitl', 'completed', 'failed', 'cancelled'
    )),
    -- NULL allowed (not yet calculated); when set must be 0–100
    CONSTRAINT success_rate_range CHECK (
        success_rate IS NULL OR (success_rate >= 0 AND success_rate <= 100)
    )
);
CREATE INDEX idx_executions_flow_id ON flow_executions(flow_id);
CREATE INDEX idx_executions_status ON flow_executions(status);
CREATE INDEX idx_executions_started_at ON flow_executions(started_at DESC);

-- ── Step executions table ─────────────────────────────────────────────────────
CREATE TABLE step_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES flow_executions(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id),
    step_number INTEGER NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_ms INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    CONSTRAINT step_status_valid CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'skipped', 'rerunning'
    ))
);
CREATE INDEX idx_step_exec_execution_id ON step_executions(execution_id);
CREATE INDEX idx_step_exec_agent_id ON step_executions(agent_id);
CREATE INDEX idx_step_exec_step_number ON step_executions(execution_id, step_number);

-- ── HITL reviews table ────────────────────────────────────────────────────────
CREATE TABLE hitl_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES flow_executions(id),
    step_id UUID REFERENCES step_executions(id),
    agent_id UUID REFERENCES agents(id),
    gate_type VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    output_to_review JSONB NOT NULL,
    reviewer_comments TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(255),
    CONSTRAINT hitl_gate_type_valid CHECK (gate_type IN (
        'before', 'after', 'on_demand'
    )),
    CONSTRAINT hitl_status_valid CHECK (status IN (
        'pending', 'approved', 'rejected'
    ))
);
CREATE INDEX idx_hitl_execution_id ON hitl_reviews(execution_id);
CREATE INDEX idx_hitl_status ON hitl_reviews(status);
CREATE INDEX idx_hitl_created_at ON hitl_reviews(created_at DESC);
-- Partial index: fast lookup of pending reviews (HITL queue page)
CREATE INDEX idx_hitl_pending ON hitl_reviews(status) WHERE status = 'pending';

-- ── Agent analytics table ─────────────────────────────────────────────────────
-- AGGREGATE: one row per agent, updated by sync_agent_analytics trigger.
-- Do NOT insert/update directly from application code.
CREATE TABLE agent_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE UNIQUE,
    total_runs INTEGER DEFAULT 0,
    successful_runs INTEGER DEFAULT 0,
    failed_runs INTEGER DEFAULT 0,
    avg_execution_time_ms DECIMAL(10,2) DEFAULT 0,
    min_execution_time_ms INTEGER,
    max_execution_time_ms INTEGER,
    total_llm_calls INTEGER DEFAULT 0,
    total_hitl_reviews INTEGER DEFAULT 0,
    last_run_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_analytics_agent_id ON agent_analytics(agent_id);

-- ── Agent execution events table ──────────────────────────────────────────────
-- PER-EXECUTION LOG: one row per agent per execution step.
-- Inserting here fires the sync_agent_analytics trigger.
CREATE TABLE agent_execution_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    execution_id UUID REFERENCES flow_executions(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    execution_time_ms INTEGER,
    llm_calls INTEGER DEFAULT 1,
    hitl_reviews INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT agent_exec_status_valid CHECK (status IN ('completed', 'failed'))
);
CREATE INDEX idx_agent_exec_events_agent_id ON agent_execution_events(agent_id);
CREATE INDEX idx_agent_exec_events_execution_id ON agent_execution_events(execution_id);
-- Unique: one event per (agent, execution, step) — prevents double-counting in analytics
CREATE UNIQUE INDEX idx_agent_exec_events_unique
    ON agent_execution_events(agent_id, execution_id, step_number);

-- ── Trigger: sync_agent_analytics ────────────────────────────────────────────
-- Fires AFTER INSERT on agent_execution_events.
-- Upserts the aggregate row in agent_analytics using a running average formula.
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
        COALESCE(NEW.execution_time_ms, 0),
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
        -- Running average: (old_avg * old_count + new_value) / new_count
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
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_agent_analytics
    AFTER INSERT ON agent_execution_events
    FOR EACH ROW EXECUTE FUNCTION update_agent_analytics_on_event();

-- ── Trigger: update_updated_at_column ────────────────────────────────────────
-- Fires BEFORE UPDATE on flows and agent_analytics.
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_flows_updated_at
    BEFORE UPDATE ON flows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analytics_updated_at
    BEFORE UPDATE ON agent_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── Sample data (smoke test) ──────────────────────────────────────────────────
INSERT INTO flows (name, description, flow_config) VALUES (
    'Sample Flow',
    'A sample flow for smoke testing',
    '{
        "nodes": [
            {"id": "start", "type": "start", "position": {"x": 100, "y": 100}, "data": {}},
            {"id": "end",   "type": "end",   "position": {"x": 300, "y": 100}, "data": {}}
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "end"}
        ]
    }'::jsonb
);

-- ── Permissions ───────────────────────────────────────────────────────────────
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO admin;
