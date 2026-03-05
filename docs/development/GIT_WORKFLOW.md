# Git Workflow — AgentCanvas

**Applies to**: All contributors and coding agents
**Strategy**: GitLab Flow (feature branches → main, protected main branch)

---

## Branch Strategy

### Branch Types

| Type | Pattern | Purpose | Base Branch |
|------|---------|---------|-------------|
| `feature/` | `feature/<issue-id>-<description>` | New features | `main` |
| `fix/` | `fix/<issue-id>-<description>` | Bug fixes | `main` |
| `docs/` | `docs/<description>` | Documentation only | `main` |
| `chore/` | `chore/<description>` | Tooling, deps, cleanup | `main` |
| `test/` | `test/<description>` | Tests only | `main` |
| `release/` | `release/v<major>.<minor>` | Release preparation | `main` |

### Examples
```
feature/42-add-hitl-before-gate
fix/87-fix-execution-timeout
docs/update-api-reference
chore/upgrade-fastapi-to-0-112
test/add-flow-executor-unit-tests
```

### Protected Branches
- `main` — protected, no direct push. All changes via MR.
- All MRs to `main` require: CI passing + linting green + review

---

## Commit Convention (Conventional Commits)

### Format
```
<type>(<scope>): <short description> [#<issue-id>]

[optional body — explain WHY, not WHAT]

[optional footer: breaking changes, issue closes]
```

### Types

| Type | Use for |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting only (no logic change) |
| `refactor` | Code restructure (no feature/fix) |
| `test` | Adding or fixing tests |
| `chore` | Build, tooling, dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

### Scopes

| Scope | Covers |
|-------|--------|
| `backend` | General backend |
| `frontend` | General frontend |
| `api` | API routes/schemas |
| `canvas` | React Flow canvas |
| `executor` | FlowExecutor core |
| `memory` | Memory management |
| `hitl` | HITL gate logic |
| `analytics` | Analytics and reporting |
| `database` | Schema, migrations |
| `docker` | Docker/Compose config |
| `docs` | Documentation files |
| `session` | Session tracking |

### Examples
```
feat(executor): add retry logic for failed agent steps [#42]
fix(hitl): prevent duplicate approval submissions [#87]
docs(api): document flow execution endpoints
chore(docker): pin postgres image to 15.4
refactor(memory): extract shared memory into separate service [#103]
```

### Multi-file commits
For commits touching multiple scopes, use the primary scope:
```
feat(backend): implement HITL gate with before/after modes [#55]
```

---

## Merge Request (MR) Process

### Creating an MR

1. Branch from `main`:
   ```bash
   git checkout main && git pull origin main
   git checkout -b feature/42-add-hitl-before-gate
   ```

2. Work on the feature (follow coding standards)

3. Before pushing, run locally:
   ```bash
   docker-compose exec backend ruff check app/ && black --check app/
   docker-compose exec frontend npm run lint && npm run type-check
   ```

4. Push and create MR:
   ```bash
   git push -u origin feature/42-add-hitl-before-gate
   # Create MR in GitLab, link to issue #42
   ```

### MR Description Template

```markdown
## Summary
Brief description of what this MR does.

## Related Issue
Closes #<issue-id>

## Changes
- Added X to Y
- Modified Z to support W

## Testing Done
- [ ] Unit tests pass: `pytest tests/unit/`
- [ ] Integration tests pass: `pytest tests/integration/`
- [ ] Frontend tests pass: `npm test`
- [ ] Manual testing: describe what was tested

## Screenshots (if UI change)
[attach screenshots]

## Checklist
- [ ] Follows coding standards (all 10 principles)
- [ ] No hardcoded secrets
- [ ] Type hints complete (Python) / TypeScript types complete
- [ ] Linting passes
- [ ] CHANGELOG.md updated
- [ ] Session log updated
```

### MR Rules
- MR title must reference issue: `feat(executor): add HITL gates [#42]`
- MR must not decrease test coverage
- All CI checks must pass
- At least one approval required (human or designated review agent)
- Squash commits when merging to keep history clean

---

## Commit Message for Session Work

When a coding agent closes or works on an issue, the commit must include:
```
feat(scope): description [#issue-id]

Session: YYYY-MM-DD-NNN
Agent: Claude Sonnet 4.6
Track: track:backend-core

- What was implemented
- Why this approach was taken
```

---

## CHANGELOG.md Format

Every MR that changes functionality must update `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- HITL before/after gate modes [#42]

### Fixed
- Flow execution timeout handling [#87]

### Changed
- Memory service refactored for better isolation [#103]
```

---

## Parallel Agent Workflow

When multiple agents work in parallel:

1. Each agent works on a different track (see CLAUDE.md parallel tracks)
2. Each agent creates its own branch: `feature/<issue-id>-<desc>`
3. Agents must NOT modify the same files simultaneously
4. When tracks share a file (e.g., `docker-compose.yml`), use a sequential handoff
5. Integration is done after all parallel branches are merged to `main`

### Conflict Resolution
- Agent detects conflict → stops work → reports to orchestrator
- Orchestrator assigns resolution to one agent
- Other agents rebase after resolution: `git rebase origin/main`
