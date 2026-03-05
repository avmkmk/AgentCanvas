# AgentCanvas — Coding Guidelines

**Purpose**: Core principles for writing safe, maintainable, and reviewable code in the AgentCanvas project.

**Category**: Standards  
**Applies to**: Backend (Python/FastAPI), Frontend (TypeScript/React), All subsystems

---

## Overview

These guidelines establish fundamental principles for code quality across AgentCanvas. They complement tool-specific standards (linters, formatters) with higher-level architectural and safety principles.

**Philosophy**: Code should be simple, explicit, safe, and easy to review. Complexity is the enemy of reliability.

---

## 1. Simplicity of Control Flow

**Principle**: Restrict code to simple, predictable control flow. Avoid constructs that make execution paths hard to trace.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Use `for`/`while` loops for iteration | Use recursion (stack overflow risk) |
| Use `if`/`else` and `switch`/`match` | Use `goto` or `setjmp`/`longjmp` |
| Keep execution paths linear and traceable | Create complex nested callbacks |
| Limit function call depth to 5 levels | Deep call chains (6+ levels) |

### Example: Sequential Flow Execution

```python
# ✅ CORRECT - Simple linear flow
async def execute_sequential(self, flow_id: UUID, execution_id: UUID):
    """Execute agents in order with clear steps."""
    nodes = await self.load_nodes(flow_id)
    
    for step_number, node in enumerate(nodes, start=1):
        result = await self._execute_step(node, step_number)
        await self._save_result(result)
        
    return {"status": "completed"}

# ❌ WRONG - Recursive flow (hard to debug, stack overflow risk)
async def execute_recursive(self, nodes: List, index: int = 0):
    """Recursively execute agents."""
    if index >= len(nodes):
        return
    
    result = await self._execute_step(nodes[index])
    return await self.execute_recursive(nodes, index + 1)  # Recursion!
```

**Why**: Simple control flow makes debugging easier, reduces cognitive load, and eliminates entire classes of bugs (stack overflow, goto spaghetti).

---

## 2. Memory & Resource Management

**Principle**: Avoid direct memory management. Always initialize variables. Ensure resources are properly released.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Initialize all variables at declaration | Use uninitialized variables |
| Use `async with` for DB/Redis connections | Forget to close connections |
| Use Pydantic models for structured data | Mutate raw dicts unpredictably |
| Release file handles, sockets explicitly | Leave resources open |

### Example: Proper Resource Management

```python
# ✅ CORRECT - Context manager ensures cleanup
async def get_flow_memory(self, flow_id: UUID) -> Dict:
    """Retrieve flow memory with safe resource handling."""
    async with self.redis.client() as conn:
        data = await conn.hgetall(f"memory:{flow_id}")
    return {k: json.loads(v) for k, v in data.items()}

# ❌ WRONG - Connection not guaranteed to close
async def get_flow_memory_unsafe(self, flow_id: UUID) -> Dict:
    """Retrieve flow memory - UNSAFE."""
    conn = await self.redis.client()
    data = await conn.hgetall(f"memory:{flow_id}")
    # If exception occurs here, conn never closes!
    return {k: json.loads(v) for k, v in data.items()}
```

```typescript
// ✅ CORRECT - Initialized state
const [executionStatus, setExecutionStatus] = useState<ExecutionStatus>({
  id: null,
  status: 'idle',
  currentStep: 0,
  totalSteps: 0
});

// ❌ WRONG - Uninitialized, can be undefined
const [executionStatus, setExecutionStatus] = useState<ExecutionStatus>();
// Later: executionStatus.currentStep will throw if not initialized
```

**Why**: Resource leaks cause production failures. Uninitialized variables cause undefined behavior. Context managers prevent leaks even when exceptions occur.

---

## 3. Explicitness and Predictability

**Principle**: Make all type conversions, assumptions, and operations explicit. Never rely on implicit behavior.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Explicit type casting with validation | Implicit type coercion |
| Explicit Pydantic model conversion | Trust raw dict structure |
| Named arguments for clarity | Rely on positional args only |
| Explicit enum values | Magic numbers/strings |

### Example: Explicit Type Handling

