# Feature Backlog — AgentCanvas

**Format**: Each issue maps to a GitLab issue. Grouped by parallel work track.
**Status**: open | in-progress | review | done

---

## Track: track:devops

| # | Title | Priority | Milestone | Status |
|---|-------|----------|-----------|--------|
| D-01 | Docker Compose with all 5 services (BE, FE, Postgres, Mongo, Redis) | critical | M1 | done |
| D-02 | Environment variable setup (.env.example) | critical | M1 | done |
| D-03 | Docker health checks for all services | high | M1 | done |
| D-04 | GitLab CI pipeline: lint + type-check + test gates | high | M6 | open |
| D-05 | Nginx reverse proxy config | medium | M1 | open |
| D-06 | Production Docker Compose (no dev volumes) | medium | M6 | open |

---

## Track: track:database

| # | Title | Priority | Milestone | Status |
|---|-------|----------|-----------|--------|
| DB-01 | PostgreSQL schema: flows, agents, flow_executions, step_executions | critical | M1 | done |
| DB-02 | PostgreSQL schema: hitl_reviews, agent_analytics, agent_execution_events | critical | M1 | done |
| DB-03 | PostgreSQL triggers: analytics auto-update, updated_at | critical | M1 | done |
| DB-04 | MongoDB: execution_history collection with validation schema | critical | M1 | done |
| DB-05 | MongoDB: flow_memory collection with validation schema | critical | M1 | done |
| DB-06 | MongoDB indexes: execution_id unique, flow_id unique, status | high | M1 | done |
| DB-07 | SQLAlchemy ORM models for all PostgreSQL tables | critical | M1 | done |
| DB-08 | Alembic migration setup + initial migration file | high | M1 | in-progress |

---

## Track: track:backend-api

| # | Title | Priority | Milestone | Status |
|---|-------|----------|-----------|--------|
| BA-01 | FastAPI app skeleton: main.py, CORS, lifespan, health endpoint | critical | M1 | done |
| BA-02 | Flow CRUD endpoints: POST/GET/PUT/DELETE /flows | critical | M2 | in-progress |
| BA-03 | Flow list endpoint with pagination | high | M2 | in-progress |
| BA-04 | Execution endpoints: POST /executions, GET /executions/{id} | critical | M3 | open |
| BA-05 | Execution step details: GET /executions/{id}/steps | high | M3 | open |
| BA-06 | Stop execution: POST /executions/{id}/cancel | high | M3 | open |
| BA-07 | HITL list endpoint: GET /hitl?status=pending | critical | M4 | open |
| BA-08 | HITL approve/reject: POST /hitl/{id}/approve, /reject | critical | M4 | open |
| BA-09 | Memory read endpoint: GET /memory/{flow_id} | high | M3 | open |
| BA-10 | Memory update endpoint: PUT /memory/{flow_id} | high | M3 | open |
| BA-11 | Analytics endpoints: GET /analytics/agents, /agents/{id} | high | M5 | open |
| BA-12 | WebSocket endpoint: WS /ws/executions/{execution_id} | critical | M3 | open |
| BA-13 | Pydantic schemas for all request/response models | critical | M1 | done |
| BA-14 | Global error handler middleware | high | M1 | done |

---

## Track: track:backend-core

| # | Title | Priority | Milestone | Status |
|---|-------|----------|-----------|--------|
| BC-01 | LLMService: Anthropic client wrapper with timeout + retry | critical | M3 | open |
| BC-02 | FlowExecutor: load flow, sequential step loop | critical | M3 | open |
| BC-03 | AgentRunner: build prompt, call LLM, validate response, save output | critical | M3 | open |
| BC-04 | MemoryService: read/write shared memory in MongoDB | critical | M3 | open |
| BC-05 | MemoryService: read/write agent-specific memory | high | M3 | open |
| BC-06 | HITLManager: create review, pause execution, handle approve/reject | critical | M4 | open |
| BC-07 | HITL gate modes: before_step, after_step, on_demand | critical | M4 | open |
| BC-08 | WebSocket manager: broadcast events to connected clients | critical | M3 | open |
| BC-09 | Execution background task: run via FastAPI BackgroundTasks | high | M3 | open |
| BC-10 | Agent template system: load pre-built configs | medium | M5 | open |
| BC-11 | AnalyticsService: query and format agent stats | high | M5 | open |
| BC-12 | Prompt sanitizer: strip injection patterns before LLM call | high | M3 | open |

