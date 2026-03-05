# Testing Strategy — AgentCanvas

**Applies to**: Backend (Python/pytest) and Frontend (TypeScript/Vitest)
**Requirement**: Test coverage must not decrease with any commit.

---

## Testing Pyramid

```
        ┌────────────────┐
        │   E2E Tests    │  ← Few, slow, validate full flows
        │  (Playwright)  │     Phase 2 only
        ├────────────────┤
        │  Integration   │  ← API + DB + service interactions
        │    Tests       │     Required for all API endpoints
        ├────────────────┤
        │   Unit Tests   │  ← Business logic in isolation
        │                │     Required for all core services
        └────────────────┘
```

---

## Backend Testing (Python + pytest)

### Structure
```
backend/
└── tests/
    ├── conftest.py           # Fixtures: DB, test client, mocks
    ├── unit/
    │   ├── test_flow_executor.py
    │   ├── test_hitl_manager.py
    │   ├── test_memory_service.py
    │   └── test_llm_service.py
    └── integration/
        ├── test_flows_api.py
        ├── test_executions_api.py
        ├── test_hitl_api.py
        └── test_analytics_api.py
```

### Running Tests (inside container)
```bash
# All tests
docker-compose exec backend pytest

# Unit tests only
docker-compose exec backend pytest tests/unit/

# Integration tests only
docker-compose exec backend pytest tests/integration/

# With coverage report
docker-compose exec backend pytest --cov=app --cov-report=term-missing

# Specific test
docker-compose exec backend pytest tests/unit/test_flow_executor.py::test_sequential_execution
```

### Coverage Requirements
| Module | Minimum Coverage |
|--------|-----------------|
| `core/flow_executor.py` | 80% |
| `core/hitl_manager.py` | 80% |
| `memory/memory_service.py` | 75% |
| `services/llm_service.py` | 70% |
| `api/*.py` (routers) | 70% |

### Key Test Patterns

**Unit Test — Service in Isolation (mock external calls):**
```python
# tests/unit/test_flow_executor.py
import pytest
from unittest.mock import AsyncMock, patch
from app.core.flow_executor import FlowExecutor
from tests.factories import FlowFactory, AgentFactory

@pytest.mark.asyncio
async def test_sequential_execution_calls_agents_in_order(db_session, mock_llm):
    """FlowExecutor must call agents in step order, passing output forward."""
    flow = FlowFactory.create(agents=[AgentFactory.create(step=1), AgentFactory.create(step=2)])
    executor = FlowExecutor(db=db_session, llm=mock_llm)

    result = await executor.execute(flow.id)

    assert result.status == "completed"
    assert mock_llm.complete.call_count == 2
    # Step 2 input should contain step 1 output
    second_call_prompt = mock_llm.complete.call_args_list[1][0][0]
    assert "step_1_output" in second_call_prompt

@pytest.mark.asyncio
async def test_execution_stops_on_hitl_gate(db_session, mock_llm):
    """FlowExecutor must pause and create a review when HITL gate is hit."""
    agent = AgentFactory.create(hitl_config={"gate_type": "after", "enabled": True})
    flow = FlowFactory.create(agents=[agent])
    executor = FlowExecutor(db=db_session, llm=mock_llm)

    result = await executor.execute(flow.id)

    assert result.status == "paused_hitl"
    hitl_reviews = await db_session.query(HITLReview).filter_by(execution_id=result.id).all()
    assert len(hitl_reviews) == 1
    assert hitl_reviews[0].status == "pending"
```

**Integration Test — API endpoint with real DB:**
```python
# tests/integration/test_executions_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_start_execution_returns_execution_id(client: AsyncClient, saved_flow):
    """POST /executions must create and return an execution record."""
    response = await client.post("/api/executions", json={"flow_id": str(saved_flow.id)})

    assert response.status_code == 202
    data = response.json()
    assert "execution_id" in data
    assert data["status"] == "running"

@pytest.mark.asyncio
async def test_start_execution_with_invalid_flow_returns_404(client: AsyncClient):
    response = await client.post("/api/executions", json={"flow_id": "00000000-0000-0000-0000-000000000000"})
    assert response.status_code == 404
```

### Fixtures (conftest.py)
```python
# Always mock LLM in tests — never call real API
@pytest.fixture
def mock_llm():
    with patch("app.services.llm_service.LLMService.complete") as mock:
        mock.return_value = AsyncMock(return_value="Mocked LLM response")
        yield mock

# Use test database (separate from dev)
@pytest.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(test_engine) as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

---

## Frontend Testing (TypeScript + Vitest)

### Structure
```
frontend/src/
└── __tests__/
    ├── components/
    │   ├── AgentNode.test.tsx
    │   ├── ConfigPanel.test.tsx
    │   ├── HITLReviewModal.test.tsx
    │   └── ExecutionLog.test.tsx
    ├── hooks/
    │   ├── useFlow.test.ts
    │   └── useExecution.test.ts
    └── utils/
        └── promptSanitizer.test.ts
```

### Running Tests (inside container)
```bash
# All tests
docker-compose exec frontend npm test

# Watch mode (dev)
docker-compose exec frontend npm run test:watch

# With coverage
docker-compose exec frontend npm run test:coverage
```

### Coverage Requirements
| Area | Minimum |
|------|---------|
| `core/` business logic utils | 75% |
| Custom hooks | 70% |
| Critical components (HITL, Canvas) | 60% |

### Key Test Pattern (Component + Mock API)
```typescript
// __tests__/components/HITLReviewModal.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { HITLReviewModal } from '../../components/hitl/HITLReviewModal';
import { vi } from 'vitest';

const mockApprove = vi.fn();

describe('HITLReviewModal', () => {
  it('calls approve handler when Approve button clicked', async () => {
    render(
      <HITLReviewModal
        review={{ id: '123', output: 'Agent output here', gate_type: 'after' }}
        onApprove={mockApprove}
        onReject={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /approve/i }));

    await waitFor(() => expect(mockApprove).toHaveBeenCalledWith('123'));
  });

  it('shows the agent output in review content', () => {
    render(<HITLReviewModal review={{ id: '1', output: 'Expected output', gate_type: 'after' }} onApprove={vi.fn()} onReject={vi.fn()} />);
    expect(screen.getByText('Expected output')).toBeInTheDocument();
  });
});
```

---

## What NOT to Test

- Third-party library internals (React Flow, Zustand internals)
- Framework-provided behavior (FastAPI validation for standard types)
- Database driver behavior
- Docker/network infrastructure

Focus tests on **your business logic** — the code you wrote.

---

## CI Test Gates

All must pass before any MR can be merged:

```yaml
# .gitlab-ci.yml
test:backend:
  script:
    - docker-compose exec -T backend ruff check app/
    - docker-compose exec -T backend mypy app/
    - docker-compose exec -T backend pytest --cov=app --cov-fail-under=70

test:frontend:
  script:
    - docker-compose exec -T frontend npm run lint
    - docker-compose exec -T frontend npm run type-check
    - docker-compose exec -T frontend npm run test:coverage
```