```python
# ✅ CORRECT - Explicit validation and casting
async def create_review(
    self,
    execution_id: UUID,
    agent_id: UUID,
    gate_type: Literal["before", "after", "on_demand"],
    data_to_review: Dict
) -> UUID:
    """Create HITL review with explicit types."""
    # Explicit validation
    if gate_type not in ["before", "after", "on_demand"]:
        raise ValueError(f"Invalid gate_type: {gate_type}")
    
    # Explicit UUID conversion
    review_id = uuid4()
    
    return review_id

# ❌ WRONG - Implicit assumptions, no validation
async def create_review_implicit(self, execution_id, agent_id, gate, data):
    """Create HITL review - IMPLICIT."""
    # Assumes gate is valid string (no check)
    # Assumes execution_id is UUID (might be string!)
    # Assumes data has expected structure
    review_id = uuid4()
    return review_id
```

```typescript
// ✅ CORRECT - Explicit type guards
function isExecutionCompleted(status: ExecutionStatus): boolean {
  return status.status === 'completed' && status.currentStep === status.totalSteps;
}

// ❌ WRONG - Implicit truthiness check
function isExecutionCompleted(status: ExecutionStatus): boolean {
  return status.status && status.currentStep;  // Implicit coercion!
}
```

**Why**: Explicit code is predictable. Implicit behavior causes subtle bugs that are hard to debug across languages/versions.

---

## 4. Consistency

**Principle**: Follow uniform naming conventions, code style, and patterns across the entire codebase.

### Naming Standards

| Element | Python | TypeScript | Example |
|---------|--------|------------|---------|
| Variables | `snake_case` | `camelCase` | `execution_id` / `executionId` |
| Functions | `snake_case` | `camelCase` | `execute_flow()` / `executeFlow()` |
| Classes | `PascalCase` | `PascalCase` | `FlowExecutor` / `AgentNode` |
| Constants | `UPPER_SNAKE` | `UPPER_SNAKE` | `MAX_RETRIES` / `TIMEOUT_MS` |
| Private methods | `_snake_case` | `#camelCase` | `_handle_error()` / `#validateInput()` |
| Booleans | `is_/has_/should_` | `is/has/should` | `is_completed` / `isCompleted` |

### Example: Consistent Naming

```python
# ✅ CORRECT - Consistent Python conventions
class FlowExecutor:
    MAX_RETRY_ATTEMPTS = 3  # Constant
    
    def __init__(self, db_client):
        self.db_client = db_client  # Instance variable
        self._retry_count = 0  # Private variable
    
    async def execute_flow(self, flow_id: UUID) -> Dict:  # Public method
        """Execute a flow."""
        return await self._run_steps(flow_id)  # Private method
    
    async def _run_steps(self, flow_id: UUID) -> Dict:
        """Internal step execution."""
        pass

# ❌ WRONG - Mixed conventions
class flowExecutor:  # Wrong: should be PascalCase
    maxRetries = 3  # Wrong: should be UPPER_SNAKE
    
    def __init__(self, DBClient):  # Wrong: parameter should be snake_case
        self.DBClient = DBClient  # Wrong: attribute should be snake_case
    
    async def ExecuteFlow(self, FlowID):  # Wrong: should be snake_case
        return await self.runSteps(FlowID)  # Inconsistent: mix of conventions
```

**Why**: Consistency reduces cognitive load. Developers instantly recognize what something is by its name pattern.

---

## 5. Error Handling and Checks

**Principle**: Check the result of every operation that can fail. Handle all exceptional conditions explicitly.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Wrap all async operations in try/except | Use bare `except:` without logging |
| Check for None/null before accessing | Assume values always exist |
| Validate LLM responses before use | Pass through unchecked responses |
| Log all caught exceptions with context | Silently swallow errors |
| Raise custom exceptions with details | Raise generic `Exception` |

### Example: Proper Error Handling

