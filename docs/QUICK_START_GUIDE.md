# Quick Start Guide

This guide will get you from zero to a running application in under 15 minutes.

## 1. Prerequisites (2 minutes)

Make sure you have the following software installed:

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   [Git](https://git-scm.com/downloads)
*   [Node.js](https://nodejs.org/en/download/) (v18+)
*   [Python](https://www.python.org/downloads/) (v3.10+)
*   A DialKey (or other LLM provider) API key.

## 2. Setup Steps

### Step 1: Clone & Configure (3 minutes)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd multi-agent-orchestrator

# 2. Create your local environment file from the example
cp .env.example .env

# 3. Edit the .env file with your credentials
nano .env
```

### Step 2: Start Services (5 minutes)

```bash
# Start all services using Docker Compose
docker-compose up -d

# Verify that all containers are healthy
docker-compose ps
```

### Step 3: Verify Installation (2 minutes)

```bash
# Test the backend health endpoint
curl http://localhost:8080/health
# Expected output: {"status":"healthy"}

# Open the frontend in your browser
open http://localhost:3000
```

## 3. Create Your First Flow (3 minutes)

1.  Drag the "Researcher" agent onto the canvas.
2.  Drag the "Analyst" agent onto the canvas.
3.  Connect the two agents by dragging a line from the output of the Researcher to the input of the Analyst.
4.  Click the "Save" button, name your flow "My First Flow", and save it.
5.  Click the "Run" button to start the execution.

## 4. Next Steps

*   Read `docs/planning/ImplemenationPlan.md` for a deep dive into the system architecture.
*   Explore `docs/api/API_EXAMPLES.md` to learn how to interact with the API programmatically.
*   Consult `docs/development/DEVELOPMENT_WORKFLOW.md` for daily development practices.