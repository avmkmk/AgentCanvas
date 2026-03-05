🎯 MULTI-AGENT ORCHESTRATOR - COMPLETE IMPLEMENTATION PLAN
Version: 1.0  
Date: March 2, 2026  
Timeline: 14 Days (56 hours total @ 4 hours/day)  
Status: Ready for Implementation
---
📋 TABLE OF CONTENTS
1. Executive Summary (#1-executive-summary)
2. Project Overview (#2-project-overview)
3. System Architecture (#3-system-architecture)
4. Technology Stack (#4-technology-stack)
5. Database Design (#5-database-design)
6. API Specification (#6-api-specification)
7. Frontend Design (#7-frontend-design)
8. Backend Design (#8-backend-design)
9. Implementation Timeline (#9-implementation-timeline)
10. Deployment Strategy (#10-deployment-strategy)
11. Testing Strategy (#11-testing-strategy)
12. Security Considerations (#12-security-considerations)
---
1. EXECUTIVE SUMMARY
1.1 Project Vision
Build a drag-and-drop multi-agent orchestrator that allows users to:
- Visually design agent workflows
- Configure agents with dynamic system prompts
- Execute sequential agent flows
- Implement human-in-the-loop gates
- Manage comprehensive memory and context
- Track analytics and performance
1.2 Key Features (MVP)
✅ Drag-and-drop canvas (React Flow)  
✅ Agent configuration panel (system prompts, roles, model selection)  
✅ Sequential flow execution  
✅ HITL gates (before, after, on-demand)  
✅ HITL review queue with approval/rejection  
✅ Shared, long-term, persistent memory management  
✅ Save/load flows  
✅ Execution logs and monitoring  
✅ Analytics (success/failure rates, agent performance)  
✅ Background execution  
✅ Pre-built agent templates  
1.3 Out of Scope (Phase 2)
❌ Parallel flow execution  
❌ Vector database integration  
❌ Multi-modal agents  
❌ Plugin system  
❌ Token usage tracking  
❌ Memory search UI  
1.4 Success Criteria
At the end of 14 days, the system should:
1. Allow creating a 3-agent sequential flow via drag-and-drop
2. Execute the flow with HITL gates working correctly
3. Persist memory across multiple executions
4. Display analytics showing success rates and agent performance
5. Support save/load functionality for flows
---
2. PROJECT OVERVIEW
2.1 Problem Statement
Current agentic AI frameworks lack:
- Intuitive visual interfaces for non-technical users
- Comprehensive memory management across executions
- Built-in human oversight mechanisms
- Detailed analytics and observability
2.2 Solution
A hybrid approach combining:
- Custom orchestration engine for full control
- Swarms-inspired patterns for agent abstractions
- Microsoft Agent Framework patterns for memory management
- LiteLLM integration for unified model access
- React Flow for intuitive visual design
2.3 Target Users
- AI/ML engineers building agentic systems
- Researchers experimenting with multi-agent workflows
- Product teams prototyping AI-powered features
- Organizations requiring HITL oversight
2.4 Technical Constraints
- Timeline: 14 days (56 hours)
- Deployment: Local Docker initially
- Authentication: Simple API keys
- Database: Single database setup for MVP
- LLM Access: DialKey proxy (rate-limited)
---
3. SYSTEM ARCHITECTURE
3.1 High-Level Architecture Diagram
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                            │
│                  (React + TypeScript + Vite)                 │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  Flow Canvas   │  │  Agent Config  │  │  HITL Review  │ │
│  │  (React Flow)  │  │  Panel         │  │  Queue/Modal  │ │
│  │                │  │                │  │               │ │
│  │  - Drag/Drop   │  │  - Prompts     │  │  - Pending    │ │
│  │  - Nodes/Edges │  │  - Roles       │  │  - Approve    │ │
│  │  - Validation  │  │  - Models      │  │  - Reject     │ │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  Flow Manager  │  │  Execution     │  │  Analytics    │ │
│  │                │  │  Viewer        │  │  Dashboard    │ │
│  │  - Save        │  │                │  │               │ │
│  │  - Load        │  │  - Progress    │  │  - Metrics    │ │
│  │  - List        │  │  - Logs        │  │  - Charts     │ │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │
                    REST API + WebSocket
                           │
┌──────────────────────────┴───────────────────────────────────┐
│                    BACKEND LAYER                              │
│                   (FastAPI + Python)                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           ORCHESTRATION ENGINE                           │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │  Flow        │  │  Agent       │  │  HITL        │ │ │
│  │  │  Executor    │  │  Manager     │  │  Manager     │ │ │
│  │  │              │  │              │  │              │ │ │
│  │  │  - Sequential│  │  - Factory   │  │  - Queue     │ │ │
│  │  │  - Steps     │  │  - Lifecycle │  │  - Approval  │ │ │
│  │  │  - Context   │  │  - Templates │  │  - Rejection │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           MEMORY & CONTEXT LAYER                         │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │  Memory      │  │  Context     │  │  Shared      │ │ │
│  │  │  Manager     │  │  Manager     │  │  Memory      │ │ │
│  │  │              │  │              │  │              │ │ │
│  │  │  - Short-term│  │  - Builder   │  │  - Redis     │ │ │
│  │  │  - Long-term │  │  - Formatter │  │  - Session   │ │ │
│  │  │  - Persistent│  │  - Injection │  │  - Cache     │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           SERVICES LAYER                                 │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │  LLM Service │  │  Analytics   │  │  Logger      │ │ │
│  │  │  (LiteLLM)   │  │  Service     │  │  Service     │ │ │
│  │  │              │  │              │  │              │ │ │
│  │  │  - DialKey   │  │  - Metrics   │  │  - MongoDB   │ │ │
│  │  │  - Models    │  │  - Aggreg.   │  │  - Detailed  │ │ │
│  │  │  - Retries   │  │  - Stats     │  │  - Structured│ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────────┐
│                    DATA LAYER                                 │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │  MongoDB     │  │  Redis       │      │
│  │              │  │              │  │              │      │
│  │  - Flows     │  │  - Execution │  │  - Sessions  │      │
│  │  - Agents    │  │    History   │  │  - Queue     │      │
│  │  - Executions│  │  - Memory    │  │  - Cache     │      │
│  │  - HITL      │  │  - Logs      │  │  - PubSub    │      │
│  │  - Analytics │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
3.2 Component Interactions
User Action: Create & Execute Flow
════════════════════════════════════
1. USER CREATES FLOW
   ↓
   Frontend: FlowCanvas
   - User drags "Researcher" agent to canvas
   - User drags "Analyst" agent to canvas  
   - User connects Researcher → Analyst
   - User configures each agent:
     * System prompt
     * Role (from templates)
     * Model (GPT-4o, Claude, etc.)
     * HITL gates (after execution for Researcher)
   ↓
   Frontend: SaveFlowDialog
   - POST /api/v1/flows
   - Flow saved to PostgreSQL
   ↓
   
2. USER EXECUTES FLOW
   ↓
   Frontend: ExecutionViewer
   - POST /api/v1/executions/start
   - Execution starts in background
   - WebSocket connection established
   ↓
   
3. BACKEND ORCHESTRATION
   ↓
   FlowExecutor.execute_sequential()
   
   Step 1: Researcher Agent
   ├─ AgentManager.get_agent("researcher")
   ├─ MemoryManager.get_context_for_agent("researcher")
   │  └─ Returns: {} (empty on first run)
   ├─ LLMService.generate(prompt + context)
   │  └─ LiteLLM → DialKey → GPT-4o
   ├─ Agent Output: "Research findings on AI trends..."
   ├─ MemoryManager.add_to_memory()
   │  ├─ Redis: Add to shared memory
   │  └─ MongoDB: Persist to flow_memory collection
   └─ HITL Gate (after) triggered
      ├─ HITLManager.create_review()
      │  ├─ Save review to PostgreSQL
      │  └─ Add to Redis queue
      ├─ WebSocket: Notify frontend "Review needed"
      └─ FlowExecutor.wait_for_approval()
   ↓
   
4. HUMAN REVIEW
   ↓
   Frontend: HITLModal pops up
   - Shows: Researcher output
   - Human reviews
   - Options: Approve / Reject with comments
   ↓
   Case A: Human Approves
   - POST /api/v1/hitl/{review_id}/approve
   - FlowExecutor continues to Step 2
   ↓
   Case B: Human Rejects
   - POST /api/v1/hitl/{review_id}/reject
   - Comments: "Add more detail about market size"
   - FlowExecutor RE-RUNS Step 1 with comments as context
   - Researcher agent gets:
     * Original prompt
     * Previous output
     * Human comments
   - Produces new output
   - HITL review created again
   ↓
   
5. CONTINUE EXECUTION (after approval)
   ↓
   Step 2: Analyst Agent
   ├─ MemoryManager.get_context_for_agent("analyst")
   │  └─ Returns:
   │     * Shared memory (Researcher's approved output)
   │     * Execution history (if flow ran before)
   ├─ LLMService.generate(prompt + context)
   ├─ Agent Output: "Analysis of research findings..."
   ├─ MemoryManager.add_to_memory()
   └─ No HITL gate (user didn't enable it)
   ↓
   
6. FLOW COMPLETION
   ↓
   FlowExecutor.finalize()
   ├─ Save execution record to PostgreSQL
   │  └─ Status: "completed"
   │     Total steps: 2
   │     Success: true
   ├─ Save detailed logs to MongoDB
   ├─ Update analytics
   │  └─ Researcher: +1 run, +1 success
   │     Analyst: +1 run, +1 success
   └─ WebSocket: Notify frontend "Execution complete"
   ↓
   
7. USER VIEWS RESULTS
   ↓
   Frontend: ExecutionViewer
   - Shows final output from Analyst
   - Shows execution timeline
   - Shows logs for each step
   ↓
   Frontend: AnalyticsDashboard
   - Success rate: 100%
   - Total executions: 1
   - Agent performance chart
   ↓
   
8. MEMORY PERSISTENCE
   ↓
   User runs flow again (2nd time)
   ↓
   Researcher agent now receives context:
   {
     "shared_memory": { ... },
     "execution_history": [
       {
         "run_number": 1,
         "date": "2026-03-02",
         "researcher_output": "...",
         "analyst_output": "...",
         "status": "completed"
       }
     ]
   }
   ↓
   Agent can reference previous runs!
3.3 Data Flow
┌─────────────────────────────────────────────────────────┐
│                    DATA FLOW DIAGRAM                     │
└─────────────────────────────────────────────────────────┘
Flow Configuration (Design Time)
═══════════════════════════════════
User Design → React Flow State → API → PostgreSQL
  ↓              ↓                  ↓        ↓
Canvas      nodes: [],        POST     flows table
            edges: []          /flows   agents table
Flow Execution (Runtime)
═══════════════════════════════════
PostgreSQL → FlowExecutor → Agent → LiteLLM → Model
     ↓            ↓           ↓         ↓        ↓
Load config   Orchestrate  Execute   DialKey  GPT-4o
     ↓            ↓           ↓                   ↓
     └────────────┴───────────┴────> Output ─────┘
                                        ↓
                              ┌─────────┴─────────┐
                              ↓                   ↓
                           Redis             MongoDB
                    (short-term memory)  (long-term memory)
                              ↓                   ↓
                        session data      execution_history
                        shared_memory     flow_memory
                              ↓                   ↓
                              └─────────┬─────────┘
                                        ↓
                              Next Agent Execution
                          (receives full context)
Analytics Flow
═══════════════════════════════════
Execution Complete → AnalyticsService → PostgreSQL
        ↓                   ↓                ↓
  Update metrics     Calculate stats   agent_analytics
        ↓                   ↓                ↓
    WebSocket         Aggregate data     Update rows
        ↓                   ↓
  Frontend Dashboard  ← API Request ←  GET /analytics
HITL Flow
═══════════════════════════════════
Agent Output → HITLManager → PostgreSQL + Redis
     ↓             ↓              ↓           ↓
Create review  Generate ID   hitl_reviews  queue:reviews
     ↓             ↓              ↓
 WebSocket ───→ Frontend ───→ Modal
     ↓             ↓              ↓
  Notify      User sees      Approve/Reject
     ↓             ↓              ↓
     └─────────────┴──────────────┘
                   ↓
              POST /hitl/{id}/approve
                   ↓
            Update PostgreSQL
                   ↓
          Resume Flow Execution
---
4. TECHNOLOGY STACK
4.1 Frontend Stack
Core Framework:
  - React: 18.2.0
  - TypeScript: 5.3.3
  - Vite: 5.0.7
Canvas & Visualization:
  - React Flow: 11.10.0
    Why: Industry standard for node-based UIs
    Features: Drag-drop, zoom, pan, custom nodes/edges
  
State Management:
  - Zustand: 4.4.7
    Why: Lightweight, TypeScript-friendly
    Use: Flow state, agent configs, execution state
UI Components:
  - Tailwind CSS: 3.3.6
    Why: Utility-first, rapid development
  - Radix UI: (Dialog, Select, etc.)
    Why: Accessible, unstyled components
  - Lucide React: Icons
Code Editor:
  - Monaco Editor: 4.6.0
    Why: VS Code editor for system prompts
    Features: Syntax highlighting, autocomplete
Data Visualization:
  - Recharts: 2.10.0
    Why: React-friendly charting library
    Use: Analytics dashboard
HTTP & WebSocket:
  - Axios: 1.6.2
    Why: Promise-based HTTP client
  - Socket.IO Client: 4.6.0
    Why: Real-time bidirectional communication
4.2 Backend Stack
Core Framework:
  - FastAPI: 0.108.0
    Why: Modern, fast, type-safe API framework
    Features: Auto OpenAPI docs, async support
  - Uvicorn: 0.25.0 (ASGI server)
  - Python: 3.10+
Database ORMs:
  - SQLAlchemy: 2.0.23
    Why: Mature ORM for PostgreSQL
  - Motor: Async MongoDB driver
    Why: Native async support for FastAPI
  - Redis-py: 5.0.1
    Why: Official Redis client
Data Validation:
  - Pydantic: 2.5.2
    Why: Built into FastAPI, excellent validation
LLM Integration:
  - LiteLLM: 1.17.0
    Why: Unified API for all LLM providers
    Features: DialKey proxy support, retries, fallbacks
    Models: GPT-4o, GPT-4o-mini, Claude-3.5-Sonnet, etc.
WebSocket:
  - python-socketio: 5.10.0
    Why: Room-based pub/sub, integrates with FastAPI
Utilities:
  - python-dotenv: Environment variables
  - httpx: Async HTTP client
  - python-multipart: File upload support
4.3 Database Technologies
PostgreSQL: 15
  Purpose: Primary relational database
  Tables:
    - flows (flow configurations)
    - agents (agent metadata)
    - flow_executions (execution records)
    - step_executions (individual step logs)
    - hitl_reviews (HITL approval queue)
    - agent_analytics (performance metrics)
  
MongoDB: 7
  Purpose: Document storage for logs and memory
  Collections:
    - execution_history (detailed execution logs)
    - flow_memory (long-term, persistent memory per flow)
  
Redis: 7
  Purpose: Cache, sessions, queues
  Data structures:
    - Hashes: session:{execution_id}
    - Lists: hitl:queue
    - Strings: cache:flow:{flow_id}
    - PubSub: channel:execution:{execution_id}
4.4 Development Tools
Frontend:
  - ESLint: Code linting
  - Prettier: Code formatting
  - Vite DevTools: Development server
Backend:
  - Black: Code formatting
  - Pylint: Code linting
  - pytest: Testing framework
  - Alembic: Database migrations
Containerization:
  - Docker: 24+
  - Docker Compose: 2.0+
Version Control:
  - Git
  - GitHub (recommended)
---
5. DATABASE DESIGN
5.1 PostgreSQL Schema
-- ============================================
-- FLOWS TABLE
-- Stores flow configurations and metadata
-- ============================================
CREATE TABLE flows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    flow_config JSONB NOT NULL,
    -- flow_config structure:
    -- {
    --   "nodes": [
    --     {
    --       "id": "node-1",
    --       "type": "agent",
    --       "position": {"x": 100, "y": 100},
    --       "data": {
    --         "agent_id": "uuid",
    --         "name": "Researcher",
    --         "type": "conversational",
    --         "system_prompt": "You are...",
    --         "role": "researcher",
    --         "model": "gpt-4o",
    --         "hitl_config": {
    --           "before": false,
    --           "after": true,
    --           "on_demand": false
    --         }
    --       }
    --     }
    --   ],
    --   "edges": [
    --     {
    --       "id": "edge-1",
    --       "source": "node-1",
    --       "target": "node-2"
    --     }
    --   ]
    -- }
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),  -- API key identifier
    CONSTRAINT flow_name_not_empty CHECK (name <> '')
);
CREATE INDEX idx_flows_created_at ON flows(created_at DESC);
CREATE INDEX idx_flows_created_by ON flows(created_by);
-- ============================================
-- AGENTS TABLE
-- Stores individual agent configurations
-- ============================================
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flow_id UUID REFERENCES flows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    -- type options: 'conversational'
    -- (multimodal in Phase 2)
    system_prompt TEXT NOT NULL,
    role VARCHAR(100) NOT NULL,
    -- role options: 'researcher', 'analyst', 'writer', 
    -- 'critic', 'planner', 'custom'
    model_name VARCHAR(100) NOT NULL,
    -- model_name options: 'gpt-4o', 'gpt-4o-mini', 
    -- 'claude-3-5-sonnet-20241022', etc.
    config JSONB,
    -- config structure:
    -- {
    --   "temperature": 0.7,
    --   "max_tokens": 2000,
    --   "hitl_gates": {
    --     "before": false,
    --     "after": true,
    --     "on_demand": false
    --   },
    --   "retry_config": {
    --     "max_retries": 3,
    --     "backoff": "exponential"
    --   }
    -- }
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT agent_name_not_empty CHECK (name <> ''),
    CONSTRAINT agent_type_valid CHECK (type IN ('conversational')),
    CONSTRAINT agent_role_valid CHECK (role IN (
        'researcher', 'analyst', 'writer', 'critic', 
        'planner', 'custom'
    ))
);
CREATE INDEX idx_agents_flow_id ON agents(flow_id);
CREATE INDEX idx_agents_type ON agents(type);
CREATE INDEX idx_agents_role ON agents(role);
-- ============================================
-- FLOW EXECUTIONS TABLE
-- Tracks flow execution instances
-- ============================================
CREATE TABLE flow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flow_id UUID REFERENCES flows(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- status options: 'pending', 'running', 'paused_hitl', 
    -- 'completed', 'failed', 'cancelled'
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    total_steps INTEGER NOT NULL,
    completed_steps INTEGER DEFAULT 0,
    current_step INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    error_message TEXT,
    execution_metadata JSONB,
    -- execution_metadata structure:
    -- {
    --   "triggered_by": "api_key_id",
    --   "execution_mode": "background",
    --   "total_llm_calls": 5,
    --   "total_hitl_reviews": 2
    -- }
    CONSTRAINT status_valid CHECK (status IN (
        'pending', 'running', 'paused_hitl', 
        'completed', 'failed', 'cancelled'
    )),
    CONSTRAINT success_rate_range CHECK (
        success_rate >= 0 AND success_rate <= 100
    )
);
CREATE INDEX idx_executions_flow_id ON flow_executions(flow_id);
CREATE INDEX idx_executions_status ON flow_executions(status);
CREATE INDEX idx_executions_started_at ON flow_executions(started_at DESC);
-- ============================================
-- STEP EXECUTIONS TABLE
-- Detailed logs for each step in a flow
-- ============================================
CREATE TABLE step_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES flow_executions(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id),
    step_number INTEGER NOT NULL,
    input_data JSONB,
    -- input_data structure:
    -- {
    --   "user_message": "...",
    --   "context": {
    --     "shared_memory": {...},
    --     "execution_history": [...]
    --   }
    -- }
    output_data JSONB,
    -- output_data structure:
    -- {
    --   "content": "Agent response...",
    --   "metadata": {
    --     "model_used": "gpt-4o",
    --     "tokens_used": 1500,
    --     "latency_ms": 2340
    --   }
    -- }
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- status: 'pending', 'running', 'completed', 
    -- 'failed', 'skipped', 'rerunning'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_ms INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    CONSTRAINT status_valid CHECK (status IN (
        'pending', 'running', 'completed', 
        'failed', 'skipped', 'rerunning'
    ))
);
CREATE INDEX idx_step_exec_execution_id ON step_executions(execution_id);
CREATE INDEX idx_step_exec_agent_id ON step_executions(agent_id);
CREATE INDEX idx_step_exec_step_number ON step_executions(execution_id, step_number);
-- ============================================
-- HITL REVIEWS TABLE
-- Human-in-the-loop approval queue
-- ============================================
CREATE TABLE hitl_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES flow_executions(id),
    step_id UUID REFERENCES step_executions(id),
    agent_id UUID REFERENCES agents(id),
    gate_type VARCHAR(20) NOT NULL,
    -- gate_type: 'before', 'after', 'on_demand'
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- status: 'pending', 'approved', 'rejected'
    output_to_review JSONB NOT NULL,
    -- output_to_review structure:
    -- {
    --   "agent_name": "Researcher",
    --   "agent_output": "...",
    --   "context_used": {...}
    -- }
    reviewer_comments TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(255),  -- API key identifier
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
-- ============================================
-- AGENT ANALYTICS TABLE (AGGREGATE)
-- One row per agent, continuously updated.
-- Tracks lifetime performance stats per agent.
-- DO NOT add execution_id here — use
-- agent_execution_events for per-execution data.
-- ============================================
CREATE TABLE agent_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE UNIQUE,
    -- UNIQUE: one aggregate row per agent
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
-- ============================================
-- AGENT EXECUTION EVENTS TABLE (PER-EXECUTION LOG)
-- One row per agent per execution run.
-- Used to compute per-run breakdowns and to
-- update the aggregate agent_analytics table.
-- ============================================
CREATE TABLE agent_execution_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    execution_id UUID REFERENCES flow_executions(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    -- status: 'completed', 'failed'
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
-- ============================================
-- FUNCTION: update_agent_analytics_on_event()
-- Automatically keeps aggregate table in sync
-- whenever a new agent_execution_events row is
-- inserted. Called by trigger below.
-- ============================================
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
-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================
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
5.2 MongoDB Collections
// ============================================
// EXECUTION_HISTORY COLLECTION
// Detailed, timestamped logs for each execution
// ============================================
{
  "_id": ObjectId,
  "flow_id": "uuid-from-postgres",
  "execution_id": "uuid-from-postgres",
  "flow_name": "Research & Analysis Flow",
  "started_at": ISODate("2026-03-02T10:00:00Z"),
  "completed_at": ISODate("2026-03-02T10:05:23Z"),
  "status": "completed",
  "execution_log": [
    {
      "timestamp": ISODate("2026-03-02T10:00:01Z"),
      "event_type": "step_start",
      "step_number": 1,
      "agent_id": "uuid",
      "agent_name": "Researcher",
      "metadata": {
        "model": "gpt-4o",
        "temperature": 0.7
      }
    },
    {
      "timestamp": ISODate("2026-03-02T10:00:15Z"),
      "event_type": "llm_call",
      "step_number": 1,
      "agent_id": "uuid",
      "input": {
        "system_prompt": "You are a researcher...",
        "user_message": "Research AI trends",
        "context": {...}
      },
      "output": {
        "content": "AI trends analysis...",
        "tokens_used": 1500,
        "latency_ms": 2340
      }
    },
    {
      "timestamp": ISODate("2026-03-02T10:00:20Z"),
      "event_type": "hitl_review_created",
      "step_number": 1,
      "review_id": "uuid",
      "gate_type": "after"
    },
    {
      "timestamp": ISODate("2026-03-02T10:02:45Z"),
      "event_type": "hitl_review_approved",
      "step_number": 1,
      "review_id": "uuid",
      "reviewer_comments": "Looks good"
    },
    {
      "timestamp": ISODate("2026-03-02T10:02:50Z"),
      "event_type": "memory_updated",
      "step_number": 1,
      "memory_type": "shared",
      "data": {
        "agent": "Researcher",
        "output": "AI trends analysis..."
      }
    },
    {
      "timestamp": ISODate("2026-03-02T10:03:00Z"),
      "event_type": "step_completed",
      "step_number": 1,
      "agent_id": "uuid",
      "status": "success",
      "execution_time_ms": 2340
    },
    // ... more steps
  ],
  "memory_snapshots": [
    {
      "timestamp": ISODate("2026-03-02T10:00:20Z"),
      "step_number": 1,
      "shared_memory": {
        "researcher_output": "AI trends analysis..."
      },
      "agent_memories": {
        "researcher_uuid": {
          "last_output": "AI trends analysis...",
          "execution_count": 1
        }
      }
    },
    // ... more snapshots
  ],
  "final_output": {
    "analyst_output": "Based on the research...",
    "execution_summary": "Successfully completed 2-agent flow"
  },
  "metadata": {
    "total_steps": 2,
    "total_hitl_reviews": 1,
    "total_llm_calls": 2,
    "total_execution_time_ms": 320000
  },
  "created_at": ISODate("2026-03-02T10:00:00Z")
}
// Index for fast queries
db.execution_history.createIndex({ "flow_id": 1, "started_at": -1 });
db.execution_history.createIndex({ "execution_id": 1 });
db.execution_history.createIndex({ "status": 1 });
// ============================================
// FLOW_MEMORY COLLECTION
// Long-term, persistent memory per flow
// Shared across all executions of the same flow
// ============================================
{
  "_id": ObjectId,
  "flow_id": "uuid-from-postgres",
  "flow_name": "Research & Analysis Flow",
  "shared_memory": {
    "conversation_history": [
      {
        "execution_id": "exec-1-uuid",
        "date": ISODate("2026-03-02T10:00:00Z"),
        "researcher_output": "AI trends...",
        "analyst_output": "Analysis..."
      },
      {
        "execution_id": "exec-2-uuid",
        "date": ISODate("2026-03-03T14:00:00Z"),
        "researcher_output": "Updated AI trends...",
        "analyst_output": "Updated analysis..."
      }
    ],
    "accumulated_facts": [
      "AI adoption increased by 40% in 2025",
      "Healthcare AI market reached $10B",
      // ... more facts learned over time
    ],
    "key_insights": [
      "Users prefer agentic workflows for complex tasks",
      "HITL gates improve output quality by 35%"
    ]
  },
  "agent_memories": {
    "researcher_uuid": {
      "role": "researcher",
      "execution_count": 5,
      "successful_executions": 5,
      "failed_executions": 0,
      "learned_patterns": [
        "Always check multiple sources",
        "Include market size data"
      ],
      "last_execution": ISODate("2026-03-03T14:00:00Z")
    },
    "analyst_uuid": {
      "role": "analyst",
      "execution_count": 5,
      "successful_executions": 4,
      "failed_executions": 1,
      "learned_patterns": [
        "Structure analysis in 3 parts: trends, risks, opportunities"
      ],
      "last_execution": ISODate("2026-03-03T14:00:00Z")
    }
  },
  "metadata": {
    "total_executions": 5,
    "last_execution_date": ISODate("2026-03-03T14:00:00Z"),
    "memory_size_bytes": 45000,
    "created_at": ISODate("2026-03-02T10:00:00Z"),
    "last_updated": ISODate("2026-03-03T14:05:23Z")
  }
}
// Index for fast lookups
db.flow_memory.createIndex({ "flow_id": 1 }, { unique: true });
db.flow_memory.createIndex({ "metadata.last_updated": -1 });
5.3 Redis Data Structures
# ============================================
# SESSION DATA
# Temporary execution state during runtime
# ============================================
# Key pattern: session:{execution_id}
# Type: Hash
# TTL: 1 hour after execution completes
HSET session:exec-123 current_step 2
HSET session:exec-123 status "running"
HSET session:exec-123 started_at "2026-03-02T10:00:00Z"
HSET session:exec-123 agent_states '{"researcher": "completed", "analyst": "running"}'
# Retrieve all session data
HGETALL session:exec-123
# Returns:
# {
#   "current_step": "2",
#   "status": "running",
#   "started_at": "2026-03-02T10:00:00Z",
#   "agent_states": "{\"researcher\": \"completed\", ...}"
# }
# ============================================
# SHARED MEMORY (Short-term)
# Memory accessible by all agents during execution
# ============================================
# Key pattern: memory:{execution_id}:shared
# Type: Hash
# TTL: 24 hours after execution
HSET memory:exec-123:shared researcher_output "AI trends analysis..."
HSET memory:exec-123:shared last_updated "2026-03-02T10:00:20Z"
# Retrieve all shared memory
HGETALL memory:exec-123:shared
# ============================================
# HITL QUEUE
# List of pending HITL reviews
# ============================================
# Key: hitl:queue
# Type: List (FIFO queue)
# Add review to queue
LPUSH hitl:queue review-uuid-1
LPUSH hitl:queue review-uuid-2
# Get pending reviews (non-blocking)
LRANGE hitl:queue 0 -1
# Returns: ["review-uuid-2", "review-uuid-1"]
# Remove review after approval
LREM hitl:queue 1 review-uuid-1
# ============================================
# CACHE
# Frequently accessed data
# ============================================
# Key pattern: cache:flow:{flow_id}
# Type: String (JSON)
# TTL: 5 minutes
SET cache:flow:abc123 '{"name": "Research Flow", "agents": [...]}' EX 300
# Key pattern: cache:agent:{agent_id}
SET cache:agent:def456 '{"name": "Researcher", "role": "researcher"}' EX 300
# ============================================
# PUBSUB CHANNELS
# Real-time notifications
# ============================================
# Channel pattern: channel:execution:{execution_id}
# Backend publishes events
PUBLISH channel:execution:exec-123 '{"type": "step_completed", "step": 1}'
PUBLISH channel:execution:exec-123 '{"type": "hitl_review_needed", "review_id": "..."}'
# Frontend subscribes
SUBSCRIBE channel:execution:exec-123
# ============================================
# RATE LIMITING (for DialKey)
# Track API calls to respect rate limits
# ============================================
# Key pattern: ratelimit:dialkey:{minute}
# Type: String (counter)
# TTL: 60 seconds
INCR ratelimit:dialkey:2026-03-02T10:00
EXPIRE ratelimit:dialkey:2026-03-02T10:00 60
# Check if limit reached
GET ratelimit:dialkey:2026-03-02T10:00
# If > threshold, wait before next call
---
6. API SPECIFICATION
6.1 API Overview
Base URL: http://localhost:8080/api/v1  
Authentication: API Key in header: X-API-Key: your_api_key  
Content-Type: application/json  
WebSocket URL: ws://localhost:8080/ws
6.2 Flow Management Endpoints
POST /flows
Create a new flow
Request:
{
  name: Research & Analysis Flow,
  description: Research AI trends and analyze findings,
  flow_config: {
    nodes: [
      {
        id: node-start,
        type: start,
        position: { x: 100, y: 100 },
        data: { label: Start }
      },
      {
        id: node-1,
        type: agent,
        position: { x: 300, y: 100 },
        data: {
          name: Researcher,
          type: conversational,
          system_prompt: You are a research assistant who finds and summarizes information about AI trends. Be thorough and cite sources.,
          role: researcher,
          model: gpt-4o,
          config: {
            temperature: 0.7,
            max_tokens: 2000,
            hitl_gates: {
              before: false,
              after: true,
              on_demand: false
            }
          }
        }
      },
      {
        id: node-2,
        type: agent,
        position: { x: 600, y: 100 },
        data: {
          name: Analyst,
          type: conversational,
          system_prompt: You are an analyst who examines research findings and provides strategic insights. Structure your analysis in 3 parts: trends, risks, opportunities.,
          role: analyst,
          model: claude-3-5-sonnet-20241022,
          config: {
            temperature: 0.5,
            max_tokens: 3000,
            hitl_gates: {
              before: false,
              after: false,
              on_demand: false
            }
          }
        }
      },
      {
        id: node-end,
        type: end,
        position: { x: 900, y: 100 },
        data: { label: End }
      }
    ],
    edges: [
      {
        id: edge-1,
        source: node-start,
        target: node-1,
        type: smoothstep
      },
      {
        id: edge-2,
        source: node-1,
        target: node-2,
        type: smoothstep
      },
      {
        id: edge-3,
        source: node-2,
        target: node-end,
        type: smoothstep
      }
    ]
  }
}
Response (201 Created):
{
  id: 550e8400-e29b-41d4-a716-446655440000,
  name: Research & Analysis Flow,
  description: Research AI trends and analyze findings,
  flow_config: { ... },
  created_at: 2026-03-02T10:00:00Z,
  updated_at: 2026-03-02T10:00:00Z
}
GET /flows
List all flows
Response (200 OK):
{
  flows: [
    {
      id: 550e8400-e29b-41d4-a716-446655440000,
      name: Research & Analysis Flow,
      description: Research AI trends and analyze findings,
      created_at: 2026-03-02T10:00:00Z,
      total_executions: 5,
      last_executed_at: 2026-03-03T14:00:00Z
    }
  ],
  total: 1
}
GET /flows/{flow_id}
Get flow details
Response (200 OK):
{
  id: 550e8400-e29b-41d4-a716-446655440000,
  name: Research & Analysis Flow,
  description: Research AI trends and analyze findings,
  flow_config: { ... },
  agents: [
    {
      id: agent-1-uuid,
      name: Researcher,
      role: researcher,
      model: gpt-4o
    },
    {
      id: agent-2-uuid,
      name: Analyst,
      role: analyst,
      model: claude-3-5-sonnet-20241022
    }
  ],
  created_at: 2026-03-02T10:00:00Z,
  updated_at: 2026-03-02T10:00:00Z
}
PUT /flows/{flow_id}
Update flow
Request: (Same structure as POST /flows)
Response (200 OK): Updated flow object
DELETE /flows/{flow_id}
Delete flow
Response (204 No Content)
---
6.3 Execution Endpoints
POST /executions/start
Start flow execution
Request:
{
  flow_id: 550e8400-e29b-41d4-a716-446655440000,
  initial_input: Research the latest AI trends in healthcare for 2026,
  execution_mode: background
}
Response (202 Accepted):
{
  execution_id: exec-123-uuid,
  flow_id: 550e8400-e29b-41d4-a716-446655440000,
  status: running,
  started_at: 2026-03-02T10:00:00Z,
  total_steps: 2,
  current_step: 0,
  websocket_channel: channel:execution:exec-123-uuid
}
GET /executions/{execution_id}
Get execution status
Response (200 OK):
{
  execution_id: exec-123-uuid,
  flow_id: 550e8400-e29b-41d4-a716-446655440000,
  status: paused_hitl,
  started_at: 2026-03-02T10:00:00Z,
  completed_at: null,
  total_steps: 2,
  completed_steps: 1,
  current_step: 1,
  success_rate: null,
  steps: [
    {
      step_number: 1,
      agent_id: agent-1-uuid,
      agent_name: Researcher,
      status: completed,
      started_at: 2026-03-02T10:00:01Z,
      completed_at: 2026-03-02T10:00:15Z,
      execution_time_ms: 14000,
      output: AI trends in healthcare...
    },
    {
      step_number: 2,
      agent_id: agent-2-uuid,
      agent_name: Analyst,
      status: pending,
      started_at: null,
      completed_at: null
    }
  ],
  pending_hitl_reviews: [
    {
      review_id: review-1-uuid,
      step_number: 1,
      agent_name: Researcher,
      gate_type: after
    }
  ]
}
GET /executions/{execution_id}/logs
Get detailed execution logs
Response (200 OK):
{
  execution_id: exec-123-uuid,
  logs: [
    {
      timestamp: 2026-03-02T10:00:01Z,
      event: step_start,
      step_number: 1,
      agent: Researcher,
      message: Started execution
    },
    {
      timestamp: 2026-03-02T10:00:05Z,
      event: llm_call,
      step_number: 1,
      model: gpt-4o,
      tokens: 1500,
      latency_ms: 2340
    },
    {
      timestamp: 2026-03-02T10:00:15Z,
      event: step_completed,
      step_number: 1,
      status: success
    },
    {
      timestamp: 2026-03-02T10:00:20Z,
      event: hitl_review_created,
      review_id: review-1-uuid,
      gate_type: after
    }
  ]
}
POST /executions/{execution_id}/pause
Manually pause execution
Response (200 OK):
{
  execution_id: exec-123-uuid,
  status: paused,
  message: Execution paused successfully
}
POST /executions/{execution_id}/resume
Resume paused execution
Response (200 OK):
{
  execution_id: exec-123-uuid,
  status: running,
  message: Execution resumed successfully
}
---
6.4 HITL Endpoints
GET /hitl/queue
Get pending HITL reviews
Response (200 OK):
{
  reviews: [
    {
      review_id: review-1-uuid,
      execution_id: exec-123-uuid,
      step_id: step-1-uuid,
      agent_id: agent-1-uuid,
      agent_name: Researcher,
      gate_type: after,
      status: pending,
      output_to_review: {
        agent_output: AI trends in healthcare for 2026:\n1. Increased adoption...,
        context_used: {
          previous_executions: 2,
          memory_context: ...
        }
      },
      created_at: 2026-03-02T10:00:20Z
    }
  ],
  total_pending: 1
}
POST /hitl/{review_id}/approve
Approve HITL review
Request:
{
  comments: Looks good, comprehensive research
}
Response (200 OK):
{
  review_id: review-1-uuid,
  status: approved,
  reviewed_at: 2026-03-02T10:02:45Z,
  message: Review approved. Execution will continue.
}
POST /hitl/{review_id}/reject
Reject HITL review (triggers re-run with comments)
Request:
{
  comments: Need more detail about market size and specific companies leading adoption
}
Response (200 OK):
{
  review_id: review-1-uuid,
  status: rejected,
  reviewed_at: 2026-03-02T10:02:45Z,
  message: Review rejected. Agent will re-run with your feedback.,
  rerun_scheduled: true
}
---
6.5 Analytics Endpoints
GET /analytics/flows
Get flow-level analytics
Response (200 OK):
{
  flows: [
    {
      flow_id: 550e8400-e29b-41d4-a716-446655440000,
      flow_name: Research & Analysis Flow,
      total_executions: 10,
      successful_executions: 9,
      failed_executions: 1,
      success_rate: 90.0,
      avg_execution_time_ms: 45000,
      total_hitl_reviews: 15,
      last_executed_at: 2026-03-03T14:00:00Z
    }
  ]
}
GET /analytics/agents
Get agent-level analytics
Query Parameters:
- flow_id (optional): Filter by flow
Response (200 OK):
{
  agents: [
    {
      agent_id: agent-1-uuid,
      agent_name: Researcher,
      role: researcher,
      model: gpt-4o,
      total_runs: 10,
      successful_runs: 10,
      failed_runs: 0,
      success_rate: 100.0,
      avg_execution_time_ms: 15000,
      total_hitl_reviews: 10,
      last_run_at: 2026-03-03T14:00:00Z
    },
    {
      agent_id: agent-2-uuid,
      agent_name: Analyst,
      role: analyst,
      model: claude-3-5-sonnet-20241022,
      total_runs: 9,
      successful_runs: 9,
      failed_runs: 0,
      success_rate: 100.0,
      avg_execution_time_ms: 30000,
      total_hitl_reviews: 0,
      last_run_at: 2026-03-03T14:00:00Z
    }
  ]
}
GET /analytics/executions/{execution_id}
Get detailed analytics for a specific execution
Response (200 OK):
{
  execution_id: exec-123-uuid,
  flow_name: Research & Analysis Flow,
  status: completed,
  started_at: 2026-03-02T10:00:00Z,
  completed_at: 2026-03-02T10:05:23Z,
  total_execution_time_ms: 323000,
  total_steps: 2,
  completed_steps: 2,
  success_rate: 100.0,
  steps_breakdown: [
    {
      step_number: 1,
      agent_name: Researcher,
      execution_time_ms: 14000,
      llm_calls: 1,
      tokens_used: 1500,
      hitl_reviews: 1,
      hitl_approval_time_ms: 145000
    },
    {
      step_number: 2,
      agent_name: Analyst,
      execution_time_ms: 30000,
      llm_calls: 1,
      tokens_used: 2500,
      hitl_reviews: 0
    }
  ],
  timeline: [
    {
      timestamp: 2026-03-02T10:00:01Z,
      event: step_1_start
    },
    {
      timestamp: 2026-03-02T10:00:15Z,
      event: step_1_completed
    },
    {
      timestamp: 2026-03-02T10:00:20Z,
      event: hitl_review_created
    },
    {
      timestamp: 2026-03-02T10:02:45Z,
      event: hitl_review_approved
    },
    {
      timestamp: 2026-03-02T10:02:50Z,
      event: step_2_start
    },
    {
      timestamp: 2026-03-02T10:05:20Z,
      event: step_2_completed
    },
    {
      timestamp: 2026-03-02T10:05:23Z,
      event: execution_completed
    }
  ]
}
---
6.6 WebSocket Events
Connection URL: ws://localhost:8080/ws/execution/{execution_id}
Client → Server (Subscribe):
{
  type: subscribe,
  execution_id: exec-123-uuid
}
Server → Client Events:
// Step started
{
  type: step_started,
  execution_id: exec-123-uuid,
  step_number: 1,
  agent_name: Researcher,
  timestamp: 2026-03-02T10:00:01Z
}
// Step completed
{
  type: step_completed,
  execution_id: exec-123-uuid,
  step_number: 1,
  agent_name: Researcher,
  status: success,
  output: AI trends in healthcare...,
  execution_time_ms: 14000,
  timestamp: 2026-03-02T10:00:15Z
}
// HITL review needed
{
  type: hitl_review_needed,
  execution_id: exec-123-uuid,
  review_id: review-1-uuid,
  step_number: 1,
  agent_name: Researcher,
  gate_type: after,
  output_to_review: ...,
  timestamp: 2026-03-02T10:00:20Z
}
// HITL review completed
{
  type: hitl_review_completed,
  execution_id: exec-123-uuid,
  review_id: review-1-uuid,
  status: approved,
  comments: Looks good,
  timestamp: 2026-03-02T10:02:45Z
}
// Execution completed
{
  type: execution_completed,
  execution_id: exec-123-uuid,
  status: completed,
  total_steps: 2,
  success_rate: 100.0,
  total_time_ms: 323000,
  timestamp: 2026-03-02T10:05:23Z
}
// Execution failed
{
  type: execution_failed,
  execution_id: exec-123-uuid,
  step_number: 2,
  error_message: LLM API rate limit exceeded,
  timestamp: 2026-03-02T10:05:23Z
}


7. FRONTEND DESIGN (CONTINUED)
7.1 Component Hierarchy (Complete)
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── FlowSelector (dropdown)
│   │   └── Actions (Run, Save, Load)
│   └── Main
│       ├── LeftSidebar
│       │   ├── AgentPalette
│       │   │   ├── AgentTemplate (Researcher)
│       │   │   ├── AgentTemplate (Analyst)
│       │   │   ├── AgentTemplate (Writer)
│       │   │   ├── AgentTemplate (Critic)
│       │   │   └── AgentTemplate (Planner)
│       │   └── FlowControls
│       │       ├── RunButton
│       │       ├── PauseButton
│       │       └── StopButton
│       ├── Canvas (React Flow)
│       │   ├── StartNode
│       │   ├── AgentNode (multiple)
│       │   │   ├── NodeHeader (name, role, status)
│       │   │   ├── NodeBody (icon, model badge)
│       │   │   └── NodeFooter (HITL indicator)
│       │   ├── EndNode
│       │   └── CustomEdge (animated when executing)
│       └── RightSidebar
│           ├── AgentConfigPanel (when node selected)
│           │   ├── BasicInfo
│           │   │   ├── NameInput
│           │   │   ├── RoleSelector
│           │   │   └── ModelSelector
│           │   ├── SystemPromptEditor (Monaco)
│           │   ├── HITLConfig
│           │   │   ├── BeforeToggle
│           │   │   ├── AfterToggle
│           │   │   └── OnDemandToggle
│           │   └── AdvancedConfig
│           │       ├── TemperatureSlider
│           │       └── MaxTokensInput
│           ├── ExecutionViewer (when flow running)
│           │   ├── ProgressBar
│           │   ├── CurrentStepIndicator
│           │   ├── StepList
│           │   │   └── StepCard (multiple)
│           │   │       ├── StepNumber
│           │   │       ├── AgentName
│           │   │       ├── Status
│           │   │       ├── Output
│           │   │       └── ExecutionTime
│           │   └── LogViewer
│           └── HITLPanel (when review needed)
│               ├── ReviewQueue
│               │   └── ReviewCard (multiple)
│               │       ├── AgentName
│               │       ├── Output
│               │       └── ActionButtons
│               └── HITLModal
│                   ├── ModalHeader
│                   ├── OutputDisplay
│                   ├── CommentTextarea
│                   └── ActionButtons (Approve/Reject)
└── Modals
    ├── SaveFlowDialog
    │   ├── FlowNameInput
    │   ├── DescriptionTextarea
    │   └── SaveButton
    ├── LoadFlowDialog
    │   ├── FlowList
    │   │   └── FlowCard (multiple)
    │   │       ├── FlowName
    │   │       ├── LastExecuted
    │   │       └── LoadButton
    │   └── SearchInput
    └── AnalyticsDashboard
        ├── MetricsOverview
        │   ├── TotalExecutions
        │   ├── SuccessRate
        │   └── AvgExecutionTime
        ├── FlowPerformanceChart (Recharts)
        ├── AgentPerformanceTable
        │   └── AgentRow (multiple)
        │       ├── AgentName
        │       ├── TotalRuns
        │       ├── SuccessRate
        │       └── AvgTime
        └── ExecutionHistory
            └── ExecutionCard (multiple)
                ├── Timestamp
                ├── Status
                └── ViewLogsButton
7.2 Key UI Components Specification
FlowCanvas Component
// frontend/src/components/Canvas/FlowCanvas.tsx
interface FlowCanvasProps {
  flowId?: string;
}
Features:
- React Flow integration
- Drag-and-drop from agent palette
- Node selection (highlights selected node)
- Edge creation (click source → click target)
- Zoom controls (fit view, zoom in/out)
- Mini-map (overview of large flows)
- Node validation (ensures connections are valid)
- Real-time execution visualization
  - Nodes light up green when executing
  - Edges animate when data flows
  - Completed nodes show checkmark
  - Failed nodes show error indicator
State Management:
- nodes: Node[]
- edges: Edge[]
- selectedNode: Node | null
- executionStatus: ExecutionStatus
AgentNode Component
// frontend/src/components/Canvas/NodeTypes/AgentNode.tsx
interface AgentNodeProps {
  data: {
    name: string;
    role: string;
    model: string;
    status: 'idle' | 'running' | 'completed' | 'failed';
    hitl_enabled: boolean;
  };
}
Visual States:
- Idle: Gray border
- Running: Blue border + pulsing animation
- Completed: Green border + checkmark icon
- Failed: Red border + error icon
- HITL Enabled: Orange badge on top-right
Layout:
┌──────────────────────────────┐
│ 🤖 Researcher        [HITL]  │ ← Header (role icon + name + hitl badge)
├──────────────────────────────┤
│     [Robot Icon]             │ ← Body (large agent icon)
│   GPT-4o                     │ ← Model badge
├──────────────────────────────┤
│ ● Connected                  │ ← Footer (status dot + text)
└──────────────────────────────┘
Interactions:
- Click: Select node (opens config panel)
- Hover: Show tooltip with full config
- Drag handles: Connect to other nodes
AgentConfigPanel Component
// frontend/src/components/AgentConfig/AgentConfigPanel.tsx
interface AgentConfigPanelProps {
  nodeId: string;
  agentData: AgentData;
  onUpdate: (updates: Partial<AgentData>) => void;
}
Sections:
1. Basic Info
   - Name input (text)
   - Role selector (dropdown with templates)
   - Model selector (dropdown: GPT-4o, GPT-4o-mini, Claude-3.5-Sonnet, etc.)
2. System Prompt
   - Monaco Editor (JavaScript mode for syntax highlighting)
   - Height: 300px
   - Theme: VS Dark
   - Features: Line numbers, word wrap
3. HITL Configuration
   - "Enable HITL Gate Before Execution" (checkbox)
   - "Enable HITL Gate After Execution" (checkbox)
   - "Enable On-Demand HITL" (checkbox)
4. Advanced Settings (collapsible)
   - Temperature slider (0.0 - 1.0)
   - Max tokens input (number)
   - Retry attempts (number)
Layout:
┌─────────────────────────────────┐
│  Agent Configuration            │
│                                 │
│  Name: [Researcher______]       │
│  Role: [Researcher ▼]           │
│  Model: [GPT-4o ▼]              │
│                                 │
│  System Prompt                  │
│  ┌─────────────────────────┐   │
│  │ You are a research...   │   │
│  │                         │   │
│  │                         │   │
│  └─────────────────────────┘   │
│                                 │
│  HITL Gates                     │
│  ☐ Before execution             │
│  ☑ After execution              │
│  ☐ On-demand                    │
│                                 │
│  ▶ Advanced Settings            │
│                                 │
└─────────────────────────────────┘
HITLModal Component
// frontend/src/components/HITL/HITLModal.tsx
interface HITLModalProps {
  review: HITLReview;
  onApprove: (reviewId: string, comments: string) => void;
  onReject: (reviewId: string, comments: string) => void;
  onClose: () => void;
}
Layout:
┌────────────────────────────────────────┐
│  Review Required - Researcher      [X] │
│                                        │
│  Agent Output:                         │
│  ┌────────────────────────────────┐   │
│  │ AI trends in healthcare:       │   │
│  │ 1. Increased adoption...       │   │
│  │ 2. Market growth to $10B...    │   │
│  │                                │   │
│  │ (scrollable, read-only)        │   │
│  └────────────────────────────────┘   │
│                                        │
│  Your Comments (optional):             │
│  ┌────────────────────────────────┐   │
│  │                                │   │
│  │                                │   │
│  └────────────────────────────────┘   │
│                                        │
│  [Reject & Re-run]     [Approve] ──┐  │
│         (gray)           (green)    │  │
└────────────────────────────────────────┘
Behavior:
- Appears automatically when HITL review is created
- Blocks other interactions (modal overlay)
- "Approve" button:
  - Saves comments (if any)
  - Calls onApprove()
  - Closes modal
  - Execution continues
- "Reject" button:
  - Requires comments
  - Calls onReject()
  - Agent re-runs with feedback
  - Modal stays open for new review
ExecutionViewer Component
// frontend/src/components/ExecutionViewer/ExecutionPanel.tsx
interface ExecutionViewerProps {
  executionId: string;
}
Features:
- Real-time progress updates (via WebSocket)
- Step-by-step output display
- Collapsible step cards
- Log viewer (detailed logs button)
- Status indicators (running, paused, completed, failed)
Layout:
┌─────────────────────────────────┐
│  Execution Progress             │
│                                 │
│  [████████░░░░░░] 50% (1/2)    │
│  Status: Running                │
│  Time: 00:02:45                 │
│                                 │
│  ──────────────────────────     │
│                                 │
│  ✅ Step 1: Researcher          │
│  └─ Output: AI trends...        │
│  └─ Time: 14s                   │
│  └─ [View Full Output]          │
│                                 │
│  🔄 Step 2: Analyst             │
│  └─ Status: Running...          │
│  └─ Time: 00:00:30              │
│                                 │
│  [View Detailed Logs]           │
│                                 │
└─────────────────────────────────┘
AnalyticsDashboard Component
// frontend/src/components/Analytics/AnalyticsDashboard.tsx
Features:
- Overview metrics cards
- Line chart (executions over time)
- Bar chart (agent performance comparison)
- Table (detailed agent stats)
- Date range filter
Layout:
┌──────────────────────────────────────────┐
│  Analytics Dashboard                     │
│                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │Total Ex.│ │Success  │ │Avg Time │   │
│  │   15    │ │  93.3%  │ │ 45.2s   │   │
│  └─────────┘ └─────────┘ └─────────┘   │
│                                          │
│  Executions Over Time                    │
│  ┌────────────────────────────────┐     │
│  │      📈 Line Chart             │     │
│  │  (Recharts LineChart)          │     │
│  └────────────────────────────────┘     │
│                                          │
│  Agent Performance                       │
│  ┌────────────────────────────────┐     │
│  │ Agent    | Runs | Success | Avg│     │
│  │──────────┼──────┼─────────┼────│     │
│  │Research. │  15  │ 100.0%  │ 14s│     │
│  │Analyst   │  14  │  92.9%  │ 30s│     │
│  │Writer    │   8  │  87.5%  │ 25s│     │
│  └────────────────────────────────┘     │
│                                          │
└──────────────────────────────────────────┘
7.3 Pre-built Agent Templates
// frontend/src/data/agentTemplates.ts
export const AGENT_TEMPLATES = [
  {
    id: 'researcher',
    name: 'Researcher',
    role: 'researcher',
    icon: '🔍',
    description: 'Finds and summarizes information',
    systemPrompt: `You are a research assistant who finds and summarizes information thoroughly and accurately.
Your responsibilities:
- Search for relevant information on the given topic
- Verify information from multiple sources
- Provide clear, well-structured summaries
- Cite sources when possible
- Highlight key findings and data points
Guidelines:
- Be thorough but concise
- Focus on factual information
- Use bullet points for clarity
- Include relevant statistics and dates`,
    defaultModel: 'gpt-4o',
    defaultConfig: {
      temperature: 0.7,
      max_tokens: 2000,
      hitl_gates: {
        before: false,
        after: true,
        on_demand: false
      }
    }
  },
  {
    id: 'analyst',
    name: 'Analyst',
    role: 'analyst',
    icon: '📊',
    description: 'Analyzes data and provides insights',
    systemPrompt: `You are a strategic analyst who examines information and provides actionable insights.
Your responsibilities:
- Analyze research findings and data
- Identify patterns, trends, and correlations
- Assess risks and opportunities
- Provide strategic recommendations
- Structure analysis clearly
Analysis Framework:
1. TRENDS: What patterns are emerging?
2. RISKS: What challenges or threats exist?
3. OPPORTUNITIES: Where are the growth areas?
4. RECOMMENDATIONS: What actions should be taken?
Guidelines:
- Use data to support conclusions
- Consider multiple perspectives
- Be objective and balanced
- Provide specific, actionable recommendations`,
    defaultModel: 'claude-3-5-sonnet-20241022',
    defaultConfig: {
      temperature: 0.5,
      max_tokens: 3000,
      hitl_gates: {
        before: false,
        after: false,
        on_demand: false
      }
    }
  },
  {
    id: 'writer',
    name: 'Writer',
    role: 'writer',
    icon: '✍️',
    description: 'Creates engaging written content',
    systemPrompt: `You are a creative writer who produces engaging, well-structured content.
Your responsibilities:
- Transform information into compelling narratives
- Write in a clear, engaging style
- Adapt tone to the target audience
- Ensure proper structure and flow
- Edit for clarity and impact
Content Structure:
1. HOOK: Start with an engaging opening
2. CONTEXT: Provide necessary background
3. MAIN CONTENT: Develop ideas thoroughly
4. CONCLUSION: End with key takeaways
Guidelines:
- Use active voice
- Vary sentence length for rhythm
- Include specific examples
- Edit ruthlessly for clarity`,
    defaultModel: 'gpt-4o',
    defaultConfig: {
      temperature: 0.8,
      max_tokens: 2500,
      hitl_gates: {
        before: false,
        after: true,
        on_demand: false
      }
    }
  },
  {
    id: 'critic',
    name: 'Critic',
    role: 'critic',
    icon: '🎯',
    description: 'Reviews and improves content quality',
    systemPrompt: `You are a constructive critic who reviews work and suggests improvements.
Your responsibilities:
- Identify strengths and weaknesses
- Provide specific, actionable feedback
- Suggest concrete improvements
- Ensure quality standards are met
- Balance criticism with encouragement
Review Framework:
1. STRENGTHS: What works well?
2. WEAKNESSES: What needs improvement?
3. SUGGESTIONS: Specific recommendations
4. PRIORITY: What to fix first?
Guidelines:
- Be specific, not vague
- Focus on improvement, not just problems
- Provide examples when possible
- Consider the intended audience
- Balance critical and positive feedback`,
    defaultModel: 'gpt-4o-mini',
    defaultConfig: {
      temperature: 0.6,
      max_tokens: 2000,
      hitl_gates: {
        before: false,
        after: false,
        on_demand: true
      }
    }
  },
  {
    id: 'planner',
    name: 'Planner',
    role: 'planner',
    icon: '📋',
    description: 'Creates structured plans and strategies',
    systemPrompt: `You are a strategic planner who creates detailed, actionable plans.
Your responsibilities:
- Break down complex goals into steps
- Identify resources and requirements
- Establish timelines and milestones
- Anticipate challenges and risks
- Create clear action plans
Planning Framework:
1. OBJECTIVE: Clear goal definition
2. STRATEGY: High-level approach
3. TACTICS: Specific action steps
4. RESOURCES: What's needed
5. TIMELINE: When things happen
6. RISKS: Potential obstacles
Guidelines:
- Be specific and actionable
- Include success metrics
- Consider dependencies
- Plan for contingencies
- Make it easy to follow`,
    defaultModel: 'gpt-4o',
    defaultConfig: {
      temperature: 0.6,
      max_tokens: 2500,
      hitl_gates: {
        before: false,
        after: true,
        on_demand: false
      }
    }
  }
];
// Model options for selector
export const MODEL_OPTIONS = [
  {
    value: 'gpt-4o',
    label: 'GPT-4o',
    provider: 'OpenAI',
    description: 'Most capable, balanced performance'
  },
  {
    value: 'gpt-4o-mini',
    label: 'GPT-4o Mini',
    provider: 'OpenAI',
    description: 'Faster, cost-effective'
  },
  {
    value: 'claude-3-5-sonnet-20241022',
    label: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    description: 'Excellent for analysis and writing'
  },
  {
    value: 'claude-3-5-haiku-20241022',
    label: 'Claude 3.5 Haiku',
    provider: 'Anthropic',
    description: 'Fast, efficient'
  }
];
7.4 State Management (Zustand)
// frontend/src/store/flowStore.ts
import { create } from 'zustand';
import { Node, Edge } from 'reactflow';
interface FlowState {
  // Flow data
  flowId: string | null;
  flowName: string;
  nodes: Node[];
  edges: Edge[];
  selectedNode: Node | null;
  
  // Execution state
  executionId: string | null;
  executionStatus: 'idle' | 'running' | 'paused' | 'completed' | 'failed';
  currentStep: number;
  totalSteps: number;
  
  // HITL state
  pendingReviews: HITLReview[];
  activeReview: HITLReview | null;
  
  // Actions
  setFlowId: (id: string) => void;
  setFlowName: (name: string) => void;
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  addNode: (node: Node) => void;
  updateNode: (nodeId: string, updates: Partial<Node>) => void;
  removeNode: (nodeId: string) => void;
  selectNode: (node: Node | null) => void;
  
  startExecution: (executionId: string) => void;
  updateExecutionStatus: (status: ExecutionStatus) => void;
  updateExecutionProgress: (current: number, total: number) => void;
  
  addPendingReview: (review: HITLReview) => void;
  removePendingReview: (reviewId: string) => void;
  setActiveReview: (review: HITLReview | null) => void;
  
  resetFlow: () => void;
}
export const useFlowStore = create<FlowState>((set) => ({
  // Initial state
  flowId: null,
  flowName: 'Untitled Flow',
  nodes: [],
  edges: [],
  selectedNode: null,
  executionId: null,
  executionStatus: 'idle',
  currentStep: 0,
  totalSteps: 0,
  pendingReviews: [],
  activeReview: null,
  
  // Actions
  setFlowId: (id) => set({ flowId: id }),
  setFlowName: (name) => set({ flowName: name }),
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  
  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node]
  })),
  
  updateNode: (nodeId, updates) => set((state) => ({
    nodes: state.nodes.map(node =>
      node.id === nodeId ? { ...node, ...updates } : node
    )
  })),
  
  removeNode: (nodeId) => set((state) => ({
    nodes: state.nodes.filter(node => node.id !== nodeId),
    edges: state.edges.filter(edge =>
      edge.source !== nodeId && edge.target !== nodeId
    )
  })),
  
  selectNode: (node) => set({ selectedNode: node }),
  
  startExecution: (executionId) => set({
    executionId,
    executionStatus: 'running',
    currentStep: 0
  }),
  
  updateExecutionStatus: (status) => set({ executionStatus: status }),
  
  updateExecutionProgress: (current, total) => set({
    currentStep: current,
    totalSteps: total
  }),
  
  addPendingReview: (review) => set((state) => ({
    pendingReviews: [...state.pendingReviews, review]
  })),
  
  removePendingReview: (reviewId) => set((state) => ({
    pendingReviews: state.pendingReviews.filter(r => r.id !== reviewId)
  })),
  
  setActiveReview: (review) => set({ activeReview: review }),
  
  resetFlow: () => set({
    flowId: null,
    flowName: 'Untitled Flow',
    nodes: [],
    edges: [],
    selectedNode: null,
    executionId: null,
    executionStatus: 'idle',
    currentStep: 0,
    totalSteps: 0,
    pendingReviews: [],
    activeReview: null
  })
}));
---
8. BACKEND DESIGN
8.1 Core Module: Flow Executor
# backend/app/core/flow_executor.py
from typing import Dict, List, Optional
from uuid import UUID
import asyncio
import json
from datetime import datetime

# STEP_TIMEOUT_SECONDS: max time to wait for a single LLM call before
# treating the step as failed and triggering retry / error path.
STEP_TIMEOUT_SECONDS = 120

class FlowExecutor:
    """
    Executes flows step-by-step with memory and HITL integration.
    
    Dependencies injected via __init__ (no global state):
      - db               : AsyncDatabase  — PostgreSQL async wrapper
      - agent_manager    : AgentManager   — creates / caches agent instances
      - memory_manager   : MemoryManager  — short/long-term memory
      - hitl_manager     : HITLManager    — HITL review queue
      - websocket_manager: WebSocketManager — pub/sub to frontend
      - logger           : LoggerService  — structured event logging
    """

    def __init__(
        self,
        db,                    # AsyncDatabase (asyncpg pool wrapper)
        agent_manager,         # AgentManager
        memory_manager,        # MemoryManager
        hitl_manager,          # HITLManager
        websocket_manager,     # WebSocketManager
        logger_service,        # LoggerService
    ):
        self.db = db
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager
        self.hitl_manager = hitl_manager
        self.ws = websocket_manager
        self.logger = logger_service

    # ------------------------------------------------------------------
    # Public: execute a full sequential flow
    # ------------------------------------------------------------------
    async def execute_sequential(
        self,
        flow_id: UUID,
        execution_id: UUID,
        initial_input: str
    ) -> Dict:
        """
        Execute a sequential flow.

        Flow:
        1. Load flow configuration from PostgreSQL
        2. Initialize memory (Redis + MongoDB)
        3. For each agent node in order:
           a. Check HITL before gate (if enabled)
           b. Execute agent with timeout + retry
           c. Save output to memory
           d. Log step completion
           e. Check HITL after gate (if enabled)
           f. If rejected → re-run with feedback, then re-check
        4. Finalise: update execution record, emit WebSocket event
        """

        # Load flow configuration
        flow = await self.load_flow(flow_id)
        nodes = self.parse_nodes(flow["flow_config"])

        # Initialise execution record in PostgreSQL
        await self.db.execute(
            """
            UPDATE flow_executions
            SET status = 'running', total_steps = $1, current_step = 0
            WHERE id = $2
            """,
            len(nodes), execution_id
        )

        # Initialise memory for this flow
        await self.memory_manager.initialize_flow_memory(flow_id)

        # Execution context — grows as steps complete
        context: Dict = {
            "initial_input": initial_input,
            "flow_id": str(flow_id),
            "execution_id": str(execution_id),
        }

        results: Dict = {}

        # Execute each node sequentially
        for step_number, node in enumerate(nodes, start=1):
            try:
                await self._update_status(
                    execution_id, status="running", current_step=step_number
                )

                await self.logger.log_event(
                    execution_id=execution_id,
                    event_type="step_start",
                    step_number=step_number,
                    agent_id=node["agent_id"],
                )

                agent = await self.agent_manager.get_agent(node["agent_id"])

                # Build full context (shared memory + history)
                agent_context = await self.memory_manager.get_context_for_agent(
                    flow_id=flow_id,
                    agent_id=node["agent_id"],
                    execution_context=context,
                )
                full_context = {**context, **agent_context}

                # HITL gate: before execution
                if node.get("config", {}).get("hitl_gates", {}).get("before"):
                    await self._handle_hitl_gate(
                        execution_id=execution_id,
                        step_number=step_number,
                        agent_id=node["agent_id"],
                        gate_type="before",
                        data_to_review=full_context,
                    )

                # Execute agent (with per-step timeout + retry)
                step_result = await self._execute_agent_with_retry(
                    agent=agent,
                    context=full_context,
                    node_config=node.get("config", {}),
                    execution_id=execution_id,
                    step_number=step_number,
                )

                # Persist step record to PostgreSQL
                await self.db.execute(
                    """
                    INSERT INTO step_executions
                        (execution_id, agent_id, step_number,
                         input_data, output_data, status, completed_at)
                    VALUES ($1, $2, $3, $4, $5, 'completed', NOW())
                    ON CONFLICT (execution_id, step_number)
                    DO UPDATE SET output_data = EXCLUDED.output_data,
                                  status = 'completed',
                                  completed_at = NOW()
                    """,
                    execution_id,
                    node["agent_id"],
                    step_number,
                    json.dumps(full_context),
                    json.dumps(step_result),
                )

                # Write to memory (Redis short-term + MongoDB long-term)
                await self.memory_manager.add_to_memory(
                    flow_id=flow_id,
                    agent_id=node["agent_id"],
                    data=step_result,
                )

                await self.logger.log_event(
                    execution_id=execution_id,
                    event_type="step_completed",
                    step_number=step_number,
                    output=step_result,
                )

                # HITL gate: after execution
                if node.get("config", {}).get("hitl_gates", {}).get("after"):
                    approval = await self._handle_hitl_gate(
                        execution_id=execution_id,
                        step_number=step_number,
                        agent_id=node["agent_id"],
                        gate_type="after",
                        data_to_review=step_result,
                    )

                    # Rejected → re-run with human feedback, then re-check
                    if not approval["approved"]:
                        step_result = await self._rerun_with_feedback(
                            agent=agent,
                            original_context=full_context,
                            original_output=step_result,
                            feedback=approval["comments"],
                        )
                        await self.memory_manager.add_to_memory(
                            flow_id=flow_id,
                            agent_id=node["agent_id"],
                            data=step_result,
                        )

                # Record analytics event (triggers DB aggregate update)
                await self.db.execute(
                    """
                    INSERT INTO agent_execution_events
                        (agent_id, execution_id, step_number, status, llm_calls)
                    VALUES ($1, $2, $3, 'completed', 1)
                    """,
                    node["agent_id"], execution_id, step_number,
                )

                # Propagate output to subsequent steps
                context[f"step_{step_number}_output"] = step_result
                results[str(node["agent_id"])] = step_result

                await self._notify_step_completion(
                    execution_id=execution_id,
                    step_number=step_number,
                    agent_name=node.get("name", "Agent"),
                    result=step_result,
                )

            except Exception as e:
                await self._handle_step_failure(
                    execution_id=execution_id,
                    step_number=step_number,
                    agent_id=node.get("agent_id"),
                    error=e,
                )
                return {"status": "failed", "step": step_number, "error": str(e)}

        # All steps done — finalise
        await self._finalize_execution(
            execution_id=execution_id,
            total_steps=len(nodes),
            results=results,
        )
        return {"status": "completed", "results": results}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def load_flow(self, flow_id: UUID) -> Dict:
        row = await self.db.fetchrow(
            "SELECT * FROM flows WHERE id = $1", flow_id
        )
        if not row:
            raise ValueError(f"Flow {flow_id} not found")
        return dict(row)

    def parse_nodes(self, flow_config: Dict) -> List[Dict]:
        """
        Extract ordered agent nodes from React Flow config.
        Filters out 'start' and 'end' meta-nodes, returns only agent nodes.
        """
        nodes = [n for n in flow_config.get("nodes", []) if n.get("type") == "agent"]
        edges = flow_config.get("edges", [])

        # Build topological order from edges
        order_map: Dict[str, int] = {}
        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            src_order = order_map.get(src, 0)
            order_map[tgt] = max(order_map.get(tgt, 0), src_order + 1)

        nodes.sort(key=lambda n: order_map.get(n["id"], 0))
        return [n["data"] for n in nodes]

    async def _update_status(
        self,
        execution_id: UUID,
        status: str,
        current_step: int = None,
    ):
        if current_step is not None:
            await self.db.execute(
                """
                UPDATE flow_executions
                SET status = $1, current_step = $2
                WHERE id = $3
                """,
                status, current_step, execution_id,
            )
        else:
            await self.db.execute(
                "UPDATE flow_executions SET status = $1 WHERE id = $2",
                status, execution_id,
            )

    async def _handle_hitl_gate(
        self,
        execution_id: UUID,
        step_number: int,
        agent_id: UUID,
        gate_type: str,
        data_to_review: Dict,
    ) -> Dict:
        """
        Create a HITL review, pause execution, wait for human decision.

        Returns:
            {'approved': bool, 'comments': str}
        """
        review_id = await self.hitl_manager.create_review(
            execution_id=execution_id,
            step_number=step_number,
            agent_id=agent_id,
            gate_type=gate_type,
            data_to_review=data_to_review,
        )

        await self._update_status(execution_id, status="paused_hitl")

        # wait_for_approval uses Redis pub/sub — no polling
        approval = await self.hitl_manager.wait_for_approval(review_id)

        await self._update_status(execution_id, status="running")
        return approval

    async def _rerun_with_feedback(
        self,
        agent,
        original_context: Dict,
        original_output: Dict,
        feedback: str,
    ) -> Dict:
        """Re-run an agent, injecting the human reviewer's feedback."""
        enhanced_context = {
            **original_context,
            "previous_attempt": original_output,
            "human_feedback": feedback,
            "instruction": (
                f"Your previous output was rejected by a human reviewer. "
                f"Please address this specific feedback and improve your response: {feedback}"
            ),
        }
        return await agent.run(enhanced_context)

    async def _execute_agent_with_retry(
        self,
        agent,
        context: Dict,
        node_config: Dict,
        execution_id: UUID,
        step_number: int,
    ) -> Dict:
        """
        Execute an agent with:
          - per-call timeout (STEP_TIMEOUT_SECONDS)
          - exponential backoff retry up to max_retries
        """
        max_retries = node_config.get("max_retries", 3)

        for attempt in range(max_retries + 1):
            try:
                # Enforce a hard timeout per LLM call
                result = await asyncio.wait_for(
                    agent.run(context),
                    timeout=STEP_TIMEOUT_SECONDS,
                )
                return result

            except asyncio.TimeoutError:
                err_msg = (
                    f"Step {step_number} timed out after "
                    f"{STEP_TIMEOUT_SECONDS}s (attempt {attempt + 1}/{max_retries + 1})"
                )
                await self.logger.log_event(
                    execution_id=execution_id,
                    event_type="step_timeout",
                    step_number=step_number,
                    message=err_msg,
                )
                if attempt == max_retries:
                    raise TimeoutError(err_msg)

            except Exception as e:
                await self.logger.log_event(
                    execution_id=execution_id,
                    event_type="step_retry",
                    step_number=step_number,
                    attempt=attempt + 1,
                    error=str(e),
                )
                if attempt == max_retries:
                    raise

            # Exponential backoff before next attempt
            backoff = 2 ** attempt  # 1s, 2s, 4s, 8s …
            await asyncio.sleep(backoff)

        # Should be unreachable, but satisfies type checker
        raise RuntimeError("execute_agent_with_retry exhausted all attempts")

    async def _notify_step_completion(
        self,
        execution_id: UUID,
        step_number: int,
        agent_name: str,
        result: Dict,
    ):
        await self.ws.emit(
            channel=f"execution:{execution_id}",
            event="step_completed",
            data={
                "execution_id": str(execution_id),
                "step_number": step_number,
                "agent_name": agent_name,
                "status": "success",
                "output": result.get("content", ""),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _handle_step_failure(
        self,
        execution_id: UUID,
        step_number: int,
        agent_id: Optional[UUID],
        error: Exception,
    ):
        await self._update_status(execution_id, status="failed")

        await self.logger.log_event(
            execution_id=execution_id,
            event_type="step_failed",
            step_number=step_number,
            error=str(error),
        )

        if agent_id:
            await self.db.execute(
                """
                INSERT INTO agent_execution_events
                    (agent_id, execution_id, step_number, status)
                VALUES ($1, $2, $3, 'failed')
                """,
                agent_id, execution_id, step_number,
            )

        await self.ws.emit(
            channel=f"execution:{execution_id}",
            event="execution_failed",
            data={
                "execution_id": str(execution_id),
                "step_number": step_number,
                "error_message": str(error),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _finalize_execution(
        self,
        execution_id: UUID,
        total_steps: int,
        results: Dict,
    ):
        await self.db.execute(
            """
            UPDATE flow_executions
            SET status = 'completed',
                completed_at = NOW(),
                completed_steps = $1,
                success_rate = 100.0
            WHERE id = $2
            """,
            total_steps, execution_id,
        )

        await self.ws.emit(
            channel=f"execution:{execution_id}",
            event="execution_completed",
            data={
                "execution_id": str(execution_id),
                "status": "completed",
                "total_steps": total_steps,
                "success_rate": 100.0,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
8.2 Core Module: Memory Manager
# backend/app/memory/memory_manager.py
from typing import Dict, List, Optional
from uuid import UUID
import json
class MemoryManager:
    """
    Manages memory across flow executions
    
    Three types of memory:
    1. Short-term (Redis) - Current execution session
    2. Long-term (MongoDB) - Historical executions
    3. Persistent (MongoDB) - Accumulated knowledge
    """
    
    def __init__(
        self,
        redis_client,
        mongodb_client,
        postgres_db
    ):
        self.redis = redis_client
        self.mongodb = mongodb_client
        self.db = postgres_db
        
    async def initialize_flow_memory(self, flow_id: UUID):
        """
        Initialize memory for a new flow execution
        """
        
        # Check if flow memory exists in MongoDB
        flow_memory = await self.mongodb.flow_memory.find_one({
            'flow_id': str(flow_id)
        })
        
        if not flow_memory:
            # Create new flow memory document
            await self.mongodb.flow_memory.insert_one({
                'flow_id': str(flow_id),
                'shared_memory': {
                    'conversation_history': [],
                    'accumulated_facts': [],
                    'key_insights': []
                },
                'agent_memories': {},
                'metadata': {
                    'total_executions': 0,
                    'created_at': datetime.utcnow()
                }
            })
    
    async def add_to_memory(
        self,
        flow_id: UUID,
        agent_id: UUID,
        data: Dict
    ):
        """
        Add data to memory (both short-term and long-term)
        """
        
        # Add to Redis (short-term, current session)
        await self.redis.hset(
            f"memory:{flow_id}:shared",
            str(agent_id),
            json.dumps(data)
        )
        
        # Add to MongoDB (long-term, persistent)
        await self.mongodb.flow_memory.update_one(
            {'flow_id': str(flow_id)},
            {
                '$push': {
                    'shared_memory.conversation_history': {
                        'agent_id': str(agent_id),
                        'timestamp': datetime.utcnow(),
                        'output': data
                    }
                },
                '$set': {
                    'metadata.last_updated': datetime.utcnow()
                }
            }
        )
        
        # Update agent-specific memory
        await self.update_agent_memory(flow_id, agent_id, data)
    
    async def get_context_for_agent(
        self,
        flow_id: UUID,
        agent_id: UUID,
        execution_context: Dict
    ) -> Dict:
        """
        Build complete context for agent execution
        
        Includes:
        - Shared memory from current execution (Redis)
        - Historical executions (MongoDB)
        - Agent-specific learnings (MongoDB)
        """
        
        # Get short-term shared memory (current execution)
        shared_memory = await self.redis.hgetall(f"memory:{flow_id}:shared")
        shared_memory_parsed = {
            k: json.loads(v) for k, v in shared_memory.items()
        }
        
        # Get long-term flow memory (historical)
        flow_memory = await self.mongodb.flow_memory.find_one({
            'flow_id': str(flow_id)
        })
        
        # Get execution history (last 5 runs)
        execution_history = await self.mongodb.execution_history.find({
            'flow_id': str(flow_id),
            'status': 'completed'
        }).sort('started_at', -1).limit(5).to_list(length=5)
        
        # Build context
        context = {
            'shared_memory': shared_memory_parsed,
            'execution_history': [
                {
                    'date': eh['started_at'],
                    'outputs': self.extract_outputs(eh),
                    'status': eh['status']
                }
                for eh in execution_history
            ],
            'agent_memory': flow_memory.get('agent_memories', {}).get(str(agent_id), {}),
            'accumulated_knowledge': {
                'facts': flow_memory.get('shared_memory', {}).get('accumulated_facts', []),
                'insights': flow_memory.get('shared_memory', {}).get('key_insights', [])
            }
        }
        
        return context
    
    async def update_agent_memory(
        self,
        flow_id: UUID,
        agent_id: UUID,
        data: Dict
    ):
        """
        Update agent-specific memory
        """
        
        await self.mongodb.flow_memory.update_one(
            {'flow_id': str(flow_id)},
            {
                '$set': {
                    f'agent_memories.{agent_id}.last_output': data,
                    f'agent_memories.{agent_id}.last_execution': datetime.utcnow()
                },
                '$inc': {
                    f'agent_memories.{agent_id}.execution_count': 1
                }
            },
            upsert=True
        )
    
    def extract_outputs(self, execution_history: Dict) -> Dict:
        """
        Extract agent outputs from execution log
        """
        
        outputs = {}
        for log_entry in execution_history.get('execution_log', []):
            if log_entry.get('event_type') == 'step_completed':
                agent_name = log_entry.get('agent_name')
                output = log_entry.get('output')
                outputs[agent_name] = output
        
        return outputs
8.3 Core Module: HITL Manager
# backend/app/core/hitl_manager.py
from typing import Dict, Optional
from uuid import UUID, uuid4
import asyncio
import json

# Maximum seconds to wait for a human review before timing out.
# After timeout the execution is marked 'failed' so it doesn't
# block indefinitely.
HITL_TIMEOUT_SECONDS = 3600  # 1 hour


class HITLManager:
    """
    Manages Human-in-the-Loop approval gates.

    Uses Redis pub/sub to signal approval/rejection so that
    wait_for_approval() unblocks instantly with zero polling.

    Channel naming convention:
        hitl:result:{review_id}   ← backend publishes here on approve/reject
    """

    def __init__(
        self,
        redis_client,      # aioredis or redis.asyncio client
        postgres_db,       # AsyncDatabase wrapper
        websocket_manager, # WebSocketManager
    ):
        self.redis = redis_client
        self.db = postgres_db
        self.ws = websocket_manager

    async def create_review(
        self,
        execution_id: UUID,
        step_number: int,
        agent_id: UUID,
        gate_type: str,
        data_to_review: Dict,
    ) -> UUID:
        """
        Persist a HITL review request and notify the frontend.

        Returns the new review_id.
        """
        review_id = uuid4()

        # Persist to PostgreSQL (source of truth)
        await self.db.execute(
            """
            INSERT INTO hitl_reviews
                (id, execution_id, agent_id, gate_type,
                 status, output_to_review, created_at)
            VALUES ($1, $2, $3, $4, 'pending', $5, NOW())
            """,
            review_id,
            execution_id,
            agent_id,
            gate_type,
            json.dumps(data_to_review),
        )

        # Add review_id to the Redis work queue for the HITL dashboard
        await self.redis.lpush("hitl:queue", str(review_id))

        # Notify frontend via WebSocket so the modal appears immediately
        await self.ws.emit(
            channel=f"execution:{execution_id}",
            event="hitl_review_needed",
            data={
                "review_id": str(review_id),
                "execution_id": str(execution_id),
                "gate_type": gate_type,
                "agent_id": str(agent_id),
                "step_number": step_number,
            },
        )

        return review_id

    async def wait_for_approval(
        self,
        review_id: UUID,
        timeout: int = HITL_TIMEOUT_SECONDS,
    ) -> Dict:
        """
        Block the flow executor coroutine until a human approves or
        rejects the review — OR until timeout is reached.

        Implementation:
            Uses Redis pub/sub on channel  hitl:result:{review_id}.
            approve_review() / reject_review() each PUBLISH to that
            channel, which unblocks this coroutine immediately with
            zero DB polling overhead.

        Returns:
            {'approved': bool, 'comments': str}

        Raises:
            asyncio.TimeoutError if no decision within `timeout` seconds.
        """
        channel = f"hitl:result:{review_id}"

        # Subscribe *before* checking current status to avoid the race
        # condition where approval arrives between the status check and
        # the subscribe call.
        async with self.redis.pubsub() as pubsub:
            await pubsub.subscribe(channel)

            # Race-free guard: if the review was already decided
            # (e.g. approved programmatically before we subscribed),
            # return immediately without waiting.
            existing = await self.db.fetchrow(
                "SELECT status, reviewer_comments FROM hitl_reviews WHERE id = $1",
                review_id,
            )
            if existing and existing["status"] in ("approved", "rejected"):
                await pubsub.unsubscribe(channel)
                return {
                    "approved": existing["status"] == "approved",
                    "comments": existing["reviewer_comments"] or "",
                }

            # Wait for the pub/sub message with a hard timeout
            try:
                async with asyncio.timeout(timeout):
                    async for message in pubsub.listen():
                        if message["type"] != "message":
                            continue
                        payload = json.loads(message["data"])
                        return {
                            "approved": payload["approved"],
                            "comments": payload.get("comments", ""),
                        }
            except asyncio.TimeoutError:
                raise asyncio.TimeoutError(
                    f"HITL review {review_id} timed out after {timeout}s. "
                    "Execution has been marked as failed."
                )

    async def approve_review(
        self,
        review_id: UUID,
        comments: Optional[str] = None,
    ):
        """
        Called by the API endpoint when a human approves.
        Persists decision to PostgreSQL, cleans up Redis queue,
        and publishes to the pub/sub channel to unblock wait_for_approval.
        """
        # 1. Update PostgreSQL (source of truth)
        row = await self.db.fetchrow(
            """
            UPDATE hitl_reviews
            SET status = 'approved',
                reviewer_comments = $2,
                reviewed_at = NOW()
            WHERE id = $1
            RETURNING execution_id
            """,
            review_id,
            comments,
        )

        # 2. Remove from Redis work queue
        await self.redis.lrem("hitl:queue", 1, str(review_id))

        # 3. Publish decision — unblocks wait_for_approval instantly
        await self.redis.publish(
            f"hitl:result:{review_id}",
            json.dumps({"approved": True, "comments": comments or ""}),
        )

        # 4. Notify frontend
        await self.ws.emit(
            channel=f"execution:{row['execution_id']}",
            event="hitl_review_completed",
            data={
                "review_id": str(review_id),
                "status": "approved",
                "comments": comments,
            },
        )

    async def reject_review(
        self,
        review_id: UUID,
        comments: str,
    ):
        """
        Called by the API endpoint when a human rejects.
        Persists decision, cleans up queue, and publishes to unblock
        wait_for_approval so the executor can re-run the step.
        """
        if not comments:
            raise ValueError("Comments are required when rejecting a review")

        # 1. Update PostgreSQL
        row = await self.db.fetchrow(
            """
            UPDATE hitl_reviews
            SET status = 'rejected',
                reviewer_comments = $2,
                reviewed_at = NOW()
            WHERE id = $1
            RETURNING execution_id
            """,
            review_id,
            comments,
        )

        # 2. Remove from Redis work queue
        await self.redis.lrem("hitl:queue", 1, str(review_id))

        # 3. Publish decision — unblocks wait_for_approval instantly
        await self.redis.publish(
            f"hitl:result:{review_id}",
            json.dumps({"approved": False, "comments": comments}),
        )

        # 4. Notify frontend
        await self.ws.emit(
            channel=f"execution:{row['execution_id']}",
            event="hitl_review_completed",
            data={
                "review_id": str(review_id),
                "status": "rejected",
                "comments": comments,
            },
        )

    async def get_pending_reviews(self) -> list:
        """Return all reviews with status = 'pending', ordered oldest first."""
        rows = await self.db.fetch(
            """
            SELECT
                hr.id            AS review_id,
                hr.execution_id,
                hr.agent_id,
                a.name           AS agent_name,
                hr.gate_type,
                hr.output_to_review,
                hr.created_at
            FROM hitl_reviews hr
            JOIN agents a ON hr.agent_id = a.id
            WHERE hr.status = 'pending'
            ORDER BY hr.created_at ASC
            """
        )
        return [dict(r) for r in rows]
8.4 Service: LLM Service (LiteLLM Integration)
# backend/app/services/llm_service.py
from litellm import acompletion
from typing import Dict, Optional
import asyncio
import time

# Default retry policy for LLM calls.
# Override per-call via the max_retries / retry_on parameters.
DEFAULT_MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2   # back-off = BASE_BACKOFF_SECONDS ** attempt


class LLMService:
    """
    Unified LLM service using LiteLLM.
    Supports multiple models via DialKey proxy or direct provider keys.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Args:
            api_key  : DialKey proxy key, or a direct OpenAI / Anthropic key.
            base_url : DialKey base URL if using a proxy.
                       Leave None to call providers directly.
        """
        import litellm
        litellm.api_key = api_key
        if base_url:
            litellm.api_base = base_url
        self._litellm = litellm

    async def generate(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        context: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> Dict:
        """
        Generate a completion from the specified model.

        Retry policy:
          - Retries up to `max_retries` times on rate-limit (429) errors
            and transient network errors.
          - Uses exponential back-off: BASE_BACKOFF_SECONDS ** attempt
            (i.e. 2s, 4s, 8s for DEFAULT_MAX_RETRIES=3).
          - Non-retriable errors (e.g. 400 bad request, 401 auth) are
            raised immediately without retrying.

        Returns:
            {
                'content': str,
                'metadata': {
                    'model': str,
                    'tokens_used': int,
                    'latency_ms': int,
                    'finish_reason': str,
                }
            }

        Raises:
            Exception on non-retriable errors or after all retries exhausted.
        """
        messages = [{"role": "system", "content": system_prompt}]

        if context:
            context_text = self._format_context(context)
            messages.append({"role": "system", "content": f"Context:\n{context_text}"})

        messages.append({"role": "user", "content": user_message})

        last_exception: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            start_time = time.monotonic()
            try:
                response = await acompletion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency_ms = int((time.monotonic() - start_time) * 1000)

                return {
                    "content": response.choices[0].message.content,
                    "metadata": {
                        "model": model,
                        "tokens_used": response.usage.total_tokens,
                        "latency_ms": latency_ms,
                        "finish_reason": response.choices[0].finish_reason,
                    },
                }

            except Exception as e:
                last_exception = e
                error_str = str(e).lower()

                # Determine whether this error is worth retrying
                is_rate_limit = "rate_limit" in error_str or "429" in error_str
                is_transient  = any(
                    kw in error_str
                    for kw in ("timeout", "connection", "service unavailable", "503")
                )

                if not (is_rate_limit or is_transient):
                    # Non-retriable — fail immediately
                    raise

                if attempt == max_retries:
                    # Exhausted all attempts
                    break

                # Exponential back-off before next attempt
                backoff = BASE_BACKOFF_SECONDS ** (attempt + 1)
                await asyncio.sleep(backoff)

        # All retries exhausted
        raise RuntimeError(
            f"LLM call to '{model}' failed after {max_retries + 1} attempts. "
            f"Last error: {last_exception}"
        ) from last_exception

    def _format_context(self, context: Dict) -> str:
        """
        Render the context dictionary as human-readable text injected
        into the system prompt.  Truncates execution history to last 5
        runs and caps each output at 500 characters to avoid blowing
        the model's context window.
        """
        sections: list[str] = []

        # Shared memory from the current execution session
        if context.get("shared_memory"):
            sections.append("=== Shared Memory (Current Execution) ===")
            for agent_id, data in context["shared_memory"].items():
                sections.append(f"Agent {agent_id}: {str(data)[:500]}")

        # Historical execution outputs (capped to last 5 runs)
        history = context.get("execution_history", [])
        if history:
            sections.append("\n=== Execution History (Last 5 Runs) ===")
            for i, execution in enumerate(history[-5:], 1):
                sections.append(f"\nRun #{i} ({execution.get('date', 'unknown')}):")
                for agent_name, output in execution.get("outputs", {}).items():
                    sections.append(f"  {agent_name}: {str(output)[:500]}...")

        # Agent-specific long-term memory
        agent_mem = context.get("agent_memory", {})
        if agent_mem:
            sections.append("\n=== Your Previous Work ===")
            if "execution_count" in agent_mem:
                sections.append(
                    f"You have been executed {agent_mem['execution_count']} time(s)."
                )
            for pattern in agent_mem.get("learned_patterns", []):
                sections.append(f"  - {pattern}")

        # Accumulated facts / insights
        knowledge = context.get("accumulated_knowledge", {})
        if knowledge.get("facts"):
            sections.append("\n=== Key Facts ===")
            for fact in knowledge["facts"][:5]:
                sections.append(f"  - {fact}")

        return "\n".join(sections)
---
9. IMPLEMENTATION TIMELINE (14 DAYS)
Week 1: Backend Foundation
Day 1 (4 hours): Project Setup
- [ ] Create project structure
- [ ] Set up Docker Compose (PostgreSQL, MongoDB, Redis)
- [ ] Initialize FastAPI backend
- [ ] Create database connections
- [ ] Test all services running
- [ ] Create health check endpoint
Deliverables: Docker services running, backend connects to DBs
---
Day 2 (4 hours): Database Schema & Models
- [ ] Create PostgreSQL schema (flows, agents, executions, hitl_reviews, analytics)
- [ ] Create SQLAlchemy models
- [ ] Create Pydantic schemas
- [ ] Write migration script
- [ ] Design MongoDB collections
- [ ] Test CRUD operations
Deliverables: All tables created, models working
---
Day 3 (4 hours): LLM Integration & Base Agent
- [ ] Set up LiteLLM with DialKey
- [ ] Create LLMService class
- [ ] Implement BaseAgent class
- [ ] Create ConversationalAgent
- [ ] Test agent execution with GPT-4o
- [ ] Implement agent factory pattern
Deliverables: Can create and execute agents
---
Day 4 (4 hours): Memory Management System
- [ ] Implement MemoryManager class
- [ ] Create SharedMemory (Redis)
- [ ] Create PersistentStore (MongoDB)
- [ ] Implement ContextManager
- [ ] Test memory persistence across executions
- [ ] Test context building for agents
Deliverables: Memory system working, agents receive context
---
Day 5 (4 hours): Flow Executor (Sequential)
- [ ] Implement FlowExecutor class
- [ ] Build sequential execution logic
- [ ] Integrate memory updates per step
- [ ] Add error handling and retries
- [ ] Implement logging to MongoDB
- [ ] Test end-to-end execution
Deliverables: Can execute sequential flows
---
Day 6 (4 hours): HITL System
- [ ] Implement HITLManager class
- [ ] Create review queue (Redis)
- [ ] Build approval/rejection logic
- [ ] Integrate HITL gates into FlowExecutor
- [ ] Implement re-run logic on rejection
- [ ] Test HITL flow
Deliverables: HITL gates working, rejection re-runs agent
---
Day 7 (4 hours): API Endpoints
- [ ] Create flow endpoints (CRUD)
- [ ] Create agent endpoints
- [ ] Create execution endpoints
- [ ] Create HITL endpoints
- [ ] Implement WebSocket for real-time updates
- [ ] Test all endpoints with Postman
Deliverables: Complete REST API working
---
Week 2: Frontend & Integration
Day 8 (4 hours): Frontend Setup & Canvas
- [ ] Initialize Vite + React + TypeScript
- [ ] Set up Tailwind CSS
- [ ] Install React Flow
- [ ] Create basic canvas component
- [ ] Add zoom/pan controls
- [ ] Create custom AgentNode component
- [ ] Test drag-and-drop on canvas
Deliverables: Canvas renders, can add nodes
---
Day 9 (4 hours): Agent Configuration Panel
- [ ] Create AgentConfigPanel component
- [ ] Build pre-built agent templates
- [ ] Add Monaco Editor for system prompts
- [ ] Create role selector dropdown
- [ ] Create model selector dropdown
- [ ] Add HITL toggles
- [ ] Implement drag from palette to canvas
Deliverables: Can configure agents fully in UI
---
Day 10 (4 hours): Flow Management (Save/Load)
- [ ] Create SaveFlowDialog component
- [ ] Implement save flow API call
- [ ] Create LoadFlowDialog component
- [ ] Fetch and display saved flows
- [ ] Load selected flow into canvas
- [ ] Test save/load roundtrip
Deliverables: Flows persist, can load them
---
Day 11 (4 hours): Execution UI & HITL Queue
- [ ] Create ExecutionViewer component
- [ ] Add "Run Flow" button
- [ ] Display execution progress
- [ ] Create HITLQueue component
- [ ] Build HITLModal component
- [ ] Implement approve/reject actions
- [ ] Test HITL workflow in UI
Deliverables: Can run flows and review HITL gates
---
Day 12 (4 hours): WebSocket Integration
- [ ] Set up Socket.IO client
- [ ] Connect to backend WebSocket
- [ ] Subscribe to execution channels
- [ ] Handle real-time events
- [ ] Update UI on step completion
- [ ] Show HITL notifications
- [ ] Test real-time updates
Deliverables: Real-time execution updates working
---
Day 13 (4 hours): Analytics Dashboard
- [ ] Create AnalyticsDashboard component
- [ ] Implement analytics API endpoints
- [ ] Display success/failure rates
- [ ] Create agent performance chart (Recharts)
- [ ] Build execution logs viewer
- [ ] Test analytics calculations
Deliverables: Analytics dashboard functional
---
Day 14 (4 hours): Polish, Testing & Documentation
- [ ] Fix bugs
- [ ] Improve UI styling
- [ ] Add loading states
- [ ] Add error handling
- [ ] Write README.md
- [ ] Document API endpoints
- [ ] Create user guide
- [ ] End-to-end integration test
Deliverables: Polished POC ready to demo
---
10. DEPLOYMENT STRATEGY
10.1 Local Development (Docker Compose)
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: orchestrator-postgres
    environment:
      POSTGRES_DB: orchestrator
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/app/db/migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5
  mongodb:
    image: mongo:7
    container_name: orchestrator-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
      MONGO_INITDB_DATABASE: orchestrator
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/orchestrator --quiet
      interval: 10s
      timeout: 5s
      retries: 5
  redis:
    image: redis:7-alpine
    container_name: orchestrator-redis
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: orchestrator-backend
    environment:
      DATABASE_URL: postgresql://admin:admin123@postgres:5432/orchestrator
      MONGODB_URL: mongodb://admin:admin123@mongodb:27017/orchestrator
      REDIS_URL: redis://redis:6379
      DIALKEY_API_KEY: ${DIALKEY_API_KEY}
      DIALKEY_BASE_URL: ${DIALKEY_BASE_URL}
      API_KEY: ${API_KEY}
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      mongodb:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: orchestrator-frontend
    environment:
      VITE_API_URL: http://localhost:8080/api/v1
      VITE_WS_URL: ws://localhost:8080
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0
volumes:
  postgres_data:
  mongo_data:
  redis_data:
10.2 Environment Variables
# .env
# Database
DATABASE_URL=postgresql://admin:admin123@localhost:5432/orchestrator
MONGODB_URL=mongodb://admin:admin123@localhost:27017/orchestrator
REDIS_URL=redis://localhost:6379
# LLM
DIALKEY_API_KEY=your_dialkey_api_key_here
DIALKEY_BASE_URL=https://your-dialkey-proxy.com/v1
# API Security
API_KEY=your_api_key_for_authentication
SECRET_KEY=your_secret_key_for_jwt
# Frontend
VITE_API_URL=http://localhost:8080/api/v1
VITE_WS_URL=ws://localhost:8080
10.3 Deployment Commands
# Start all services
docker-compose up -d
# View logs
docker-compose logs -f
# Stop all services
docker-compose down
# Rebuild after code changes
docker-compose up --build
# Reset everything (including data)
docker-compose down -v
---
11. TESTING STRATEGY
11.1 Backend Tests
# backend/tests/test_flow_executor.py
import pytest
from app.core.flow_executor import FlowExecutor
@pytest.mark.asyncio
async def test_sequential_execution():
    """Test basic sequential flow execution"""
    
    # Setup
    executor = FlowExecutor(...)
    flow_id = create_test_flow()
    
    # Execute
    result = await executor.execute_sequential(
        flow_id=flow_id,
        execution_id=uuid4(),
        initial_input="Test input"
    )
    
    # Assert
    assert result['status'] == 'completed'
    assert len(result['results']) == 2  # 2 agents
@pytest.mark.asyncio
async def test_hitl_approval():
    """Test HITL gate approval flow"""
    
    # Setup
    hitl_manager = HITLManager(...)
    review_id = await hitl_manager.create_review(...)
    
    # Approve in background
    asyncio.create_task(
        hitl_manager.approve_review(review_id, "Looks good")
    )
    
    # Wait for approval
    result = await hitl_manager.wait_for_approval(review_id)
    
    # Assert
    assert result['approved'] == True
    assert result['comments'] == "Looks good"
@pytest.mark.asyncio
async def test_memory_persistence():
    """Test memory persists across executions"""
    
    # First execution
    memory_manager = MemoryManager(...)
    await memory_manager.add_to_memory(flow_id, agent_id, {"test": "data"})
    
    # Second execution
    context = await memory_manager.get_context_for_agent(flow_id, agent_id, {})
    
    # Assert
    assert 'execution_history' in context
    assert len(context['execution_history']) > 0
11.2 Frontend Tests
// frontend/src/components/__tests__/FlowCanvas.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import FlowCanvas from '../Canvas/FlowCanvas';
describe('FlowCanvas', () => {
  it('renders canvas', () => {
    render(<FlowCanvas />);
    expect(screen.getByTestId('flow-canvas')).toBeInTheDocument();
  });
  it('adds node on drag-drop', () => {
    const { container } = render(<FlowCanvas />);
    
    // Simulate drag-drop
    const palette = screen.getByTestId('agent-palette');
    const canvas = screen.getByTestId('flow-canvas');
    
    fireEvent.dragStart(palette);
    fireEvent.drop(canvas);
    
    // Assert node added
    expect(container.querySelectorAll('.agent-node')).toHaveLength(1);
  });
});
11.3 Integration Testing (CONTINUED)
# End-to-end test script (continued)
#!/bin/bash
echo "Starting E2E test..."
# 1. Create flow
FLOW_ID=$(curl -X POST http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test_key" \
  -d @test_flow.json | jq -r '.id')
echo "Created flow: $FLOW_ID"
# 2. Start execution
EXEC_ID=$(curl -X POST http://localhost:8080/api/v1/executions/start \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test_key" \
  -d "{\"flow_id\": \"$FLOW_ID\", \"initial_input\": \"Test\"}" | jq -r '.execution_id')
echo "Started execution: $EXEC_ID"
# 3. Wait for HITL review
sleep 5
REVIEW_ID=$(curl http://localhost:8080/api/v1/hitl/queue \
  -H "X-API-Key: test_key" | jq -r '.reviews[0].review_id')
echo "Found review: $REVIEW_ID"
# 4. Approve review
curl -X POST http://localhost:8080/api/v1/hitl/$REVIEW_ID/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test_key" \
  -d '{"comments": "Approved via test"}'
echo "Approved review"
# 5. Wait for completion
sleep 10
# 6. Check execution status
STATUS=$(curl http://localhost:8080/api/v1/executions/$EXEC_ID \
  -H "X-API-Key: test_key" | jq -r '.status')
echo "Final status: $STATUS"
if [ "$STATUS" = "completed" ]; then
  echo "✅ E2E test PASSED"
  exit 0
else
  echo "❌ E2E test FAILED"
  exit 1
fi
11.4 Manual Testing Checklist
 Manual Testing Checklist
 Flow Creation
- [ ] Can drag agent from palette to canvas
- [ ] Can connect agents with edges
- [ ] Can select and configure agent
- [ ] Can edit system prompt in Monaco Editor
- [ ] Can select role from dropdown
- [ ] Can select model from dropdown
- [ ] Can toggle HITL gates
- [ ] Can save flow with name and description
- [ ] Saved flow appears in load dialog
 Flow Loading
- [ ] Can see list of saved flows
- [ ] Can load flow into canvas
- [ ] All agent configurations preserved
- [ ] All edges restored correctly
 Flow Execution
- [ ] "Run Flow" button starts execution
- [ ] Execution runs in background
- [ ] Can navigate away and return
- [ ] Progress bar updates in real-time
- [ ] Current executing node highlights
- [ ] Completed nodes show checkmark
 HITL Workflow
- [ ] Modal pops up when review needed
- [ ] Agent output displays correctly
- [ ] Can approve with comments
- [ ] Execution continues after approval
- [ ] Can reject with comments
- [ ] Agent re-runs with feedback
- [ ] New output appears for review
- [ ] Can approve on second attempt
 Memory Persistence
- [ ] Run flow first time
- [ ] Run same flow second time
- [ ] Agents reference previous execution in output
- [ ] Memory visible in execution logs
- [ ] MongoDB contains execution history
 Analytics
- [ ] Dashboard shows correct metrics
- [ ] Success rate calculated properly
- [ ] Agent performance chart displays
- [ ] Execution history loads
- [ ] Can view detailed logs
 Error Handling
- [ ] Invalid API key shows error
- [ ] LLM rate limit handled gracefully
- [ ] Network errors display toast
- [ ] Failed steps show error indicator
- [ ] Can retry failed executions
 UI/UX
- [ ] Loading states display properly
- [ ] Buttons disable during operations
- [ ] Tooltips show on hover
- [ ] Responsive on different screen sizes
- [ ] No console errors
---
12. SECURITY CONSIDERATIONS
12.1 API Security
CORS Configuration (REQUIRED — without this all browser requests fail):
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import flows, executions, hitl, analytics
from app.api import health

app = FastAPI(
    title="Multi-Agent Orchestrator",
    description="Visual drag-and-drop multi-agent orchestration platform",
    version="1.0.0",
)

# -----------------------------------------------------------------------
# CORS — must be added BEFORE any routes are registered.
# In development, allow the Vite dev server (localhost:3000).
# In production, replace with your actual frontend domain.
# -----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Vite dev server
        "http://127.0.0.1:3000",   # Alternative local address
        # "https://your-production-domain.com",  # Add for production
    ],
    allow_credentials=True,         # Required for cookie / auth header forwarding
    allow_methods=["*"],            # GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],            # X-API-Key, Content-Type, Authorization, etc.
)

# Register routers
app.include_router(health.router, tags=["health"])
app.include_router(flows.router,      prefix="/api/v1", tags=["flows"])
app.include_router(executions.router, prefix="/api/v1", tags=["executions"])
app.include_router(hitl.router,       prefix="/api/v1/hitl", tags=["hitl"])
app.include_router(analytics.router,  prefix="/api/v1/analytics", tags=["analytics"])

Authentication:
# backend/app/dependencies.py
from fastapi import Header, HTTPException, status
async def verify_api_key(x_api_key: str = Header(...)):
    """
    Verify API key for all protected endpoints
    """
    
    # In MVP: Simple comparison with env variable
    # In Production: Hash comparison with database
    
    if x_api_key != os.getenv('API_KEY'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return x_api_key
# Usage in endpoints:
@router.post("/flows", dependencies=[Depends(verify_api_key)])
async def create_flow(flow: FlowCreate):
    ...
Rate Limiting:
# backend/app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
class RateLimiter:
    """
    Simple in-memory rate limiter
    For production: Use Redis-based limiter
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # {api_key: [(timestamp, count)]}
    
    async def check_rate_limit(self, api_key: str):
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        if api_key in self.requests:
            self.requests[api_key] = [
                (ts, count) for ts, count in self.requests[api_key]
                if ts > minute_ago
            ]
        
        # Count requests
        total = sum(count for _, count in self.requests.get(api_key, []))
        
        if total >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # Record request
        if api_key not in self.requests:
            self.requests[api_key] = []
        self.requests[api_key].append((now, 1))
12.2 Input Validation
System Prompt Validation:
# backend/app/utils/validators.py
import re
from typing import Optional
def validate_system_prompt(prompt: str) -> Optional[str]:
    """
    Validate system prompt for security issues
    """
    
    # Check length
    if len(prompt) > 10000:
        return "System prompt too long (max 10,000 characters)"
    
    # Check for prompt injection patterns
    dangerous_patterns = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+prior",
        r"forget\s+everything",
        r"act\s+as\s+if"
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return f"Potentially dangerous pattern detected: {pattern}"
    
    return None  # Valid
def validate_flow_config(flow_config: dict) -> Optional[str]:
    """
    Validate flow configuration structure
    """
    
    # Check required fields
    if 'nodes' not in flow_config or 'edges' not in flow_config:
        return "Flow config must have 'nodes' and 'edges'"
    
    # Check node structure
    for node in flow_config['nodes']:
        if 'id' not in node or 'type' not in node:
            return "Each node must have 'id' and 'type'"
    
    # Check for circular dependencies
    if has_circular_dependencies(flow_config):
        return "Flow contains circular dependencies"
    
    return None  # Valid
12.3 Data Sanitization
Output Sanitization:
# backend/app/utils/sanitize.py
import bleach
from typing import Any, Dict
def sanitize_agent_output(output: str) -> str:
    """
    Sanitize agent output before storing or displaying
    
    Removes potentially harmful HTML/JS
    """
    
    # Allow basic formatting tags only
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre']
    
    sanitized = bleach.clean(
        output,
        tags=allowed_tags,
        strip=True
    )
    
    return sanitized
def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input before passing to LLM
    """
    
    # Remove null bytes
    sanitized = user_input.replace('\x00', '')
    
    # Limit length
    if len(sanitized) > 50000:
        sanitized = sanitized[:50000]
    
    return sanitized
12.4 Database Security
SQL Injection Prevention:
# Always use parameterized queries
# ❌ NEVER DO THIS:
query = f"SELECT * FROM flows WHERE id = '{flow_id}'"
await db.execute(query)
# ✅ ALWAYS DO THIS:
query = "SELECT * FROM flows WHERE id = $1"
await db.execute(query, flow_id)
MongoDB Injection Prevention:
# backend/app/db/mongodb.py
def sanitize_mongo_query(query: dict) -> dict:
    """
    Sanitize MongoDB query to prevent injection
    """
    
    # Remove $where operator (allows arbitrary code)
    if '$where' in query:
        del query['$where']
    
    # Recursively sanitize nested queries
    for key, value in query.items():
        if isinstance(value, dict):
            query[key] = sanitize_mongo_query(value)
    
    return query
12.5 Environment Variables
Secure Configuration:
# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
class Settings(BaseSettings):
    """
    Application settings loaded from environment
    """
    
    # Database
    database_url: str
    mongodb_url: str
    redis_url: str
    
    # LLM
    dialkey_api_key: str
    dialkey_base_url: str
    
    # Security
    api_key: str
    secret_key: str
    
    # App config
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance
    """
    return Settings()
12.6 Secrets Management
Production Recommendations:
# DO NOT commit .env to git
# Add to .gitignore
echo ".env" >> .gitignore
# For production, use:
# - AWS Secrets Manager
# - Azure Key Vault
# - HashiCorp Vault
# - Kubernetes Secrets
# Example: AWS Secrets Manager
aws secretsmanager create-secret \
    --name orchestrator/api-keys \
    --secret-string '{"api_key":"xxx","dialkey_key":"yyy"}'
---
13. MONITORING & OBSERVABILITY
13.1 Logging Strategy
# backend/app/utils/logging.py
import logging
from datetime import datetime
from typing import Dict, Any
class StructuredLogger:
    """
    Structured logging for better observability
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        self.logger.addHandler(handler)
    
    def log_execution_start(self, execution_id: str, flow_id: str):
        self.logger.info(
            "Execution started",
            extra={
                'execution_id': execution_id,
                'flow_id': flow_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_agent_execution(
        self,
        execution_id: str,
        agent_id: str,
        duration_ms: int,
        status: str
    ):
        self.logger.info(
            "Agent executed",
            extra={
                'execution_id': execution_id,
                'agent_id': agent_id,
                'duration_ms': duration_ms,
                'status': status
            }
        )
    
    def log_error(self, execution_id: str, error: Exception):
        self.logger.error(
            "Execution error",
            extra={
                'execution_id': execution_id,
                'error_type': type(error).__name__,
                'error_message': str(error)
            },
            exc_info=True
        )
# Usage
logger = StructuredLogger(__name__)
logger.log_execution_start(execution_id, flow_id)
13.2 Health Checks
# backend/app/api/health.py
from fastapi import APIRouter, status
from datetime import datetime
router = APIRouter()
@router.get("/health")
async def health_check():
    """
    Basic health check
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
@router.get("/health/detailed")
async def detailed_health_check(db, redis, mongodb):
    """
    Detailed health check with dependency status
    """
    
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {}
    }
    
    # Check PostgreSQL
    try:
        await db.execute("SELECT 1")
        health["dependencies"]["postgres"] = "healthy"
    except Exception as e:
        health["dependencies"]["postgres"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check MongoDB
    try:
        await mongodb.admin.command('ping')
        health["dependencies"]["mongodb"] = "healthy"
    except Exception as e:
        health["dependencies"]["mongodb"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check Redis
    try:
        await redis.ping()
        health["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    return health
13.3 Metrics Collection
# backend/app/middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time
# Define metrics
execution_counter = Counter(
    'flow_executions_total',
    'Total number of flow executions',
    ['flow_id', 'status']
)
execution_duration = Histogram(
    'flow_execution_duration_seconds',
    'Flow execution duration',
    ['flow_id']
)
active_executions = Gauge(
    'active_executions',
    'Number of currently running executions'
)
hitl_reviews_counter = Counter(
    'hitl_reviews_total',
    'Total HITL reviews',
    ['status']
)
# Middleware to collect metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record request duration
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).observe(duration)
    
    return response
---
14. TROUBLESHOOTING GUIDE
14.1 Common Issues
Issue: Docker containers won't start
# Solution 1: Check if ports are in use
lsof -i :5432  # PostgreSQL
lsof -i :27017 # MongoDB
lsof -i :6379  # Redis
lsof -i :8080  # Backend
lsof -i :3000  # Frontend
# Kill processes if needed
kill -9 <PID>
# Solution 2: Remove old containers and volumes
docker-compose down -v
docker system prune -a
docker-compose up -d
Issue: Backend can't connect to databases
# Check container status
docker-compose ps
# Check logs
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs redis
# Test connections
docker-compose exec postgres psql -U admin -d orchestrator
docker-compose exec mongodb mongosh -u admin -p admin123
docker-compose exec redis redis-cli ping
Issue: LLM API calls failing
# Check DialKey configuration
echo $DIALKEY_API_KEY
echo $DIALKEY_BASE_URL
# Test DialKey directly
curl -X POST $DIALKEY_BASE_URL/chat/completions \
  -H "Authorization: Bearer $DIALKEY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "test"}]
  }'
# Check rate limits
# Look for "429 Too Many Requests" in logs
docker-compose logs backend | grep "429"
Issue: HITL modal not appearing
# Check WebSocket connection
# Open browser console, look for:
# "WebSocket connection established"
# Check backend WebSocket logs
docker-compose logs backend | grep "WebSocket"
# Test WebSocket manually
wscat -c ws://localhost:8080/ws/execution/{execution_id}
Issue: Memory not persisting
# Check MongoDB connection
docker-compose exec backend python -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
async def test():
    client = AsyncIOMotorClient('mongodb://admin:admin123@mongodb:27017')
    result = await client.orchestrator.flow_memory.find_one()
    print(result)
asyncio.run(test())
"
# Check if data exists
docker-compose exec mongodb mongosh -u admin -p admin123
> use orchestrator
> db.flow_memory.find().pretty()
14.2 Performance Optimization
Database Indexing:
-- Add indexes for frequently queried fields
CREATE INDEX CONCURRENTLY idx_flows_name ON flows(name);
CREATE INDEX CONCURRENTLY idx_executions_status_created ON flow_executions(status, created_at DESC);
CREATE INDEX CONCURRENTLY idx_hitl_pending ON hitl_reviews(status) WHERE status = 'pending';
Redis Caching:
# Cache frequently accessed flows
@lru_cache(maxsize=100)
async def get_flow_cached(flow_id: UUID):
    # Check Redis first
    cached = await redis.get(f"cache:flow:{flow_id}")
    if cached:
        return json.loads(cached)
    
    # Load from database
    flow = await db.get_flow(flow_id)
    
    # Cache for 5 minutes
    await redis.setex(
        f"cache:flow:{flow_id}",
        300,
        json.dumps(flow)
    )
    
    return flow
Connection Pooling:
# backend/app/db/postgres.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,        # Max connections
    max_overflow=10,     # Extra connections if needed
    pool_pre_ping=True,  # Verify connection before use
    pool_recycle=3600    # Recycle connections after 1 hour
)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
---
15. FUTURE ENHANCEMENTS (PHASE 2)
15.1 Planned Features
Parallel Flow Execution:
# Execute multiple agents simultaneously
async def execute_parallel(self, flow, execution_id):
    """
    Execute agents in parallel when they don't depend on each other
    
    Example:
    Start → Agent1 ↘
                     → Agent3 → End
    Start → Agent2 ↗
    
    Agent1 and Agent2 run in parallel, then Agent3
    """
    
    # Build dependency graph
    graph = self.build_dependency_graph(flow)
    
    # Execute in layers
    for layer in graph.layers:
        # All agents in same layer run in parallel
        tasks = [
            self.execute_agent(agent_id)
            for agent_id in layer
        ]
        results = await asyncio.gather(*tasks)
Vector Database Integration:
# Add semantic search to memory
class VectorMemoryStore:
    """
    Store agent outputs as embeddings for semantic search
    """
    
    def __init__(self, chroma_client):
        self.client = chroma_client
        self.collection = client.get_or_create_collection("agent_memory")
    
    async def add_memory(self, agent_id: str, text: str, metadata: dict):
        # Generate embedding and store
        self.collection.add(
            documents=[text],
            metadatas=[{
                "agent_id": agent_id,
                **metadata
            }],
            ids=[str(uuid4())]
        )
    
    async def search_memory(self, query: str, n_results: int = 5):
        # Semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
Multi-modal Agents:
# Support image and audio processing
class MultiModalAgent(BaseAgent):
    """
    Agent that can handle text, images, and audio
    """
    
    async def process_image(self, image_url: str, prompt: str):
        # Use GPT-4 Vision
        response = await self.llm.generate(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": image_url}
                    ]
                }
            ]
        )
        return response
    
    async def transcribe_audio(self, audio_file: bytes):
        # Use Whisper API
        response = await self.llm.transcribe(
            model="whisper-1",
            file=audio_file
        )
        return response
Token Usage Tracking:
# Track LLM costs per execution
class TokenTracker:
    """
    Track token usage and costs
    """
    
    PRICING = {
        "gpt-4o": {
            "input": 0.005,  # per 1K tokens
            "output": 0.015
        },
        "gpt-4o-mini": {
            "input": 0.0001,
            "output": 0.0006
        },
        "claude-3-5-sonnet-20241022": {
            "input": 0.003,
            "output": 0.015
        }
    }
    
    async def record_usage(
        self,
        execution_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ):
        cost = (
            (input_tokens / 1000) * self.PRICING[model]["input"] +
            (output_tokens / 1000) * self.PRICING[model]["output"]
        )
        
        await self.db.execute("""
            INSERT INTO token_usage (
                execution_id, model, input_tokens,
                output_tokens, cost
            ) VALUES ($1, $2, $3, $4, $5)
        """, execution_id, model, input_tokens, output_tokens, cost)
Plugin System:
# Allow custom agents and tools
class PluginRegistry:
    """
    Registry for custom agent plugins
    """
    
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin_class):
        """
        Register a custom agent plugin
        
        Example:
        @plugin_registry.register_plugin("custom_analyzer")
        class CustomAnalyzer(BaseAgent):
            async def run(self, context):
                # Custom logic
                return result
        """
        self.plugins[name] = plugin_class
    
    def get_plugin(self, name: str):
        return self.plugins.get(name)
---
16. GLOSSARY
Agent: An autonomous AI entity with a specific role, system prompt, and capabilities. Executes tasks using LLMs.
Flow: A directed graph of agents connected by edges, representing a workflow.
Sequential Execution: Running agents one after another, where each agent receives output from the previous agent.
Parallel Execution: Running multiple agents simultaneously when they don't depend on each other.
HITL (Human-in-the-Loop): A checkpoint where human approval is required before continuing execution.
System Prompt: Instructions that define an agent's behavior, personality, and capabilities.
Context: Historical information and memory passed to an agent during execution.
Memory:
- Short-term: Temporary data stored in Redis for current execution
- Long-term: Historical execution data stored in MongoDB
- Persistent: Accumulated knowledge stored across all executions
Orchestrator: The central system that coordinates agent execution.
DialKey: API proxy service that provides unified access to multiple LLM providers.
LiteLLM: Python library that provides a unified interface to different LLM APIs.
React Flow: JavaScript library for building node-based UIs.
WebSocket: Protocol for real-time bidirectional communication between client and server.
---
17. CONCLUSION
17.1 Success Metrics
At the end of 14 days, you should have achieved:
✅ Functional POC
- Drag-and-drop interface for creating flows
- Agent configuration with pre-built templates
- Sequential flow execution
- HITL gates with approval/rejection
- Memory persistence across executions
- Save/load functionality
- Analytics dashboard
✅ Technical Deliverables
- Docker Compose setup with all services
- FastAPI backend with complete REST API
- React + TypeScript frontend
- PostgreSQL + MongoDB + Redis integration
- LiteLLM integration with DialKey
- WebSocket real-time updates
✅ Documentation
- README with setup instructions
- API reference
- Architecture documentation
- User guide
17.2 Next Steps After POC
1. User Testing
   - Gather feedback from real users
   - Identify pain points
   - Prioritize Phase 2 features
2. Performance Optimization
   - Load testing
   - Database query optimization
   - Frontend bundle size reduction
3. Production Deployment
   - AWS infrastructure setup
   - CI/CD pipeline
   - Monitoring and alerting
   - Backup strategy
4. Security Hardening
   - Security audit
   - Penetration testing
   - OAuth integration
   - Role-based access control
5. Phase 2 Features
   - Parallel flow execution
   - Vector database integration
   - Multi-modal agents
   - Token usage tracking
   - Plugin system
17.3 Contact & Support
For questions during implementation:
- Review this document thoroughly
- Check troubleshooting guide (Section 14)
- Use Claude Code for pair programming
- Document issues and solutions as you go
17.4 Final Checklist
Before considering POC complete:
- [ ] All Docker services running
- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] Can create a 3-agent flow
- [ ] Can execute flow end-to-end
- [ ] HITL gates work correctly
- [ ] Memory persists across runs
- [ ] Analytics display correctly
- [ ] Save/load works
- [ ] README is complete
- [ ] Code is commented
- [ ] Git repository initialized
- [ ] .env.example created
- [ ] Demo video recorded
---
END OF IMPLEMENTATION PLAN
Version: 1.0  
Last Updated: March 2, 2026  
Total Pages: ~60  
Estimated Implementation Time: 56 hours (14 days × 4 hours/day)
---
Now save this entire document!
I've now provided the COMPLETE implementation plan from start to finish. This document includes:
1. ✅ Executive Summary
2. ✅ Project Overview
3. ✅ System Architecture
4. ✅ Technology Stack
5. ✅ Database Design (PostgreSQL, MongoDB, Redis)
6. ✅ API Specification (All endpoints)
7. ✅ Frontend Design (Complete component hierarchy)
8. ✅ Backend Design (All core modules)
9. ✅ Implementation Timeline (14-day breakdown)
10. ✅ Deployment Strategy
11. ✅ Testing Strategy (Unit, Integration, E2E)
12. ✅ Security Considerations
13. ✅ Monitoring & Observability
14. ✅ Troubleshooting Guide
15. ✅ Future Enhancements (Phase 2)
16. ✅ Glossary
17. ✅ Conclusion
This is a production-ready implementation plan ready for execution!
You can now:
1. Copy this entire text
2. Save it as IMPLEMENTATION_PLAN.md in your multi-agent-orchestrator-plan folder
3. Start implementing Day 1 tomorrow!
Would you like me to create any additional supplementary documents like:
- Quick start guide
- API examples
- Database migration scripts
- Docker troubleshooting guide
- Development workflow document