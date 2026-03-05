# CLAUDE.md — AgentCanvas

**Purpose**: AI-optimized execution guide. Read this at the start of every session.
**Project**: Multi-agent orchestrator — drag-and-drop canvas, HITL gates, shared memory, analytics.
**Session Rule**: Create `docs/sessions/YYYY-MM-DD-NNN.md` at session start AND end.

---

## CRITICAL RULES (Non-Negotiable)

| Rule | Trigger | Action |
|------|---------|--------|
| **Coding Standards** | ANY code task | Follow all 10 standards in `docs/development/CODING_STANDARDS.md` |
| **Session Log** | Session START and END | Create/update `docs/sessions/YYYY-MM-DD-NNN.md` |
| **Guides First** | ANY task | Read the MANDATORY READS for your task track (see below) BEFORE writing code |
| **Issue Reference** | Starting any feature/fix | Branch name and commit MUST include GitLab issue number |
| **No Secrets** | ANY config/env work | Use env vars — never hardcode credentials |
| **Docker Commands** | ANY app/test command | Run inside container unless stated otherwise |
| **Testing** | ONLY when user says "test" | Do not write tests unless explicitly asked |
| **Git Ops** | ONLY when user says "commit/push/PR" | Do not commit unless explicitly asked |
| **Shell Syntax** | ANY shell command | Use bash/Linux syntax (forward slashes, /dev/null, etc.) |

---

## MANDATORY READS (By Task Track)

These files MUST be read using your Read tool before writing any code. Do not rely on summaries in this file alone.

| Track | Files to Read Before Starting |
|-------|-------------------------------|
| **ANY task** | `.codemie/guides/standards/coding-guidelines.md` |
| **track:frontend** | `docs/architecture/ARCHITECTURE.md` |
| **track:backend-api** | `docs/architecture/ARCHITECTURE.md` · `docs/security/SECURITY.md` |
| **track:backend-core** | `docs/architecture/ARCHITECTURE.md` · `docs/architecture/DATABASE.md` |
| **track:database** | `docs/architecture/DATABASE.md` |
| **track:devops** | `docs/deployment/DEPLOYMENT.md` |
| **track:testing** | `docs/development/TESTING_STRATEGY.md` |
| **track:security** | `docs/security/SECURITY.md` · `.codemie/guides/standards/coding-guidelines.md` |

---

## CODING STANDARDS SUMMARY

Detailed in `docs/development/CODING_STANDARDS.md`. The 10 non-negotiable principles:

1. **Simple Control Flow** — No recursion. Use loops and flat branching only.
2. **Memory Management** — Always initialize variables. Use context managers. No resource leaks.
3. **Explicitness** — Explicit types everywhere. No implicit coercion. Named parameters for 3+ args.
4. **Consistency** — One way to do each thing. Match surrounding code style exactly.
5. **Error Handling** — Check every operation that can fail. No silent errors. No bare `except: pass`.
6. **Readability** — One function, one job. Max 50 lines/function. Guard clauses over nesting. Comment the WHY.
7. **Static Analysis** — All code must pass ruff/mypy (Python) and eslint/tsc (TypeScript).
8. **Third-Party/AI Components** — Wrap in service classes. Validate all external responses. Set timeouts.
9. **Safe Resources** — Validate at API boundary with Pydantic/Zod. Sanitize LLM prompts. Use connection pools.
10. **Reproducibility** — No eval/exec. Deterministic logic. Every non-obvious decision has a comment or ADR.

---

## GUIDE IMPORTS

| Category | Guide Path | Purpose |
|----------|------------|---------|
| Standards | `.codemie/guides/standards/coding-guidelines.md` | Detailed coding principles with examples |
| Architecture | `docs/architecture/ARCHITECTURE.md` | System design, layers, data flow |
| Database | `docs/architecture/DATABASE.md` | Schema design, query patterns |
| Git Workflow | `docs/development/GIT_WORKFLOW.md` | Branching, commits, MR process |
| Testing | `docs/development/TESTING_STRATEGY.md` | Test patterns, coverage requirements |
| Deployment | `docs/deployment/DEPLOYMENT.md` | Docker, environment, CI/CD |
| Security | `docs/security/SECURITY.md` | Auth, input validation, secrets |
| Session | `docs/sessions/SESSION_TEMPLATE.md` | Session log format |
| API Examples | `docs/api/API_EXAMPLES.md` | curl + Python request examples |
| Workflow | `docs/development/DEVELOPMENT_WORKFLOW.md` | Daily dev workflow, aliases, VS Code |

