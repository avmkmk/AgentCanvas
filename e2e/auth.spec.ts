import { test, expect, request } from '@playwright/test';
import { getUser1Token, getUser2Token } from './helpers/auth';

const API = 'http://localhost:8000/api/v1';

test.describe('Authentication and User Isolation', () => {
  test('unauthenticated request returns 401', async () => {
    const ctx = await request.newContext({ extraHTTPHeaders: {} });
    const res = await ctx.get(`${API}/flows`);
    expect(res.status()).toBe(401);
    await ctx.dispose();
  });

  test('user1 token gives access to flows endpoint', async () => {
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get(`${API}/flows`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body).toHaveProperty('items');
    expect(body).toHaveProperty('total');
    await ctx.dispose();
  });

  test('user1 flows are not visible to user2', async () => {
    const token1 = await getUser1Token();
    const token2 = await getUser2Token();

    // Create flow as user1
    const ctx1 = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token1}` },
    });
    const createRes = await ctx1.post(`${API}/flows`, {
      data: { name: 'User1 Private Flow', flow_config: { nodes: [], edges: [] } },
    });
    expect(createRes.status()).toBe(201);
    const flow = await createRes.json() as { id: string };

    // User2 tries to access it — should get 403
    const ctx2 = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token2}` },
    });
    const getRes = await ctx2.get(`${API}/flows/${flow.id}`);
    expect(getRes.status()).toBe(403);

    // Cleanup
    await ctx1.delete(`${API}/flows/${flow.id}`);
    await ctx1.dispose();
    await ctx2.dispose();
  });

  test('user1 only sees their own flows in list', async () => {
    const token1 = await getUser1Token();
    const token2 = await getUser2Token();

    const ctx2 = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token2}` },
    });
    const res2 = await ctx2.post(`${API}/flows`, {
      data: { name: 'User2 Exclusive Flow', flow_config: { nodes: [], edges: [] } },
    });
    const flow2 = await res2.json() as { id: string };

    const ctx1 = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token1}` },
    });
    const listRes = await ctx1.get(`${API}/flows`);
    const list = await listRes.json() as { items: Array<{ id: string }> };
    const ids = list.items.map((f) => f.id);
    expect(ids).not.toContain(flow2.id);

    await ctx2.delete(`${API}/flows/${flow2.id}`);
    await ctx1.dispose();
    await ctx2.dispose();
  });

  test('analytics endpoint requires auth', async () => {
    const ctx = await request.newContext({ extraHTTPHeaders: {} });
    const res = await ctx.get('http://localhost:8001/api/v1/analytics/agents');
    expect(res.status()).toBe(401);
    await ctx.dispose();
  });

  test('analytics endpoint returns data with valid token', async () => {
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get('http://localhost:8001/api/v1/analytics/agents');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body).toHaveProperty('items');
    await ctx.dispose();
  });
});