```python
# ✅ CORRECT - Comprehensive error handling
async def execute_agent_with_retry(
    self,
    agent,
    context: Dict,
    max_retries: int = 3
) -> Dict:
    """Execute agent with retry logic and error handling."""
    for attempt in range(max_retries):
        try:
            # Timeout protection
            result = await asyncio.wait_for(
                agent.run(context),
                timeout=120
            )
            
            # Validate result structure
            if not result or "content" not in result:
                raise ValueError(f"Invalid agent response: {result}")
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(
                f"Agent timeout on attempt {attempt + 1}/{max_retries}",
                extra={"agent_id": agent.id, "context": context}
            )
            if attempt == max_retries - 1:
                raise AgentTimeoutError(
                    f"Agent failed after {max_retries} attempts"
                )
        
        except Exception as e:
            logger.error(
                f"Agent execution failed: {str(e)}",
                extra={"agent_id": agent.id, "attempt": attempt},
                exc_info=True
            )
            if attempt == max_retries - 1:
                raise AgentExecutionError(f"Agent failed: {str(e)}") from e
        
        await asyncio.sleep(2 ** attempt)  # Exponential backoff

# ❌ WRONG - Silent failure, no validation
async def execute_agent_unsafe(self, agent, context):
    """Execute agent - UNSAFE."""
    try:
        result = await agent.run(context)
        return result  # No validation!
    except:  # Bare except!
        return {}  # Silent failure!
```

```typescript
// ✅ CORRECT - Checked API call with error handling
async function fetchExecutionStatus(executionId: string): Promise<ExecutionStatus> {
  try {
    const response = await axios.get(`/api/v1/executions/${executionId}`);
    
    // Validate response structure
    if (!response.data || !response.data.status) {
      throw new Error('Invalid response structure');
    }
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      logger.error('Failed to fetch execution status', {
        executionId,
        status: error.response?.status,
        message: error.message
      });
      throw new APIError(`Failed to fetch execution: ${error.message}`);
    }
    throw error;
  }
}

// ❌ WRONG - No error handling, no validation
async function fetchExecutionStatusUnsafe(executionId: string) {
  const response = await axios.get(`/api/v1/executions/${executionId}`);
  return response.data;  // Might be undefined! No error handling!
}
```

**Why**: Every production failure starts with an unhandled error. Explicit error handling prevents cascading failures and makes debugging possible.

---

## 6. Code Readability

**Principle**: Write code that is easy to understand. Keep functions focused. Explain "why," not "what."

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Functions ≤ 50 lines | Functions > 100 lines |
| Max 3 levels of nesting | 4+ levels of nesting |
| One responsibility per function | Functions that do multiple things |
| Comment "why" and "gotchas" | Comment obvious code |
| Descriptive variable names | Single-letter names (except `i`, `e`) |

### Example: Readable Code

```python
# ✅ CORRECT - Clear, focused, well-documented
async def handle_hitl_gate(
    self,
    execution_id: UUID,
    agent_id: UUID,
    gate_type: str,
    output: Dict
) -> Dict:
    """
    Handle HITL review gate and wait for human decision.
    
    Pauses flow execution until a human approves/rejects the output.
    Uses Redis pub/sub to avoid polling.
    
    Returns:
        {'approved': bool, 'comments': str}
    """
    # Create review request in database and queue
    review_id = await self.hitl_manager.create_review(
        execution_id=execution_id,
        agent_id=agent_id,
        gate_type=gate_type,
        data_to_review=output
    )
    
    # Pause execution (non-blocking via pub/sub)
    await self._update_execution_status(execution_id, "paused_hitl")
    
    # Wait for human decision (blocks this coroutine only)
    # NOTE: Uses pub/sub, not polling, for instant notification
    approval = await self.hitl_manager.wait_for_approval(review_id)
    
    # Resume execution
    await self._update_execution_status(execution_id, "running")
    
    return approval

# ❌ WRONG - Too long, too complex, poorly named
async def h(self, e, a, g, o):  # Cryptic names
    """Handle gate."""  # Vague docstring
    r = await self.hitl_manager.create_review(e, a, g, o)
    await self._update_execution_status(e, "paused_hitl")
    
    # Long complex logic mixed in (should be extracted)
    if g == "before":
        if o.get("validated"):
            if not o.get("approved"):
                # Deep nesting (4+ levels)
                if r:
                    if await self._check_retry(r):
                        # More nesting...
                        pass
    
    a = await self.hitl_manager.wait_for_approval(r)
    await self._update_execution_status(e, "running")
    return a
```

### Nesting Example