---

## TASK CLASSIFIER

| Track | User Intent | Example Requests | Primary Guide |
|-------|-------------|------------------|---------------|
| **track:frontend** | Canvas UI, React components, state, routing | "Add node type", "Fix canvas drag", "Update sidebar" | `docs/architecture/ARCHITECTURE.md` |
| **track:backend-api** | FastAPI routes, request/response schemas | "Add endpoint", "Fix 422 error", "Add validation" | `.codemie/guides/standards/coding-guidelines.md` |
| **track:backend-core** | FlowExecutor, HITL logic, Memory management | "Fix execution bug", "Add memory feature" | `docs/architecture/ARCHITECTURE.md` |
| **track:database** | Schema changes, migrations, query optimization | "Add column", "Create index", "Write migration" | `docs/architecture/DATABASE.md` |
| **track:devops** | Docker, CI/CD, environment config | "Fix Docker issue", "Add CI step", "Update compose" | `docs/deployment/DEPLOYMENT.md` |
| **track:testing** | Unit/integration tests, test fixtures | "Write tests", "Fix failing test" | `docs/development/TESTING_STRATEGY.md` |
| **track:security** | Auth, validation, secrets, OWASP | "Add auth", "Validate input", "Security review" | `docs/security/SECURITY.md` |

---

## ARCHITECTURE QUICK RULES

Full detail: `docs/architecture/ARCHITECTURE.md`

- **API routers are thin** — no business logic; delegate to services only
- **State management**: Zustand is the single source of truth; components use hooks → stores → services
- **Execution is sequential only** (MVP) — no parallel agent runs
- **All LLM responses must be validated** — never trust raw LLM output
- **Data flow**: `Component → Hook → Store → Service → API → Service → Core → DB`

---

## DATABASE QUICK REFERENCE

Full schema + SQL: `docs/architecture/DATABASE.md`

**Valid Enum Values (enforce in all code and schemas):**
- `agents.role`: `researcher | analyst | writer | critic | planner | custom`
- `flow_executions.status`: `pending | running | paused_hitl | completed | failed | cancelled`
- `hitl_reviews.gate_type`: `before | after | on_demand`
- `hitl_reviews.status`: `pending | approved | rejected`

---

## SECURITY QUICK RULES

Full patterns + code examples: `docs/security/SECURITY.md`

- **Endpoints**: Pydantic schema with length limits + `name_no_dangerous_chars` validator + `verify_api_key` dependency
- **LLM calls**: `sanitize_prompt()` on all user content before sending; validate response (non-empty, ≤50k chars)
- **Secrets**: `pydantic_settings.BaseSettings` from `.env` only — app must fail at startup if vars missing

---

## TECHNOLOGY STACK

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | Python + FastAPI | 3.11+ / 0.111+ |
| Frontend | TypeScript + React + Vite | 5.x / 18.x |
| Canvas | React Flow | 11.x |
| State | Zustand | 4.x |
| Primary DB | PostgreSQL | 15.x |
| Document DB | MongoDB | 7.x |
| Cache/Queue | Redis | 7.x |
| Containers | Docker + Docker Compose | Latest |
| BE Tests | pytest + pytest-asyncio | Latest |
| FE Tests | Vitest + Testing Library | Latest |
| BE Lint/Format | Ruff + Black + mypy | Latest |
| FE Lint/Format | ESLint + Prettier | Latest |

---

## PROJECT STRUCTURE

```
AgentCanvas/
├── CLAUDE.md                         # This file — AI agent execution guide
├── CHANGELOG.md                      # Version history (stays at root — industry convention)
├── .codemie/
│   ├── claude.extension.json         # CodeMie extension metadata
│   ├── guides/standards/
│   │   └── coding-guidelines.md      # Detailed coding principles with code examples
│   └── claude-templates/             # Templates for generating CLAUDE.md and guides
├── backend/app/                      # (not yet created)
│   ├── api/                          # FastAPI routers (thin — no business logic)
│   ├── core/                         # FlowExecutor, HITL, orchestration
│   ├── models/                       # SQLAlchemy ORM models
│   ├── schemas/                      # Pydantic request/response schemas
│   ├── services/                     # LLM client, external service wrappers
│   ├── memory/                       # Memory management modules
│   └── utils/                        # Shared utilities
├── frontend/src/                     # (not yet created)
│   ├── components/                   # React components
│   ├── hooks/                        # Custom React hooks
│   ├── services/                     # API clients, WebSocket
│   ├── store/                        # Zustand stores
│   ├── types/                        # TypeScript interfaces/types
│   └── utils/                        # Utility functions
└── docs/
    ├── QUICK_START_GUIDE.md          # Zero-to-running in 15 minutes
    ├── architecture/                 # ARCHITECTURE.md, DATABASE.md, ADR/
    ├── development/                  # CODING_STANDARDS.md, GIT_WORKFLOW.md, TESTING_STRATEGY.md, DEVELOPMENT_WORKFLOW.md
    ├── planning/                     # ROADMAP.md, BACKLOG.md, ImplemenationPlan.md
    ├── api/                          # API_EXAMPLES.md
    ├── deployment/                   # DEPLOYMENT.md
    ├── security/                     # SECURITY.md
    └── sessions/                     # SESSION_TEMPLATE.md, SESSION_INDEX.md, YYYY-MM-DD-NNN.md
```

