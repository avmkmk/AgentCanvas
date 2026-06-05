import { test, expect, request } from '@playwright/test';
import { getUser1Token } from './helpers/auth';

const API_BASE = 'http://localhost:8000';

test.describe('Backend API Health', () => {
  test('health endpoint returns ok', async () => {
    const ctx = await request.newContext();
    const res = await ctx.get(`${API_BASE}/health`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.status).toBe('ok');
    await ctx.dispose();
  });

  test('models endpoint returns model list', async () => {
    const ctx = await request.newContext();
    const res = await ctx.get(`${API_BASE}/models`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(Array.isArray(body.models)).toBeTruthy();
    expect(body.models.length).toBeGreaterThan(0);
    await ctx.dispose();
  });

  test('flows list requires auth', async () => {
    // Create a fresh context with NO headers to test auth requirement
    const ctx = await request.newContext({ extraHTTPHeaders: {} });
    const res = await ctx.get(`${API_BASE}/api/v1/flows`);
    expect(res.status()).toBe(401);
    await ctx.dispose();
  });

  test('flows list with auth returns paginated response', async () => {
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get(`${API_BASE}/api/v1/flows`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body).toHaveProperty('items');
    expect(body).toHaveProperty('total');
    expect(body).toHaveProperty('page');
    expect(body).toHaveProperty('page_size');
    await ctx.dispose();
  });

  test('create flow returns snake_case fields', async () => {
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.post(`${API_BASE}/api/v1/flows`, {
      headers: { 'Content-Type': 'application/json' },
      data: { name: 'API Test Flow', flow_config: { nodes: [], edges: [] } },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty('id');
    expect(body).toHaveProperty('flow_config');
    expect(body).toHaveProperty('is_active');
    expect(body.is_active).toBe(true);

    // Cleanup
    await ctx.delete(`${API_BASE}/api/v1/flows/${body.id}`);
    await ctx.dispose();
  });

  test('HITL pending returns empty list initially', async () => {
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get(`${API_BASE}/api/v1/hitl/pending`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
    await ctx.dispose();
  });

  test('analytics agents returns wrapped response', async () => {
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get(`${API_BASE}/api/v1/analytics/agents`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body).toHaveProperty('items');
    expect(body).toHaveProperty('total');
    await ctx.dispose();
  });
});