```typescript
// ✅ CORRECT - Early returns, max 2 levels
function validateFlowConfig(config: FlowConfig): ValidationResult {
  if (!config.nodes || config.nodes.length === 0) {
    return { valid: false, error: 'No nodes defined' };
  }
  
  if (!config.edges || config.edges.length === 0) {
    return { valid: false, error: 'No edges defined' };
  }
  
  // Validate node connections
  const nodeIds = new Set(config.nodes.map(n => n.id));
  for (const edge of config.edges) {
    if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
      return { valid: false, error: `Invalid edge: ${edge.id}` };
    }
  }
  
  return { valid: true };
}

// ❌ WRONG - Deep nesting (4 levels)
function validateFlowConfigBad(config: FlowConfig): ValidationResult {
  if (config.nodes && config.nodes.length > 0) {
    if (config.edges && config.edges.length > 0) {
      const nodeIds = new Set(config.nodes.map(n => n.id));
      for (const edge of config.edges) {
        if (nodeIds.has(edge.source)) {
          if (nodeIds.has(edge.target)) {
            // Valid
          } else {
            return { valid: false, error: 'Invalid target' };
          }
        }
      }
    }
  }
  return { valid: true };
}
```

**Why**: Readable code is maintainable code. Complex code takes longer to review, has more bugs, and is harder to modify.

---

## 7. Static Analysis and Testing

**Principle**: Write code that static analyzers can verify. Ensure robust test coverage.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Use type hints on all functions | Skip type hints |
| Run `ruff`, `mypy` on Python | Ignore linter warnings |
| Run `eslint`, `tsc --noEmit` on TS | Use `@ts-ignore` without reason |
| Write unit tests for core logic | Skip tests "because it's obvious" |
| Test error paths, not just happy paths | Only test success cases |

### Example: Type-Safe Code

```python
# ✅ CORRECT - Fully typed, analyzable
from typing import Dict, List, Optional, UUID
from pydantic import BaseModel

class AgentConfig(BaseModel):
    """Typed agent configuration."""
    id: UUID
    name: str
    role: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000

async def load_agent_config(agent_id: UUID) -> Optional[AgentConfig]:
    """Load agent configuration with full type safety."""
    row = await db.fetchrow(
        "SELECT * FROM agents WHERE id = $1", agent_id
    )
    
    if not row:
        return None
    
    # Pydantic validates structure
    return AgentConfig(**dict(row))

# ❌ WRONG - No types, analyzer can't help
async def load_agent_config_unsafe(agent_id):  # No type hint
    """Load agent config - UNSAFE."""
    row = await db.fetchrow(
        "SELECT * FROM agents WHERE id = $1", agent_id
    )
    # Returns Any type, analyzer can't verify downstream usage
    return dict(row) if row else None
```

```typescript
// ✅ CORRECT - Strict typing
interface AgentNode {
  id: string;
  type: 'agent';
  data: {
    agentId: string;
    name: string;
    role: AgentRole;
    config: AgentConfig;
  };
}

function getAgentName(node: AgentNode): string {
  return node.data.name;  // Type-checked!
}

// ❌ WRONG - Any types, no safety
function getAgentNameUnsafe(node: any): any {
  return node.data.name;  // No type checking, runtime error if structure wrong
}
```

### Testing Example

```python
# ✅ CORRECT - Test both success and failure
@pytest.mark.asyncio
async def test_execute_agent_success():
    """Test successful agent execution."""
    agent = MockAgent()
    executor = FlowExecutor(...)
    
    result = await executor.execute_agent_with_retry(agent, {})
    
    assert result["content"] == "expected output"
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_execute_agent_timeout():
    """Test agent timeout handling."""
    agent = SlowMockAgent(delay=200)  # Exceeds 120s timeout
    executor = FlowExecutor(...)
    
    with pytest.raises(AgentTimeoutError):
        await executor.execute_agent_with_retry(agent, {})

@pytest.mark.asyncio
async def test_execute_agent_invalid_response():
    """Test handling of malformed agent responses."""
    agent = MockAgent(response={"invalid": "structure"})
    executor = FlowExecutor(...)
    
    with pytest.raises(ValueError, match="Invalid agent response"):
        await executor.execute_agent_with_retry(agent, {})
```

**Why**: Static analysis catches bugs before runtime. Tests document expected behavior and prevent regressions.

---

## 8. Use of Third-Party / AI Components