---

## COMMANDS

| Task | Command |
|------|---------|
| Start all services | `docker-compose up -d` |
| Stop all services | `docker-compose down` |
| View logs | `docker-compose logs -f [service]` |
| Backend shell | `docker-compose exec backend bash` |
| Frontend shell | `docker-compose exec frontend sh` |
| BE tests (when asked) | `docker-compose exec backend pytest` |
| FE tests (when asked) | `docker-compose exec frontend npm test` |
| BE lint | `docker-compose exec backend ruff check app/` |
| BE format | `docker-compose exec backend black app/` |
| FE lint | `docker-compose exec frontend npm run lint` |
| FE format | `docker-compose exec frontend npm run format` |
| PostgreSQL shell | `docker-compose exec postgres psql -U admin -d orchestrator` |

---

## GIT WORKFLOW SUMMARY

```
Branch:   feature/<issue-id>-<short-description>
          fix/<issue-id>-<short-description>
          docs/<description>   |   chore/<description>

Commit:   feat(scope): description [#issue-id]
          fix(scope): description [#issue-id]

Scopes:   backend | frontend | database | docker | api |
          canvas | executor | memory | hitl | analytics | docs
```

Full details: `docs/development/GIT_WORKFLOW.md`

---

## SESSION TRACKING

**Session START:**
1. Note current timestamp (IST)
2. Create `docs/sessions/YYYY-MM-DD-NNN.md` from `SESSION_TEMPLATE.md`
3. List goals and GitLab issues to work on

**Session END:**
1. Fill in: end time, duration, tasks completed, files changed, issues updated
2. Record analytics: estimated tokens, cost, files created/modified, lines added
3. Note blockers and next session prep
4. Append one-line entry to `docs/sessions/SESSION_INDEX.md`

---

## PARALLEL WORK TRACKS

Multiple agents can work simultaneously on these tracks — they have minimal dependencies:

| Track | Dependencies | Can start immediately? |
|-------|-------------|----------------------|
| `track:database` | None | YES |
| `track:backend-api` | DB models | After database track |
| `track:backend-core` | DB models + API schemas | After database track |
| `track:frontend` | API contract (schemas) | YES (with mock data) |
| `track:devops` | None | YES |
| `track:testing` | Feature code | After respective track |

---

## GITHUB MCP

GitHub MCP is connected for this project (local scope — your machine only).
Transport: Remote HTTP → `https://api.githubcopilot.com/mcp`
Token: read from `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable at runtime.

### Usage Rules for Agents

- Always use MCP tools for GitHub operations — never construct raw `curl` calls to the GitHub API
- Reference issue numbers in all branch names and commits (see GIT WORKFLOW SUMMARY)
- Do not create PRs or push branches unless the user explicitly asks

---

## TROUBLESHOOTING

| Symptom | Cause | Fix |
|---------|-------|-----|
| Backend won't start | DB not ready | `docker-compose logs postgres` — wait for "ready" |
| Pydantic validation errors | Schema mismatch | Check `schemas/` vs `models/` alignment |
| Frontend hot reload broken | Vite config | `docker-compose restart frontend` |
| DB migration conflict | Existing schema | `docker-compose down -v && docker-compose up -d` |
| MongoDB auth fails | Wrong credentials | Check `MONGO_URI` in `.env` |
| Tests time out | Redis offline | `docker-compose up -d redis` |
| mypy errors | Missing type hints | Add explicit return type and param types |
| ruff errors | Style violation | Run `ruff check --fix app/` |
