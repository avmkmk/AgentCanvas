# Coding Standards — AgentCanvas

**Applies to**: All code in this repository — Backend (Python/FastAPI), Frontend (TypeScript/React)
**Enforced by**: AI coding agents, code review, CI linting gates
**Last Updated**: 2026-03-03

---

## Purpose

These standards define how code must be written in AgentCanvas. They are specifically designed for **AI-assisted development** — where coding agents (Claude Code, Copilot, etc.) generate code that must be safe, auditable, and maintainable by both humans and agents.

Every coding agent working on this codebase **must follow these standards without exception**.

---

## Standard 1 — Simplicity of Control Flow

> Restrict code to simple, predictable control flow. Complex flow is the #1 source of bugs in AI-generated code.

**Rules:**
- Use `for`/`while` loops for iteration — never recursion
- Use `if`/`else` and `match`/`switch` for branching
- Keep call depth to 5 levels maximum
- Never use `goto`, `setjmp`, `longjmp`, or equivalent hacks
- Each function should have **one entry point and one exit point** where possible

**Python:**
```python
# CORRECT — simple sequential execution
async def execute_flow(self, nodes: list[Node]) -> ExecutionResult:
    results = []
    for step, node in enumerate(nodes, start=1):
        result = await self._run_node(node, step)
        results.append(result)
    return ExecutionResult(steps=results)

# WRONG — recursive execution (stack overflow risk, hard to debug)
async def execute_flow(self, nodes: list[Node], index: int = 0):
    if index >= len(nodes):
        return []
    result = await self._run_node(nodes[index])
    return [result] + await self.execute_flow(nodes, index + 1)
```

**TypeScript:**
```typescript
// CORRECT — linear state transitions
function processNodes(nodes: Node[]): Result[] {
  const results: Result[] = [];
  for (const node of nodes) {
    const result = processNode(node);
    results.push(result);
  }
  return results;
}

// WRONG — chained promises creating implicit execution order
const results = nodes.reduce((acc, node) =>
  acc.then(prev => processNode(node).then(r => [...prev, r])), Promise.resolve([]));
```

---

## Standard 2 — Memory Management

> Avoid resource leaks. Every opened resource must be explicitly closed. All variables must be initialized before use.

**Rules:**
- Always initialize variables at declaration — never declare without assignment
- Use context managers (`with`, `async with`) for all resources in Python
- Use `try/finally` or RAII patterns in TypeScript
- Never access array/list indexes without bounds checking
- Explicitly close database connections, file handles, HTTP clients, WebSocket connections

**Python:**
```python
# CORRECT — context managers guarantee cleanup
async def save_execution(self, data: dict) -> None:
    async with self.db.begin() as session:           # auto-commits/rolls back
        execution = FlowExecution(**data)
        session.add(execution)
    # session automatically closed here

# WRONG — resource leak if exception occurs
async def save_execution(self, data: dict) -> None:
    session = self.db.begin()
    execution = FlowExecution(**data)
    session.add(execution)
    session.commit()
    # session never closed on exception
```

**TypeScript:**
```typescript
// CORRECT — always initialize
const agentCount: number = 0;
const agents: Agent[] = [];

// WRONG — uninitialized variables
let agentCount;
let agents;
```

---

## Standard 3 — Explicitness and Predictability

> Write code where behavior is obvious at a glance. AI agents must never rely on implicit behavior.

**Rules:**
- Make all type casts explicit — never rely on implicit coercion
- Never rely on argument evaluation order in function calls
- Use explicit return types on all functions (Python: type hints, TypeScript: return type annotations)
- Prefer named parameters over positional for functions with 3+ arguments
- Avoid Python `**kwargs` in public API functions — define every parameter explicitly

**Python:**
```python
# CORRECT — explicit types, named params
async def create_execution(
    flow_id: UUID,
    user_id: str,
    max_steps: int = 10,
) -> FlowExecution:
    ...

# WRONG — implicit, no types
async def create_execution(flow_id, user_id, max_steps=10):
    ...
```

**TypeScript:**
```typescript
// CORRECT — explicit types and casts
const nodeCount: number = parseInt(String(rawCount), 10);

// WRONG — implicit coercion
const nodeCount = +rawCount;  // What type is rawCount? What if it's null?
```

---

## Standard 4 — Consistency

> One way to do each thing, applied uniformly. Consistency lets agents reliably read and extend code.

**Rules:**
- Follow naming conventions strictly — see table below
- Use the same pattern for similar operations across the codebase
- When extending existing code, match the surrounding style exactly
- Never mix async and sync code in the same service layer

