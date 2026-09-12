/**
 * Shared TypeScript types for the NEXUS frontend.
 */

/** Health-check response from the backend. */
export interface HealthStatus {
  status: 'ok' | 'degraded' | 'down';
  service: string;
  version: string;
}

/** Placeholder — future incident model. */
export interface Incident {
  id: string;
  title: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved';
  created_at: string;
}

/** Placeholder — future agent action model. */
export interface AgentAction {
  id: string;
  agent: string;
  action: string;
  timestamp: string;
  result: 'success' | 'failure' | 'pending';
}
