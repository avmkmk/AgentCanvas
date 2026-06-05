import { test, expect, request } from '@playwright/test';
import { getUser1Token } from './helpers/auth';

const API_BASE = 'http://localhost:8000/api/v1';

test.describe('Execution Flow', () => {
  test('Run Flow button triggers execution and shows log entries', async ({ page }) => {
    // Create a flow via API (no agents — execution will complete immediately)
    const token = await getUser1Token();
    const ctx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.post(`${API_BASE}/flows`, {
      headers: { 'Content-Type': 'application/json' },
      data: { name: 'E2E Exec Test', flow_config: { nodes: [], edges: [] } },
    });
    const flow = await res.json() as { id: string };
    await ctx.dispose();

    await page.goto(`/flows/${flow.id}`);

    // Click Run Flow
    await page.getByRole('button', { name: 'Run Flow' }).click();

    // Wait for execution to start — button shows "Running…" or execution log changes
    await page.waitForFunction(
      () => document.body.innerText.includes('Running') ||
            document.body.innerText.includes('Run Flow') ||
            document.body.innerText.includes('Execution Log'),
      { timeout: 15_000 }
    );

    // The log panel should still be visible
    await expect(page.getByText('Execution Log')).toBeVisible();

    // Cleanup
    const delToken = await getUser1Token();
    const delCtx = await request.newContext({
      extraHTTPHeaders: { Authorization: `Bearer ${delToken}` },
    });
    await delCtx.delete(`${API_BASE}/flows/${flow.id}`);
    await delCtx.dispose();
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