**Principle**: Validate all external inputs and outputs. Handle AI/LLM responses defensively.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Validate LLM response structure | Trust LLM output directly |
| Check for empty/malformed responses | Assume responses are well-formed |
| Parse JSON outputs with error handling | Use `json.loads()` without try/catch |
| Set timeouts on all LLM calls | Wait indefinitely for responses |
| Validate tool outputs before chaining | Chain outputs blindly |

### Example: Defensive LLM Handling

```python
# ✅ CORRECT - Defensive validation of LLM output
from typing import Dict, Optional
import json

async def call_llm_safely(
    self,
    model: str,
    prompt: str,
    system_prompt: str
) -> Dict:
    """
    Call LLM with defensive validation.
    
    Validates response structure and handles malformed outputs.
    """
    try:
        # Timeout protection (120s max)
        response = await asyncio.wait_for(
            litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            ),
            timeout=120
        )
        
        # Validate response structure
        if not response or not response.choices:
            raise ValueError("Empty LLM response")
        
        content = response.choices[0].message.content
        
        # Validate content is not empty
        if not content or not content.strip():
            raise ValueError("LLM returned empty content")
        
        # If expecting JSON, validate it parses
        if self._is_json_expected(prompt):
            try:
                parsed = json.loads(content)
                # Validate expected keys exist
                if not self._validate_json_structure(parsed):
                    raise ValueError(f"Invalid JSON structure: {parsed}")
            except json.JSONDecodeError as e:
                raise ValueError(f"LLM returned invalid JSON: {str(e)}")
        
        return {
            "content": content,
            "model": model,
            "tokens": response.usage.total_tokens if response.usage else 0,
            "validated": True
        }
        
    except asyncio.TimeoutError:
        logger.error(f"LLM call timed out after 120s: model={model}")
        raise LLMTimeoutError(f"LLM call to {model} timed out")
    
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}", exc_info=True)
        raise LLMError(f"LLM call failed: {str(e)}") from e

# ❌ WRONG - No validation, no error handling
async def call_llm_unsafe(self, model, prompt, system_prompt):
    """Call LLM - UNSAFE."""
    response = await litellm.acompletion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    # Assumes response is valid, assumes choices exist, no timeout
    return response.choices[0].message.content
```

```typescript
// ✅ CORRECT - Validate third-party API response
async function fetchAgentTemplates(): Promise<AgentTemplate[]> {
  try {
    const response = await axios.get('/api/v1/templates');
    
    // Validate response structure
    if (!response.data || !Array.isArray(response.data.templates)) {
      throw new Error('Invalid templates response structure');
    }
    
    // Validate each template has required fields
    const templates = response.data.templates;
    for (const template of templates) {
      if (!template.id || !template.name || !template.systemPrompt) {
        throw new Error(`Invalid template structure: ${JSON.stringify(template)}`);
      }
    }
    
    return templates;
    
  } catch (error) {
    logger.error('Failed to fetch templates', { error });
    // Return safe default rather than crashing
    return DEFAULT_TEMPLATES;
  }
}

// ❌ WRONG - No validation
async function fetchAgentTemplatesUnsafe() {
  const response = await axios.get('/api/v1/templates');
  return response.data.templates;  // Might not exist! Might not be array!
}
```

**Why**: AI/LLM outputs are non-deterministic and can be malformed. External APIs can return unexpected data. Defensive validation prevents cascading failures.

---

## 9. Safe Use of Resources

**Principle**: Validate all inputs and outputs. Always release resources. No blind trust.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Validate all user inputs with Pydantic | Trust input structure |
| Sanitize inputs before DB queries | Concatenate user input into SQL |
| Use connection pools for DB/Redis | Create new connections per request |
| Close file handles explicitly | Leave files open |
| Check API rate limits before calling | Spam external APIs |

### Example: Input Validation