### Naming Conventions

| Context | Convention | Example |
|---------|-----------|---------|
| Python variables/functions | `snake_case` | `flow_executor`, `run_step()` |
| Python classes | `PascalCase` | `FlowExecutor`, `AgentConfig` |
| Python constants | `UPPER_SNAKE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| TypeScript variables/functions | `camelCase` | `flowExecutor`, `runStep()` |
| TypeScript classes/interfaces/types | `PascalCase` | `FlowExecutor`, `AgentConfig` |
| TypeScript constants (module-level) | `UPPER_SNAKE` | `MAX_RETRIES` |
| TypeScript React components | `PascalCase` | `AgentNode`, `CanvasPanel` |
| API endpoints | `kebab-case` | `/api/flow-executions/{id}` |
| Database tables | `snake_case` | `flow_executions`, `agent_analytics` |
| GitLab branches | `kebab-case` | `feature/123-add-hitl-gate` |
| CSS/Tailwind classes | Follow Tailwind conventions | — |

### File Naming

| Layer | Convention | Example |
|-------|-----------|---------|
| Python modules | `snake_case.py` | `flow_executor.py` |
| TypeScript modules | `camelCase.ts` | `flowExecutor.ts` |
| React components | `PascalCase.tsx` | `AgentNode.tsx` |
| Test files (Python) | `test_<module>.py` | `test_flow_executor.py` |
| Test files (TS) | `<module>.test.ts(x)` | `AgentNode.test.tsx` |

---

## Standard 5 — Error Handling and Checks

> Every operation that can fail must be handled. Silenced errors are forbidden.

**Rules:**
- Check the result of every operation that can fail — database calls, HTTP requests, file I/O, LLM API calls
- Never use bare `except: pass` or catch-all error suppression
- Use specific exception types — never catch `Exception` unless re-raising or logging fully
- Return structured error responses from all API endpoints
- Log all errors with enough context to reproduce the issue
- Distinguish between recoverable errors (retry) and fatal errors (fail fast)

**Python:**
```python
# CORRECT — specific handling with context
async def call_llm(self, prompt: str, agent_id: UUID) -> LLMResponse:
    try:
        response = await self.llm_client.complete(prompt)
        return LLMResponse(content=response.text, tokens=response.usage)
    except RateLimitError as e:
        logger.warning("LLM rate limit hit for agent %s: %s", agent_id, e)
        raise RetryableError("LLM rate limited") from e
    except AuthenticationError as e:
        logger.error("LLM auth failure for agent %s: %s", agent_id, e)
        raise FatalError("LLM authentication failed") from e

# WRONG — swallowed errors
async def call_llm(self, prompt: str) -> LLMResponse:
    try:
        return await self.llm_client.complete(prompt)
    except Exception:
        return None  # Caller has no idea what went wrong
```

**TypeScript:**
```typescript
// CORRECT — typed error handling with user-facing message
async function fetchFlow(id: string): Promise<Flow> {
  const response = await fetch(`/api/flows/${id}`);
  if (!response.ok) {
    throw new ApiError(`Failed to fetch flow ${id}`, response.status);
  }
  return response.json() as Promise<Flow>;
}

// WRONG — ignored error, no type info
async function fetchFlow(id: string) {
  const response = await fetch(`/api/flows/${id}`);
  return response.json();  // What if 404? What if network error?
}
```

---

## Standard 6 — Code Readability

> Code is read 10x more than it is written. Write for the next agent, not for the compiler.

**Rules:**
- Functions must do ONE thing — if you can describe it with "and", split it
- Maximum function length: 50 lines for logic, 100 lines for orchestration
- Maximum file length: 500 lines — split into modules if larger
- Comment the **why**, not the **what** — code explains what, comments explain why
- Avoid deeply nested code — maximum 3 levels of nesting
- Use early returns to reduce nesting (guard clauses)

**Python:**
```python
# CORRECT — guard clauses flatten nesting
async def approve_hitl_review(self, review_id: UUID, reviewer: str) -> HITLReview:
    review = await self.get_review(review_id)
    if review is None:
        raise NotFoundError(f"Review {review_id} not found")
    if review.status != "pending":
        raise ConflictError(f"Review {review_id} already {review.status}")
    if not reviewer:
        raise ValidationError("Reviewer name is required")

    # Core logic is clean and readable
    review.status = "approved"
    review.reviewed_by = reviewer
    review.reviewed_at = datetime.utcnow()
    return await self.save_review(review)

