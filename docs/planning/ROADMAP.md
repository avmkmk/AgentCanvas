# Project Roadmap — AgentCanvas

**Start Date**: 2026-03-03 | **MVP Target**: 2026-03-17 (14 days)

---

## Milestones

### Milestone 1 — Foundation (Days 1-3)
**Goal**: Codebase skeleton, all services running, database ready.

| Track | Issues | Status |
|-------|--------|--------|
| track:devops | Docker Compose setup, all 5 services | pending |
| track:database | PostgreSQL schema + migrations | pending |
| track:database | MongoDB initialization | pending |
| track:backend-api | FastAPI app skeleton, health check | pending |
| track:frontend | Vite + React skeleton, router setup | pending |

**Done when**: `docker-compose up` starts all services; `GET /health` returns 200; React app renders.

---

### Milestone 2 — Core Canvas (Days 4-6)
**Goal**: Users can create, configure, save, and load flows on the canvas.

| Track | Issues | Status |
|-------|--------|--------|
| track:frontend | React Flow canvas with node types | pending |
| track:frontend | Agent configuration side panel | pending |
| track:backend-api | Flow CRUD endpoints | pending |
| track:backend-core | Flow persistence service | pending |

**Done when**: User can drag nodes onto canvas, configure an agent, save flow, and reload it.

---

### Milestone 3 — Execution Engine (Days 7-9)
**Goal**: Sequential flow execution works end-to-end.

| Track | Issues | Status |
|-------|--------|--------|
| track:backend-core | FlowExecutor sequential engine | pending |
| track:backend-core | LLM service with retry + timeout | pending |
| track:backend-core | Memory service (shared + agent-specific) | pending |
| track:backend-api | Execution endpoints (start, stop, status) | pending |
| track:frontend | Execution progress UI with live updates | pending |
| track:frontend | WebSocket client for real-time events | pending |

**Done when**: A 2-agent flow executes sequentially; output of agent 1 feeds agent 2; execution log shows all steps.

---

### Milestone 4 — HITL Gates (Days 10-11)
**Goal**: Human-in-the-loop gates work (before, after, on-demand).

| Track | Issues | Status |
|-------|--------|--------|
| track:backend-core | HITL gate logic in FlowExecutor | pending |
| track:backend-api | HITL endpoints (list, approve, reject) | pending |
| track:frontend | HITL review queue UI | pending |
| track:frontend | HITL gate configuration on agent nodes | pending |

**Done when**: Flow pauses at HITL gate; review appears in queue; approve/reject resumes or stops execution.

---

### Milestone 5 — Analytics + Templates (Days 12-13)
**Goal**: Analytics dashboard works; agent templates available.

| Track | Issues | Status |
|-------|--------|--------|
| track:backend-core | Analytics aggregation (via DB trigger) | pending |
| track:backend-api | Analytics endpoints | pending |
| track:frontend | Analytics dashboard (charts, success rates) | pending |
| track:backend-core | Pre-built agent template system | pending |
| track:frontend | Template picker UI | pending |

**Done when**: Analytics show per-agent success rates, avg execution times; templates load pre-configured agents.

---

### Milestone 6 — Polish + Testing (Day 14)
**Goal**: All tests pass; error states handled; deployment-ready.

| Track | Issues | Status |
|-------|--------|--------|
| track:testing | Backend unit tests (FlowExecutor, HITL, Memory) | pending |
| track:testing | Backend integration tests (API + DB) | pending |
| track:testing | Frontend component tests | pending |
| track:devops | CI pipeline with lint + test gates | pending |
| track:frontend | Error states, loading states, empty states | pending |

**Done when**: CI passes; test coverage ≥ 70%; app handles all error states gracefully.

---

## Phase 2 (Post-MVP)

These are explicitly out of scope for MVP:

- [ ] Parallel flow execution
- [ ] Vector database integration (semantic memory search)
- [ ] Multi-modal agents (image, audio input/output)
- [ ] Plugin system
- [ ] Token usage tracking per execution
- [ ] Memory search UI
- [ ] Multi-user / team workspaces
- [ ] Flow versioning
- [ ] Export/import flows

---

## Success Criteria for MVP

1. Create a 3-agent sequential flow via drag-and-drop
2. Execute the flow — each agent's output feeds the next
3. HITL gate pauses execution and waits for approval
4. Shared memory persists across executions
5. Analytics show per-agent performance metrics
6. Save and reload a flow from the database
7. Background execution (user can navigate away)
8. Pre-built agent templates selectable from library