```python
# ✅ CORRECT - Strict input validation
from pydantic import BaseModel, Field, validator
from typing import Literal

class CreateFlowRequest(BaseModel):
    """Validated flow creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=1000)
    flow_config: Dict = Field(...)
    
    @validator('name')
    def name_no_special_chars(cls, v):
        """Ensure name contains only safe characters."""
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        if any(c in v for c in ['<', '>', '"', "'"]):
            raise ValueError('Name contains invalid characters')
        return v.strip()
    
    @validator('flow_config')
    def validate_flow_structure(cls, v):
        """Ensure flow config has required structure."""
        if 'nodes' not in v or 'edges' not in v:
            raise ValueError('Flow config must have nodes and edges')
        if not isinstance(v['nodes'], list):
            raise ValueError('Nodes must be a list')
        return v

@router.post("/flows")
async def create_flow(request: CreateFlowRequest):
    """
    Create flow with validated input.
    
    Pydantic validates structure before this function runs.
    """
    flow_id = await flow_service.create(
        name=request.name,
        description=request.description,
        config=request.flow_config
    )
    return {"id": flow_id}

# ❌ WRONG - No validation, SQL injection risk
@router.post("/flows")
async def create_flow_unsafe(request: Dict):
    """Create flow - UNSAFE."""
    # No validation! Could be malformed!
    name = request.get("name")  # Might be None, empty, or malicious
    config = request.get("flow_config")  # Might be invalid structure
    
    # SQL injection risk if name contains quotes!
    await db.execute(f"INSERT INTO flows (name) VALUES ('{name}')")
```

### Example: Resource Cleanup

```python
# ✅ CORRECT - Guaranteed cleanup with context manager
async def process_large_file(file_path: str) -> Dict:
    """Process file with guaranteed cleanup."""
    result = {"lines_processed": 0, "errors": 0}
    
    # File automatically closed even if exception occurs
    async with aiofiles.open(file_path, 'r') as f:
        async for line in f:
            try:
                await process_line(line)
                result["lines_processed"] += 1
            except Exception as e:
                logger.error(f"Failed to process line: {e}")
                result["errors"] += 1
    
    return result

# ❌ WRONG - File handle leak if exception occurs
async def process_large_file_unsafe(file_path: str) -> Dict:
    """Process file - UNSAFE."""
    f = await aiofiles.open(file_path, 'r')
    result = {"lines_processed": 0}
    
    async for line in f:
        await process_line(line)  # If this raises, f never closes!
        result["lines_processed"] += 1
    
    await f.close()  # Never reached if exception above
    return result
```

**Why**: Unvalidated inputs are the #1 source of security vulnerabilities. Resource leaks cause memory exhaustion and system crashes.

---

## 10. Reproducibility and Reviewability

**Principle**: Code must be easy to audit and debug. Avoid runtime code generation. Ensure deterministic behavior.

### Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Version control all agent prompts | Generate prompts dynamically at runtime |
| Use explicit configuration files | Use `eval()` or `exec()` |
| Log all decisions with full context | Modify code at runtime |
| Make execution deterministic (when possible) | Rely on random behavior without seed |
| Document all environment dependencies | Hidden dependencies |

### Example: Version-Controlled Prompts

```python
# ✅ CORRECT - Prompts in version control, auditable
# File: backend/app/prompts/agent_templates.py

RESEARCHER_SYSTEM_PROMPT = """
You are a research assistant who finds and summarizes information thoroughly.

Your responsibilities:
- Search for relevant information on the given topic
- Verify information from multiple sources
- Provide clear, well-structured summaries
- Cite sources when possible

Guidelines:
- Be thorough but concise
- Focus on factual information
- Use bullet points for clarity
"""

ANALYST_SYSTEM_PROMPT = """
You are a strategic analyst who examines information and provides actionable insights.

Analysis Framework:
1. TRENDS: What patterns are emerging?
2. RISKS: What challenges or threats exist?
3. OPPORTUNITIES: Where are the growth areas?
4. RECOMMENDATIONS: What actions should be taken?
"""

def get_system_prompt(role: str) -> str:
    """
    Get system prompt for agent role.
    
    All prompts are static and version-controlled for auditability.
    """
    prompts = {
        "researcher": RESEARCHER_SYSTEM_PROMPT,
        "analyst": ANALYST_SYSTEM_PROMPT,
    }
    
    if role not in prompts:
        raise ValueError(f"Unknown role: {role}")
    
    return prompts[role]

# ❌ WRONG - Dynamic prompt generation, not auditable
def get_system_prompt_dynamic(role: str, user_preferences: Dict) -> str:
    """Generate prompt dynamically - NOT REVIEWABLE."""
    # Prompt changes based on runtime data, can't audit behavior
    base = "You are a helpful assistant. "
    
    if user_preferences.get("style") == "formal":
        base += "Be formal and professional. "
    else:
        base += "Be casual and friendly. "
    
    # Adding user-provided content to prompt (security risk!)
    if user_preferences.get("custom_instructions"):
        base += user_preferences["custom_instructions"]
    
    return base  # Different every time, can't reproduce bugs
```

