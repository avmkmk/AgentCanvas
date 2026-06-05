import { APIRequestContext, request } from '@playwright/test';

const KEYCLOAK_URL = 'http://localhost:8080';
const REALM = 'flowind';

export async function getToken(username: string, password: string): Promise<string> {
  const ctx: APIRequestContext = await request.newContext();
  const res = await ctx.post(
    `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      data: `grant_type=password&client_id=flowind-frontend&username=${username}&password=${password}`,
    }
  );
  const body = await res.json() as { access_token: string };
  await ctx.dispose();
  return body.access_token;
}

export async function getUser1Token(): Promise<string> {
  return getToken('user1', 'password');
}

export async function getUser2Token(): Promise<string> {
  return getToken('user2', 'password');
}
