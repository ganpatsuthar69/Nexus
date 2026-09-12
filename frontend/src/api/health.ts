/**
 * NEXUS API client — thin wrapper around fetch for backend calls.
 */

const API_BASE = '/api';

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}