### Example: Reproducible Execution

```python
# ✅ CORRECT - Deterministic with explicit random seed
import random
from typing import Optional

async def execute_with_reproducibility(
    flow_id: UUID,
    execution_id: UUID,
    random_seed: Optional[int] = None
) -> Dict:
    """
    Execute flow with optional reproducibility.
    
    If random_seed provided, execution is deterministic and can be replayed.
    """
    if random_seed is not None:
        random.seed(random_seed)
        logger.info(f"Execution {execution_id} using random seed: {random_seed}")
    
    # Log all configuration for reproducibility
    logger.info(
        "Starting execution",
        extra={
            "flow_id": str(flow_id),
            "execution_id": str(execution_id),
            "timestamp": datetime.utcnow().isoformat(),
            "python_version": sys.version,
            "random_seed": random_seed
        }
    )
    
    result = await self._execute_flow(flow_id, execution_id)
    
    return result

# ❌ WRONG - Non-reproducible, can't debug failures
async def execute_non_reproducible(flow_id, execution_id):
    """Execute flow - NOT REPRODUCIBLE."""
    # Uses random behavior without seed
    if random.random() > 0.5:
        strategy = "parallel"
    else:
        strategy = "sequential"
    
    # Can't reproduce this execution later to debug!
    result = await self._execute_flow(flow_id, execution_id, strategy)
    return result
```

### No Runtime Code Generation

```python
# ✅ CORRECT - Static configuration, type-safe
from enum import Enum

class AgentRole(str, Enum):
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"

def create_agent(role: AgentRole, config: Dict) -> Agent:
    """Create agent using static factory pattern."""
    agent_classes = {
        AgentRole.RESEARCHER: ResearcherAgent,
        AgentRole.ANALYST: AnalystAgent,
        AgentRole.WRITER: WriterAgent,
    }
    
    agent_class = agent_classes.get(role)
    if not agent_class:
        raise ValueError(f"Unknown role: {role}")
    
    return agent_class(config)

# ❌ WRONG - Runtime code generation, security risk
def create_agent_dynamic(role: str, code: str) -> Agent:
    """Create agent dynamically - DANGEROUS."""
    # NEVER do this! Security risk, not auditable
    exec(code)  # Executes arbitrary code!
    return eval(f"{role}Agent()")  # Can't review what this does
```

**Why**: Code that modifies itself or generates prompts dynamically is impossible to audit. Deterministic execution makes debugging possible. Version-controlled artifacts enable forensics.

---

## Summary Checklist

Before submitting code for review, verify:

- [ ] **Control Flow**: Simple, linear, no recursion
- [ ] **Resources**: All connections/files properly closed
- [ ] **Explicitness**: All types explicit, no implicit coercion
- [ ] **Consistency**: Naming follows project conventions
- [ ] **Error Handling**: All operations checked, exceptions logged
- [ ] **Readability**: Functions < 50 lines, nesting ≤ 3 levels
- [ ] **Static Analysis**: Passes `ruff`/`mypy`/`eslint`/`tsc`
- [ ] **Third-Party Safety**: LLM/API responses validated
- [ ] **Resource Safety**: Inputs validated, outputs sanitized
- [ ] **Reproducibility**: No runtime code gen, deterministic where possible

---

## Related Standards

- **Code Quality**: `.codemie/guides/standards/code-quality.md` — Tool-specific linter/formatter rules
- **Git Workflow**: `.codemie/guides/standards/git-workflow.md` — Branching, commits, PRs
- **Testing Patterns**: `.codemie/guides/testing/testing-patterns.md` — Unit/integration test patterns
- **Error Handling**: `.codemie/guides/development/error-handling.md` — Exception patterns
- **Security Patterns**: `.codemie/guides/security/security-patterns.md` — Authentication, validation

---

**Last Updated**: 2026-03-03  
**Version**: 1.0
