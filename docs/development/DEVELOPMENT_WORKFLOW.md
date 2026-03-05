# Development Workflow Guide

This guide provides a comprehensive overview of the development workflow, from daily procedures to coding best practices.

## 1. Daily Workflow

### Morning Setup (5 minutes)

Start your day by getting the latest code and ensuring all services are running.

```bash
# 1. Navigate to the project directory
cd multi-agent-orchestrator

# 2. Pull the latest changes from the main branch
git pull origin main

# 3. Start all services in detached mode
docker-compose up -d

# 4. Wait for services to become healthy (approx. 30 seconds)
# Check the status of all containers
docker-compose ps

# 5. Verify that the backend and frontend are responsive
curl http://localhost:8080/health
open http://localhost:3000
```

### Git Workflow

Follow this process for feature development to maintain a clean and understandable commit history.

#### Feature Development

1.  **Create a feature branch** from the `main` branch.
    ```bash
    git checkout -b feature/your-feature-name
    ```
2.  **Make your code changes.**
3.  **Check the status** of your changes.
    ```bash
    git status
    ```
4.  **Stage your changes.**
    ```bash
    git add .
    ```
5.  **Commit with a meaningful message** following the conventional commits standard.
    ```bash
    git commit -m "feat(backend): Add new analytics endpoint"
    ```
6.  **Push your branch** to the remote repository.
    ```bash
    git push origin feature/your-feature-name
    ```
7.  **Create a Pull Request** on GitHub for review.

#### Commit Message Convention

Using conventional commits helps automate changelog generation and makes the project history more readable.

*   `feat`: A new feature (e.g., `feat(frontend): Add agent config panel`)
*   `fix`: A bug fix (e.g., `fix(backend): Correct memory context bug`)
*   `docs`: Documentation changes
*   `style`: Code style changes (formatting, etc.)
*   `refactor`: Code changes that neither fix a bug nor add a feature
*   `test`: Adding or updating tests
*   `chore`: Maintenance tasks (e.g., updating dependencies)

---

## 2. Backend Development

### Hot Reload

The backend uses `uvicorn` with `--reload`, so any changes to Python files will automatically restart the server.

```yaml
# docker-compose.yml snippet
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
  volumes:
    - ./backend:/app
```

### Running Tests

Execute tests within the running `backend` container.

```bash
# Run all tests
docker-compose exec backend pytest

# Run a specific test file
docker-compose exec backend pytest tests/test_flow_executor.py

# Run with code coverage
docker-compose exec backend pytest --cov=app tests/

# Run a specific test function
docker-compose exec backend pytest tests/test_flow_executor.py::test_sequential_execution
```

### Database Access

Directly access the databases for debugging.

```bash
# PostgreSQL
docker-compose exec postgres psql -U admin -d orchestrator

# MongoDB
docker-compose exec mongodb mongosh -u admin -p admin123

# Redis
docker-compose exec redis redis-cli
```

---

## 3. Frontend Development

### Hot Reload

The frontend uses Vite's Hot Module Replacement (HMR). Changes to React components or other frontend files will be reflected in the browser almost instantly without a full page reload.

### Running Tests

Execute frontend tests using `npm test`.

```bash
# Run all tests
docker-compose exec frontend npm test

# Run tests with coverage
docker-compose exec frontend npm run test:coverage
```

### Type Checking & Linting

Ensure code quality before committing.

```bash
# Check for TypeScript errors
docker-compose exec frontend npm run type-check

# Lint files with ESLint
docker-compose exec frontend npm run lint

# Automatically fix linting issues
docker-compose exec frontend npm run lint:fix

# Format code with Prettier
docker-compose exec frontend npm run format
```

---

## 4. Code Organization

### Backend Structure

```
backend/app/
├── api/              # API endpoints (FastAPI routers)
├── core/             # Core business logic (FlowExecutor, etc.)
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic data validation schemas
├── services/         # Clients for external services (LLM, etc.)
├── memory/           # Memory management modules
└── utils/            # Shared utility functions
```

### Frontend Structure

```
frontend/src/
├── components/       # Reusable React components
├── hooks/            # Custom React hooks (e.g., useFlow)
├── services/         # API clients and WebSocket service
├── store/            # Zustand state management stores
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
```

---

## 5. Productivity Tips

### Command Line Aliases

Add these to your `~/.bashrc` or `~/.zshrc` to save time.

```bash
alias dc='docker-compose'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcrestart='docker-compose restart'
alias be='docker-compose exec backend'
alias fe='docker-compose exec frontend'
alias db='docker-compose exec postgres psql -U admin -d orchestrator'
```

### VS Code Extensions

Install these recommended extensions for an optimal development experience. They are also listed in `.vscode/extensions.json`.

*   Python (ms-python.python)
*   Pylance (ms-python.vscode-pylance)
*   ESLint (dbaeumer.vscode-eslint)
*   Prettier - Code formatter (esbenp.prettier-vscode)
*   Docker (ms-azuretools.vscode-docker)
*   Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
