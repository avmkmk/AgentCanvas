# API Examples Guide

This document provides practical examples for each API endpoint, using both `curl` and Python with the `requests` library.

## 1. Authentication

All requests to the API must include your API key in the `X-API-Key` header.

```bash
-H "X-API-Key: your_api_key_here"
```

---

## 2. Flow Management

### Create a Flow

**Endpoint:** `POST /api/v1/flows`

**`curl`:**
```bash
curl -X POST http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "name": "My New Flow",
    "description": "This is a test flow.",
    "flow_config": {
      "nodes": [],
      "edges": []
    }
  }'
```

**Python:**
```python
import requests

API_URL = "http://localhost:8080/api/v1"
API_KEY = "your_api_key"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

flow_data = {
    "name": "My New Flow",
    "description": "This is a test flow.",
    "flow_config": {
        "nodes": [],
        "edges": []
    }
}

response = requests.post(f"{API_URL}/flows", headers=headers, json=flow_data)
print(response.json())
```

### List All Flows

**Endpoint:** `GET /api/v1/flows`

**`curl`:**
```bash
curl -X GET http://localhost:8080/api/v1/flows \
  -H "X-API-Key: your_api_key"
```

**Python:**
```python
response = requests.get(f"{API_URL}/flows", headers=headers)
print(response.json())
```

---

## 3. Flow Execution

### Start Execution

**Endpoint:** `POST /api/v1/executions/start`

**`curl`:**
```bash
curl -X POST http://localhost:8080/api/v1/executions/start \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "flow_id": "your_flow_id_here",
    "initial_input": "Start the process."
  }'
```

**Python:**
```python
execution_data = {
    "flow_id": "your_flow_id_here",
    "initial_input": "Start the process."
}

response = requests.post(f"{API_URL}/executions/start", headers=headers, json=execution_data)
print(response.json())
```

---

## 4. HITL (Human-in-the-Loop) Operations

### Get Pending Reviews

**Endpoint:** `GET /api/v1/hitl/queue`

**`curl`:**
```bash
curl -X GET http://localhost:8080/api/v1/hitl/queue \
  -H "X-API-Key: your_api_key"
```

### Approve a Review

**Endpoint:** `POST /api/v1/hitl/{review_id}/approve`

**`curl`:**
```bash
curl -X POST http://localhost:8080/api/v1/hitl/your_review_id/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "comments": "This looks correct. Proceed."
  }'
```

---
