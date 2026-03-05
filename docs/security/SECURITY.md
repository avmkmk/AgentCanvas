# Security Guidelines — AgentCanvas

**Applies to**: All code in this repository
**Standard**: OWASP Top 10 + LLM-specific security concerns

---

## Security Principles (from Coding Standards 8, 9)

- All external inputs are untrusted until validated
- External API responses (especially LLMs) are treated as untrusted
- Credentials never appear in code — always in environment variables
- Resources are always released — no file/connection/handle leaks
- Every boundary crossing (API, DB, LLM) has explicit validation

---

## Input Validation

### Rule: Validate at the API boundary with Pydantic (BE) and Zod (FE)

Every endpoint must have a Pydantic schema. Schemas must enforce:
- String length limits (`min_length`, `max_length`)
- Numeric range constraints
- Enum values for fixed-option fields
- No dangerous characters in user-facing string fields

```python
# backend/app/schemas/flow.py
class CreateFlowRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=2000)
    agents: list[AgentConfig] = Field(..., min_length=1, max_length=20)

    @field_validator("name")
    @classmethod
    def name_no_dangerous_chars(cls, v: str) -> str:
        v = v.strip()
        if any(tag in v.lower() for tag in ["<script", "javascript:", "on="]):
            raise ValueError("Invalid characters in flow name")
        return v
```

---

## Prompt Injection Prevention

AgentCanvas sends user-provided content to LLMs. User input in system prompts or agent inputs must be sanitized.

### Attack Vector
User creates an agent with system prompt: `Ignore all previous instructions and...`

### Prevention
```python
# backend/app/utils/prompt_sanitizer.py
INJECTION_PATTERNS = [
    r"ignore (all |previous )?instructions",
    r"you are now",
    r"disregard (your|the) (previous|above)",
    r"act as (a |an )?(?!helpful|professional)",  # allow "act as a professional"
    r"forget everything",
    r"system override",
]

def sanitize_prompt(text: str) -> str:
    """Remove known injection patterns. Returns sanitized text."""
    sanitized = text
    for pattern in INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE)
    return sanitized

# Usage in AgentRunner — always sanitize user-provided content before LLM call
safe_prompt = sanitize_prompt(user_system_prompt)
```

---

## Secrets Management

### Rule: No secrets in code. Ever.

| Secret | How to Store | How to Access |
|--------|-------------|---------------|
| Anthropic API key | `.env` file / Docker secret | `os.getenv("ANTHROPIC_API_KEY")` |
| DB passwords | `.env` file / Docker secret | Connection string from env |
| JWT secret | `.env` file | `os.getenv("JWT_SECRET")` |
| Any API tokens | `.env` file | `os.getenv(...)` |

`.env` file is in `.gitignore`. Use `.env.example` as template with placeholder values only.

### Pattern
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str
    mongodb_url: str
    redis_url: str
    jwt_secret: str
    allowed_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()  # Fails at startup if any required var is missing
```

---

## CORS Configuration

```python
# Never use allow_origins=["*"] in any environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # From env var
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## API Authentication

### MVP: API Key Authentication (Header-based)

```python
# backend/app/api/dependencies.py
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

Use as a FastAPI dependency on protected routers:
```python
@router.post("/executions", dependencies=[Depends(verify_api_key)])
async def start_execution(...):
    ...
```

---

## Rate Limiting

Apply rate limits to LLM-calling endpoints to prevent runaway costs:

```python
# Use slowapi (FastAPI rate limiting)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/executions")
@limiter.limit("10/minute")
async def start_execution(request: Request, ...):
    ...
```

---

## LLM Response Validation

Never assume LLM response structure is correct. Always validate:

```python
async def call_llm(self, prompt: str) -> str:
    raw = await self._client.messages.create(...)

    # Validate — do not assume structure
    if not raw.content:
        raise LLMResponseError("Empty content list in LLM response")
    if not raw.content[0].text:
        raise LLMResponseError("Empty text in LLM response content")

    result = raw.content[0].text

    # Validate length is reasonable
    if len(result) > 50_000:
        raise LLMResponseError("LLM response exceeds maximum length")

    return result
```

---

## Dependency Security

- Pin all Python dependencies with exact versions in `requirements.txt`
- Pin all npm dependencies with exact versions (`package-lock.json` committed)
- Run `pip-audit` and `npm audit` in CI
- Do not add new dependencies without explicit approval

---

## Security Checklist (Pre-MR)

- [ ] No credentials or API keys in code
- [ ] All user inputs validated by Pydantic/Zod schemas
- [ ] User-provided content sanitized before LLM prompts
- [ ] No `except: pass` hiding security errors
- [ ] CORS is not open (`*`)
- [ ] All new dependencies reviewed
- [ ] No `eval()`, `exec()`, or `Function()` calls