---

## Track: track:frontend

| # | Title | Priority | Milestone | Status |
|---|-------|----------|-----------|--------|
| FE-01 | Vite + React + TypeScript + React Flow skeleton | critical | M1 | done |
| FE-02 | React Router setup with routes: /, /flows/:id, /analytics | high | M1 | open |
| FE-03 | React Flow canvas with Start, Agent, End node types | critical | M2 | open |
| FE-04 | Drag-to-add agent nodes from sidebar palette | critical | M2 | open |
| FE-05 | Edge connections between nodes (directional) | critical | M2 | open |
| FE-06 | Agent configuration panel (right sidebar) | critical | M2 | open |
| FE-07 | Save flow button — POST/PUT to API | critical | M2 | open |
| FE-08 | Load/list flows — GET from API, flow library page | high | M2 | open |
| FE-09 | Run flow button — POST /executions | critical | M3 | open |
| FE-10 | Execution progress overlay on canvas nodes | high | M3 | open |
| FE-11 | WebSocket client with reconnect logic | critical | M3 | open |
| FE-12 | Live execution log panel (step events stream) | high | M3 | open |
| FE-13 | HITL queue page: list pending reviews | critical | M4 | open |
| FE-14 | HITL review modal: show output, approve/reject | critical | M4 | open |
| FE-15 | Analytics dashboard: charts for success rate, exec time | high | M5 | open |
| FE-16 | Agent template picker modal | medium | M5 | open |
| FE-17 | Zustand stores: flowStore, executionStore, hitlStore | critical | M1 | done |
| FE-18 | API client service (typed fetch wrapper) | critical | M1 | done |
| FE-19 | TypeScript type definitions for all domain objects | critical | M1 | done |
| FE-20 | Error states, loading states, empty states for all pages | high | M6 | open |

---

## Track: track:testing

| # | Title | Priority | Milestone | Status |
|---|-------|----------|-----------|--------|
| T-01 | Backend unit tests: FlowExecutor sequential execution | high | M6 | in-progress |
| T-02 | Backend unit tests: HITLManager approve/reject | high | M6 | in-progress |
| T-03 | Backend unit tests: MemoryService read/write | high | M6 | in-progress |
| T-04 | Backend unit tests: LLMService timeout + retry | high | M6 | in-progress |
| T-05 | Backend integration tests: full execution API flow | high | M6 | in-progress |
| T-06 | Backend integration tests: HITL gate end-to-end | high | M6 | in-progress |
| T-07 | Frontend component tests: Canvas rendering | medium | M6 | open |
| T-08 | Frontend component tests: HITL review modal | medium | M6 | open |
| T-09 | Frontend component tests: Execution log panel | medium | M6 | open |
| T-10 | pytest fixtures: DB setup/teardown, LLM mock | high | M6 | in-progress |

---

## Track: track:security

| # | Title | Priority | Milestone | Status |
|---|-------|----------|-----------|--------|
| S-01 | API key auth middleware for all protected endpoints | high | M1 | done |
| S-02 | Input validation: all Pydantic schemas with field constraints | critical | M1 | done |
| S-03 | LLM prompt sanitization (prompt injection prevention) | high | M3 | open |
| S-04 | CORS configuration: allowed origins from env | high | M1 | done |
| S-05 | Rate limiting on LLM-calling endpoints | medium | M3 | open |
