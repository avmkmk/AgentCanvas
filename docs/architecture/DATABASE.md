**Purpose:** Database initialization and migration scripts
**Content Structure:**
```markdown
# Database Migrations Guide
## Initial Setup
### PostgreSQL Schema
**File:** `backend/app/db/migrations/001_initial.sql`
```sql
-- Drop existing tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS agent_analytics CASCADE;
DROP TABLE IF EXISTS hitl_reviews CASCADE;
DROP TABLE IF EXISTS step_executions CASCADE;
DROP TABLE IF EXISTS flow_executions CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS flows CASCADE;
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Flows table
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
-- Agents table
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
-- Flow executions table
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
    CONSTRAINT status_valid CHECK (status IN (
        'pending', 'running', 'paused_hitl', 'completed', 'failed', 'cancelled'
    )),
    CONSTRAINT success_rate_range CHECK (
        success_rate >= 0 AND success_rate <= 100
    )
);
CREATE INDEX idx_executions_flow_id ON flow_executions(flow_id);
CREATE INDEX idx_executions_status ON flow_executions(status);
CREATE INDEX idx_executions_started_at ON flow_executions(started_at DESC);
-- Step executions table
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
    CONSTRAINT status_valid CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'skipped', 'rerunning'
    ))
);
CREATE INDEX idx_step_exec_execution_id ON step_executions(execution_id);
CREATE INDEX idx_step_exec_agent_id ON step_executions(agent_id);
CREATE INDEX idx_step_exec_step_number ON step_executions(execution_id, step_number);
-- HITL reviews table
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
    CONSTRAINT gate_type_valid CHECK (gate_type IN (
        'before', 'after', 'on_demand'
    )),
    CONSTRAINT status_valid CHECK (status IN (
        'pending', 'approved', 'rejected'
    ))
);
CREATE INDEX idx_hitl_execution_id ON hitl_reviews(execution_id);
CREATE INDEX idx_hitl_status ON hitl_reviews(status);
CREATE INDEX idx_hitl_created_at ON hitl_reviews(created_at DESC);
CREATE INDEX idx_hitl_pending ON hitl_reviews(status) WHERE status = 'pending';
-- Agent analytics table (AGGREGATE — one row per agent, no execution_id FK)
-- Updated automatically by the sync_agent_analytics trigger.
CREATE TABLE agent_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE UNIQUE,
    -- UNIQUE enforces one aggregate row per agent
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
-- Agent execution events table (PER-EXECUTION LOG — one row per agent per run)
-- The sync_agent_analytics trigger reads these to keep agent_analytics current.
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
CREATE UNIQUE INDEX idx_agent_exec_events_unique
    ON agent_execution_events(agent_id, execution_id, step_number);
-- Trigger: keep agent_analytics in sync whenever an event is inserted
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
        NEW.agent_id, 1,
        CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'failed'    THEN 1 ELSE 0 END,
        NEW.execution_time_ms, NEW.execution_time_ms, NEW.execution_time_ms,
        NEW.llm_calls, NEW.hitl_reviews, NEW.created_at,
        NOW(), NOW()
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
$$ LANGUAGE plpgsql;
CREATE TRIGGER sync_agent_analytics
    AFTER INSERT ON agent_execution_events
    FOR EACH ROW EXECUTE FUNCTION update_agent_analytics_on_event();
-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
CREATE TRIGGER update_flows_updated_at 
    BEFORE UPDATE ON flows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analytics_updated_at 
    BEFORE UPDATE ON agent_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- Insert sample data for testing (optional)
