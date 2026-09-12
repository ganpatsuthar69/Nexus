import type { Incident, WorldState, Decision, Plan } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'nexus_dev_secret';

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
};

export const fetchIncidents = async (): Promise<Incident[]> => {
  const res = await fetch(`${API_URL}/api/incidents`, { headers });
  if (!res.ok) throw new Error('Failed to fetch incidents');
  return res.json();
};

export const fetchWorldState = async (): Promise<WorldState> => {
  const res = await fetch(`${API_URL}/api/world-state`, { headers });
  if (!res.ok) throw new Error('Failed to fetch world state');
  return res.json();
};

export const fetchPendingDecisions = async (): Promise<Decision[]> => {
  const res = await fetch(`${API_URL}/api/decisions/pending`, { headers });
  if (!res.ok) throw new Error('Failed to fetch decisions');
  return res.json();
};

export const resolveDecision = async (id: string, option: string): Promise<any> => {
  const res = await fetch(`${API_URL}/api/decisions/${id}/resolve`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ selected_option: option, reason: 'Human operator decision' }),
  });
  if (!res.ok) throw new Error('Failed to resolve decision');
  return res.json();
};

export const fetchIncidentPlans = async (incidentId: string): Promise<Plan[]> => {
  const res = await fetch(`${API_URL}/api/incidents/${incidentId}/plans`, { headers });
  if (!res.ok) throw new Error('Failed to fetch plans');
  return res.json();
};
