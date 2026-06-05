import { test, expect, request } from '@playwright/test';
import { getUser1Token } from './helpers/auth';

const API_BASE = 'http://localhost:8000/api/v1';

// Helper: create a flow via API and return its ID
async function createFlow(name: string, description?: string): Promise<string> {
  const token = await getUser1Token();
  const ctx = await request.newContext({
    extraHTTPHeaders: { Authorization: `Bearer ${token}` },
  });
  const res = await ctx.post(`${API_BASE}/flows`, {
    headers: { 'Content-Type': 'application/json' },
    data: { name, description: description ?? null, flow_config: { nodes: [], edges: [] } },
  });
  const body = await res.json() as { id: string };
  await ctx.dispose();
  return body.id;
}

// Helper: delete a flow via API
async function deleteFlow(id: string): Promise<void> {
  const token = await getUser1Token();
  const ctx = await request.newContext({
    extraHTTPHeaders: { Authorization: `Bearer ${token}` },
  });
  await ctx.delete(`${API_BASE}/flows/${id}`);
  await ctx.dispose();
}

test.describe('Flow Library', () => {
  test('shows Flow Library heading', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Flow Library' })).toBeVisible();
  });

  test('shows navigation links', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('link', { name: 'Flows' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Analytics' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'HITL Queue' })).toBeVisible();
  });

  test('shows existing flows from API', async ({ page }) => {
    const flowId = await createFlow('E2E Test Flow List', 'flow list test');

    await page.goto('/');
    await expect(page.getByText('E2E Test Flow List')).toBeVisible();

    await deleteFlow(flowId);
  });

  test('clicking flow card navigates to canvas', async ({ page }) => {
    const flowId = await createFlow('E2E Nav Test Flow');

    await page.goto('/');
    await page.getByText('E2E Nav Test Flow').click();

    await expect(page).toHaveURL(`/flows/${flowId}`);
    await expect(page.getByText('E2E Nav Test Flow')).toBeVisible();

    await deleteFlow(flowId);
  });
});

test.describe('Canvas Page', () => {
  let flowId: string;

  test.beforeEach(async () => {
    flowId = await createFlow('E2E Canvas Flow', 'canvas test');
  });

  test.afterEach(async () => {
    await deleteFlow(flowId);
  });

  test('shows flow name in toolbar', async ({ page }) => {
    await page.goto(`/flows/${flowId}`);
    await expect(page.getByText('E2E Canvas Flow')).toBeVisible();
  });

  test('shows Save and Run Flow buttons', async ({ page }) => {
    await page.goto(`/flows/${flowId}`);
    await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Run Flow' })).toBeVisible();
  });

  test('shows execution log panel', async ({ page }) => {
    await page.goto(`/flows/${flowId}`);
    await expect(page.getByText('Execution Log')).toBeVisible();
    await expect(page.getByText('No execution yet')).toBeVisible();
  });

  test('shows agent role palette', async ({ page }) => {
    await page.goto(`/flows/${flowId}`);
    await expect(page.getByText('Agent Roles')).toBeVisible();
    await expect(page.getByText('researcher')).toBeVisible();
    await expect(page.getByText('analyst')).toBeVisible();
  });

  test('shows ReactFlow canvas', async ({ page }) => {
    await page.goto(`/flows/${flowId}`);
    // ReactFlow mini map is present
    await expect(page.locator('.react-flow')).toBeVisible();
  });
});