INSERT INTO flows (name, description, flow_config) VALUES (
    'Sample Flow',
    'A sample flow for testing',
    '{
        "nodes": [
            {"id": "start", "type": "start", "position": {"x": 100, "y": 100}},
            {"id": "end", "type": "end", "position": {"x": 300, "y": 100}}
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "end"}
        ]
    }'::jsonb
);
-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
MongoDB Initialization
File: docker/mongodb/init.js
// Connect to orchestrator database
db = db.getSiblingDB('orchestrator');
// Create collections with validation
db.createCollection('execution_history', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['flow_id', 'execution_id', 'started_at', 'status'],
            properties: {
                flow_id: {
                    bsonType: 'string',
                    description: 'Flow ID from PostgreSQL'
                },
                execution_id: {
                    bsonType: 'string',
                    description: 'Execution ID from PostgreSQL'
                },
                flow_name: {
                    bsonType: 'string'
                },
                started_at: {
                    bsonType: 'date'
                },
                completed_at: {
                    bsonType: 'date'
                },
                status: {
                    enum: ['pending', 'running', 'completed', 'failed'],
                    description: 'Execution status'
                },
                execution_log: {
                    bsonType: 'array',
                    description: 'Detailed execution events'
                },
                memory_snapshots: {
                    bsonType: 'array'
                },
                final_output: {
                    bsonType: 'object'
                },
                metadata: {
                    bsonType: 'object'
                }
            }
        }
    }
});
db.createCollection('flow_memory', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['flow_id', 'shared_memory', 'agent_memories', 'metadata'],
            properties: {
                flow_id: {
                    bsonType: 'string',
                    description: 'Unique flow identifier'
                },
                flow_name: {
                    bsonType: 'string'
                },
                shared_memory: {
                    bsonType: 'object',
                    description: 'Memory shared across all agents'
                },
                agent_memories: {
                    bsonType: 'object',
                    description: 'Agent-specific memories'
                },
                metadata: {
                    bsonType: 'object',
                    required: ['total_executions', 'created_at'],
                    properties: {
                        total_executions: {
                            bsonType: 'int'
                        },
                        created_at: {
                            bsonType: 'date'
                        },
                        last_updated: {
                            bsonType: 'date'
                        }
                    }
                }
            }
        }
    }
});
// Create indexes
db.execution_history.createIndex({ flow_id: 1, started_at: -1 });
db.execution_history.createIndex({ execution_id: 1 }, { unique: true });
db.execution_history.createIndex({ status: 1 });
db.execution_history.createIndex({ 'execution_log.timestamp': 1 });
db.flow_memory.createIndex({ flow_id: 1 }, { unique: true });
db.flow_memory.createIndex({ 'metadata.last_updated': -1 });
db.flow_memory.createIndex({ 'shared_memory.accumulated_facts': 'text' });
// Insert sample document
db.flow_memory.insertOne({
    flow_id: 'sample-flow-id',
    flow_name: 'Sample Flow',
    shared_memory: {
        conversation_history: [],
        accumulated_facts: [],
        key_insights: []
    },
    agent_memories: {},
    metadata: {
        total_executions: 0,
        created_at: new Date(),
        last_updated: new Date()
    }
});
print('MongoDB initialization complete!');
Running Migrations
Option 1: Automatic (via Docker)
Migrations run automatically when starting Docker Compose:
docker-compose up -d
PostgreSQL migrations from backend/app/db/migrations/ are executed on first start.
Option 2: Manual Execution
PostgreSQL:
# Connect to PostgreSQL
docker-compose exec postgres psql -U admin -d orchestrator
# Run migration
\i /docker-entrypoint-initdb.d/001_initial.sql
# Verify tables
\dt
# Exit
\q
MongoDB:
# Connect to MongoDB
docker-compose exec mongodb mongosh -u admin -p admin123
# Switch to database
use orchestrator
# Run initialization
load('/docker-entrypoint-initdb.d/init.js')
# Verify collections
show collections
# Exit
exit
Option 3: Using Alembic (Advanced)
For production, use Alembic for version-controlled migrations:
Install Alembic:
pip install alembic
Initialize:
cd backend
alembic init alembic
Create migration:
alembic revision -m "initial schema"
Apply migration:
alembic upgrade head
Verification
# Check PostgreSQL tables
docker-compose exec postgres psql -U admin -d orchestrator -c "\dt"
# Check MongoDB collections
docker-compose exec mongodb mongosh -u admin -p admin123 \
  --eval "db.getSiblingDB('orchestrator').getCollectionNames()"
# Check data
docker-compose exec postgres psql -U admin -d orchestrator \
  -c "SELECT COUNT(*) FROM flows;"
Expected output:
 count 
-------
     1
(1 row)
Backup & Restore
Backup
PostgreSQL:
docker-compose exec postgres pg_dump -U admin orchestrator > backup.sql
MongoDB:
docker-compose exec mongodb mongodump --username admin --password admin123 \
  --db orchestrator --out /backup
Restore
PostgreSQL:
docker-compose exec -T postgres psql -U admin orchestrator < backup.sql
MongoDB:
docker-compose exec mongodb mongorestore --username admin --password admin123 \
  --db orchestrator /backup/orchestrator
Common Migration Issues
Issue: Migration already applied
Solution: Drop and recreate database
```bash
docker-compose down -v
docker-compose up -d
Issue: Permission denied
Solution: Grant permissions
```sql
GRANT ALL PRIVILEGES ON DATABASE orchestrator TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
Issue: MongoDB validation error
Solution: Drop collection and recreate
```javascript
db.execution_history.drop();
// Re-run init.js