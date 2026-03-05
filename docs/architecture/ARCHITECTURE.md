# System Architecture — AgentCanvas

**Version**: 1.0 | **Date**: 2026-03-03 | **Status**: Approved for MVP

---

## Overview

AgentCanvas is a multi-agent orchestration platform. Users visually design agent workflows on a drag-and-drop canvas, configure each agent, execute sequential flows with HITL (Human-in-the-Loop) gates, and monitor execution with shared persistent memory.

---

## System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│   React 18 + TypeScript + React Flow + Zustand + Vite       │
│   Canvas UI | Agent Config | HITL Queue | Analytics         │
└──────────────────────┬──────────────────────────────────────┘
                       │  HTTP REST + WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                      API LAYER                               │
│              FastAPI — thin routers only                     │
│   /flows | /executions | /hitl | /memory | /analytics       │
└──────────────────────┬──────────────────────────────────────┘
                       │  Service calls
┌──────────────────────▼──────────────────────────────────────┐
│                    CORE / SERVICE LAYER                      │
│   FlowExecutor | HITLManager | MemoryService | LLMService   │
│   AgentRunner | AnalyticsService                            │
└──────┬───────────────┬──────────────────┬───────────────────┘
       │               │                  │
┌──────▼──────┐ ┌──────▼──────┐  ┌───────▼────────┐
│ PostgreSQL  │ │   MongoDB   │  │     Redis       │
│ (relational)│ │ (documents) │  │ (cache/queue)   │
└─────────────┘ └─────────────┘  └────────────────┘
```

---

## Component Responsibilities

### Frontend (React + TypeScript)

| Component | File Location | Responsibility |
|-----------|---------------|----------------|
| Canvas | `components/Canvas/` | React Flow drag-and-drop graph |
| AgentNode | `components/nodes/AgentNode.tsx` | Visual node for each agent |
| ConfigPanel | `components/panels/ConfigPanel.tsx` | Right-side agent configuration |
| HITLQueue | `components/hitl/HITLQueue.tsx` | Pending reviews list |
| ExecutionLog | `components/execution/ExecutionLog.tsx` | Live execution events |
| Analytics | `components/analytics/Dashboard.tsx` | Charts, success rates |
| useFlow | `hooks/useFlow.ts` | Flow CRUD operations |
| useExecution | `hooks/useExecution.ts` | Execution state + WebSocket |
| flowStore | `store/flowStore.ts` | Zustand — flow state |
| executionStore | `store/executionStore.ts` | Zustand — execution state |

**State Management Rule**: Zustand stores are the single source of truth. Components never fetch directly — they use hooks which call stores which call services.

### Backend API Layer (FastAPI Routers)

| Router | File | Endpoints |
|--------|------|-----------|
| flows | `api/flows.py` | CRUD for flows |
| executions | `api/executions.py` | Start, stop, status, steps |
| hitl | `api/hitl.py` | List reviews, approve, reject |
| memory | `api/memory.py` | Read, update shared/agent memory |
| analytics | `api/analytics.py` | Agent stats, execution history |
| ws | `api/websocket.py` | Real-time execution events |

**Rule**: API routers must be thin. No business logic in routers — delegate to services.

### Core / Service Layer

| Service | File | Responsibility |
|---------|------|----------------|
| FlowExecutor | `core/flow_executor.py` | Orchestrates sequential agent execution |
| AgentRunner | `core/agent_runner.py` | Executes a single agent step |
| HITLManager | `core/hitl_manager.py` | Creates, evaluates, and resolves HITL reviews |
| MemoryService | `memory/memory_service.py` | Read/write shared and agent-specific memory |
| LLMService | `services/llm_service.py` | Anthropic API wrapper with retry + timeout |
| AnalyticsService | `services/analytics_service.py` | Writes and queries agent analytics |

### Data Layer

See `docs/architecture/DATABASE.md` for full schema.

| Store | Purpose | Data |
|-------|---------|------|
| PostgreSQL | Relational data | Flows, agents, executions, steps, HITL reviews, analytics |
| MongoDB | Document data | Execution history logs, flow memory snapshots |
| Redis | Ephemeral data | Execution state cache, WebSocket pub/sub |

---

## Data Flow: Flow Execution

```
User clicks "Run"
    │
    ▼
POST /api/executions {flow_id}
    │
    ▼
FlowExecutor.start(flow_id)
    │
    ├── Load flow config from PostgreSQL
    ├── Create FlowExecution record (status: running)
    ├── Initialize shared memory in MongoDB
    │
    ▼
FOR each agent node in order:
    │
    ├── AgentRunner.run(node, context)
    │   ├── Build prompt (system prompt + shared memory + previous outputs)
    │   ├── LLMService.complete(prompt)   ← Anthropic API
    │   ├── Validate response (never trust raw LLM output)
    │   ├── Save output to MongoDB execution log
    │   └── Update StepExecution in PostgreSQL
    │
    ├── [HITL Gate Check]
    │   ├── gate_type == "after"? → Create HITLReview, PAUSE execution
    │   ├── Wait for /api/hitl/{id}/approve or /reject
    │   └── On approve → resume; on reject → stop or retry
    │
    └── Update shared memory with agent output

    ▼
All steps complete:
    ├── FlowExecution status → "completed"
    ├── Save final memory snapshot
    ├── Write agent_execution_events → triggers analytics update
    └── WebSocket broadcast: execution_complete
```

---

## Real-Time Communication (WebSocket)

Events pushed to client during execution:

| Event | Payload | When |
|-------|---------|------|
| `step_started` | `{step_number, agent_name}` | Agent step begins |
| `step_completed` | `{step_number, output_preview}` | Step finishes successfully |
| `step_failed` | `{step_number, error}` | Step fails |
| `hitl_required` | `{review_id, gate_type, output}` | HITL gate triggered |
| `execution_completed` | `{execution_id, success_rate}` | All steps done |
| `execution_failed` | `{execution_id, error}` | Fatal execution error |

---

## Security Architecture

- All API inputs validated by Pydantic schemas before reaching services
- LLM prompts sanitized before sending (Standard 9 — prompt injection prevention)
- No credentials in code — all in environment variables
- CORS configured to allowed origins only
- Rate limiting on LLM endpoints

See `docs/security/SECURITY.md` for full details.

---

## Architecture Decision Records

| ADR | Decision | Status |
|-----|----------|--------|
| [ADR-001](./ADR/ADR-001-tech-stack.md) | FastAPI + React + PostgreSQL + MongoDB + Redis | Accepted |
| [ADR-002](./ADR/ADR-002-sequential-execution.md) | Sequential-only execution for MVP (no parallel) | Accepted |
| [ADR-003](./ADR/ADR-003-zustand-state.md) | Zustand for frontend state over Redux | Accepted |

---

## Constraints and Non-Negotiables

1. **No parallel flow execution in MVP** — sequential only (ADR-002)
2. **No vector database in MVP** — plain text memory only
3. **No multi-modal agents in MVP** — text only
4. **No plugin system in MVP**
5. All services must be containerized — no local-only setup