# WRONG — nested pyramid of doom
async def approve_hitl_review(self, review_id: UUID, reviewer: str):
    review = await self.get_review(review_id)
    if review is not None:
        if review.status == "pending":
            if reviewer:
                review.status = "approved"
                # ... more code deep in here
```

---

## Standard 7 — Static Analysis and Testing

> All code must be analyzable by automated tools without special configuration.

**Rules:**
- All Python code must pass: `ruff check`, `black --check`, `mypy --strict` (or relaxed per config)
- All TypeScript code must pass: `eslint`, `tsc --noEmit`
- Avoid dynamic code patterns that defeat analysis: `eval()`, `exec()`, `Function()`, dynamic attribute setting
- Every public function must have a type-annotated signature
- Test coverage must not decrease with any commit

**CI Gates (must pass before merge):**
1. Linting: `ruff check app/` + `eslint src/`
2. Type checking: `mypy app/` + `tsc --noEmit`
3. Unit tests: `pytest tests/unit/` + `vitest run`
4. Integration tests: `pytest tests/integration/`

---

## Standard 8 — Use of Third-Party and AI Components

> External systems are untrusted. Treat all external outputs as potentially invalid.

**Rules:**
- Wrap every third-party library call in a service class — never call external APIs directly from business logic
- Validate all responses from LLM APIs — do not assume the structure is correct
- Pin dependency versions — never use `*` or `latest` in production configs
- Log all external API interactions with request/response metadata (not secrets)
- Implement timeouts on ALL external calls — no call should block indefinitely
- Use circuit breaker or retry logic for LLM and database calls

**Python:**
```python
# CORRECT — isolated, validated, timeout-guarded
class LLMService:
    TIMEOUT_SECONDS = 30

    async def complete(self, prompt: str) -> str:
        async with asyncio.timeout(self.TIMEOUT_SECONDS):
            raw = await self._client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
            )
        # Validate structure — never assume
        if not raw.content or not raw.content[0].text:
            raise LLMResponseError("Empty response from LLM")
        return raw.content[0].text

# WRONG — direct call, no validation, no timeout
async def call_ai(prompt):
    response = await anthropic.messages.create(...)
    return response.content[0].text  # Will crash if structure differs
```

---

## Standard 9 — Safe Use of Resources

> Validate at every boundary. Release everything you acquire.

**Rules:**
- Validate ALL user inputs at the API boundary — use Pydantic (BE) / Zod (FE) schemas
- Never trust data from the database without validation when passing to external systems
- Sanitize any user-provided content before including in LLM prompts (prompt injection prevention)
- Always set maximum sizes: string lengths, array sizes, file sizes, token counts
- Use connection pools — never create ad-hoc database connections
- Set timeouts on all async operations

**Python — Input Validation Example:**
```python
class CreateFlowRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=2000)
    agents: list[AgentConfig] = Field(..., min_length=1, max_length=20)

    @field_validator("name")
    @classmethod
    def name_no_script_tags(cls, v: str) -> str:
        if "<script" in v.lower():
            raise ValueError("Invalid characters in flow name")
        return v.strip()
```

---

## Standard 10 — Reproducibility and Reviewability

> Every piece of code must be reviewable by a human or AI agent in a single reading.

**Rules:**
- No self-modifying code — no `exec()`, `eval()`, dynamic class creation at runtime
- No runtime code generation unless it is sandboxed, reviewed, and explicitly documented
- All configuration must be static (files/env vars) — never computed at import time
- Keep business logic deterministic — document and isolate non-deterministic components (LLM calls, random, time)
- Every non-obvious decision must have a comment or ADR (Architecture Decision Record)

**For AI-Generated Code Specifically:**
- AI agents must not generate code that is more complex than necessary for the task
- When an agent writes a function > 50 lines, it should split it without being asked
- Generated code must include the issue number in a comment if created for a specific feature
- Complex algorithms must include a brief explanation comment before the function

---

## Enforcement

| Tool | Scope | When Run |
|------|-------|----------|
| `ruff` | Python — style + lint | Pre-commit + CI |
| `black` | Python — formatting | Pre-commit + CI |
| `mypy` | Python — types | CI |
| `eslint` | TypeScript — lint | Pre-commit + CI |
| `prettier` | TypeScript — formatting | Pre-commit + CI |
| `tsc` | TypeScript — types | CI |
| `pytest` | Python — tests | CI |
| `vitest` | TypeScript — tests | CI |
| Code Review | Human + AI review | Every MR |
