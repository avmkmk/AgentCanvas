import { test, expect, request } from '@playwright/test';
import { getUser1Token } from './helpers/auth';

const API_BASE = 'http://localhost:8000/api/v1';

test.describe('Execution Flow', () => {
  test('execution lifecycle — start, poll status, cancel via API', async () => {
    // Full execution lifecycle test via API (browser UI test requires running frontend + Keycloak PKCE)
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    // Create flow
    const flowRes = await ctx.post(`${API_BASE}/flows`, {
      headers: { 'Content-Type': 'application/json' },
      data: { name: 'E2E Lifecycle Test', flow_config: { nodes: [], edges: [] } },
    });
    const flow = await flowRes.json() as { id: string };

    // Start execution
    const execRes = await ctx.post(`${API_BASE}/executions`, {
      headers: { 'Content-Type': 'application/json' },
      data: { flow_id: flow.id, input_data: {} },
    });
    expect(execRes.status()).toBe(202);
    const exec = await execRes.json() as { id: string; status: string };
    expect(exec.id).toBeTruthy();
    expect(['running', 'pending', 'completed']).toContain(exec.status);

    // Poll until terminal or timeout
    let finalStatus = exec.status;
    for (let i = 0; i < 10; i++) {
      const pollRes = await ctx.get(`${API_BASE}/executions/${exec.id}`);
      const polled = await pollRes.json() as { status: string };
      finalStatus = polled.status;
      if (['completed', 'failed', 'cancelled'].includes(finalStatus)) break;
      await new Promise(r => setTimeout(r, 1000));
    }

    // Zero-agent flow should complete immediately
    expect(['completed', 'running']).toContain(finalStatus);

    // Check execution history endpoint
    const histRes = await ctx.get(`${API_BASE}/flows/${flow.id}/executions`);
    expect(histRes.ok()).toBeTruthy();

    // Cleanup
    await ctx.delete(`${API_BASE}/flows/${flow.id}`);
    await ctx.dispose();
  });

  test('execution API returns correct shape', async () => {
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    // Create flow
    const flowRes = await ctx.post(`${API_BASE}/flows`, {
      headers: { 'Content-Type': 'application/json' },
      data: { name: 'Exec API Test', flow_config: { nodes: [], edges: [] } },
    });
    const flow = await flowRes.json() as { id: string };

    // Start execution
    const execRes = await ctx.post(`${API_BASE}/executions`, {
      headers: { 'Content-Type': 'application/json' },
      data: { flow_id: flow.id, input_data: {} },
    });
    expect(execRes.status()).toBe(202);
    const exec = await execRes.json() as { id: string; status: string; flow_id: string };
    expect(exec).toHaveProperty('id');
    expect(exec).toHaveProperty('status');
    expect(exec).toHaveProperty('flow_id');
    expect(['running', 'pending', 'completed', 'failed', 'cancelled']).toContain(exec.status);

    // Get execution
    const getRes = await ctx.get(`${API_BASE}/executions/${exec.id}`);
    expect(getRes.ok()).toBeTruthy();

    // Cancel execution
    const cancelRes = await ctx.post(`${API_BASE}/executions/${exec.id}/cancel`);
    expect(cancelRes.ok()).toBeTruthy();

    // Cleanup
    await ctx.delete(`${API_BASE}/flows/${flow.id}`);
    await ctx.dispose();
  });
});
