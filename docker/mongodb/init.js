// AgentCanvas — MongoDB Initialization Script
// Mounted into mongodb container at /docker-entrypoint-initdb.d/init.js
// Runs automatically on first docker-compose up
// Issues: DB-04 (execution_history), DB-05 (flow_memory), DB-06 (indexes)

// Switch to orchestrator database
// NOTE: MONGO_INITDB_DATABASE env var sets the default DB at container start,
// but we switch explicitly here for clarity and portability.
db = db.getSiblingDB('orchestrator');

// ── Collection: execution_history ────────────────────────────────────────────
// Stores full execution log + memory snapshots per run (one doc per execution).
// flow_id and execution_id are UUID strings matching PostgreSQL primary keys.
db.createCollection('execution_history', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['flow_id', 'execution_id', 'started_at', 'status'],
            properties: {
                flow_id: {
                    bsonType: 'string',
                    description: 'Flow UUID from PostgreSQL flows table'
                },
                execution_id: {
                    bsonType: 'string',
                    description: 'Execution UUID from PostgreSQL flow_executions table'
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
                    // Must match flow_executions.status CHECK constraint in PostgreSQL
                    enum: ['pending', 'running', 'paused_hitl', 'completed', 'failed', 'cancelled'],
                    description: 'Execution status — must stay in sync with PostgreSQL enum'
                },
                execution_log: {
                    bsonType: 'array',
                    description: 'Ordered array of step events for audit trail'
                },
                memory_snapshots: {
                    bsonType: 'array',
                    description: 'Memory state snapshots at each step (for replay/debugging)'
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

// ── Collection: flow_memory ───────────────────────────────────────────────────
// Persists shared memory and per-agent memory across executions of a flow.
// One document per flow — upserted by MemoryService on each execution.
db.createCollection('flow_memory', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['flow_id', 'shared_memory', 'agent_memories', 'metadata'],
            properties: {
                flow_id: {
                    bsonType: 'string',
                    description: 'Unique flow identifier (UUID string from PostgreSQL)'
                },
                flow_name: {
                    bsonType: 'string'
                },
                shared_memory: {
                    bsonType: 'object',
                    description: 'Memory visible to all agents in this flow'
                },
                agent_memories: {
                    bsonType: 'object',
                    description: 'Keyed by agent_id (UUID string); each value is a memory object'
                },
                metadata: {
                    bsonType: 'object',
                    required: ['total_executions', 'created_at'],
                    properties: {
                        total_executions: { bsonType: 'int' },
                        created_at: { bsonType: 'date' },
                        last_updated: { bsonType: 'date' }
                    }
                }
            }
        }
    }
});

// ── Indexes: execution_history ────────────────────────────────────────────────
// Unique on execution_id: one history document per execution
db.execution_history.createIndex({ execution_id: 1 }, { unique: true });
db.execution_history.createIndex({ flow_id: 1, started_at: -1 });
db.execution_history.createIndex({ status: 1 });
// For time-ordered log queries
db.execution_history.createIndex({ 'execution_log.timestamp': 1 });

// ── Indexes: flow_memory ──────────────────────────────────────────────────────
// Unique on flow_id: one memory document per flow
db.flow_memory.createIndex({ flow_id: 1 }, { unique: true });
db.flow_memory.createIndex({ 'metadata.last_updated': -1 });
// Text search index for MemoryService.search() — searches accumulated facts
db.flow_memory.createIndex({ 'shared_memory.accumulated_facts': 'text' });

// ── Sample document ───────────────────────────────────────────────────────────
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

print('AgentCanvas MongoDB initialization complete!');
print('Collections created: execution_history, flow_memory');
print('Indexes created: 7 total (4 on execution_history, 3 on flow_memory)');
