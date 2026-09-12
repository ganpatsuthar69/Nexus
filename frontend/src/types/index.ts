export interface Incident {
  id: string;
  title: string;
  description: string;
  status: string;
  severity: string;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  population: number;
  priority: number;
  current_status: string;
}

export interface Resource {
  id: string;
  name: string;
  resource_type: string;
  status: string;
  capacity: number;
  location_id: string;
  metadata_: any;
  updated_at: string;
}

export interface Team {
  id: string;
  name: string;
  team_type: string;
  status: string;
  location_id: string;
  capacity: number;
  metadata_: any;
}

export interface Decision {
  id: string;
  task_id: string;
  question: string;
  options: string[];
  selected_option?: string;
  decided_by?: string;
  reason?: string;
  created_at: string;
}

export interface Plan {
  id: string;
  incident_id: string;
  goal: string;
  status: string;
  version: number;
  reason: string;
  created_at: string;
  approved_by?: string;
  tasks?: Task[];
}

export interface Task {
  id: string;
  plan_id: string;
  title: string;
  description: string;
  status: string;
  priority: number;
  assigned_resource_id?: string;
  assigned_team_id?: string;
  requires_human: boolean;
  created_at: string;
  completed_at?: string;
}

export interface AgentActivity {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  details: any;
  created_at: string;
}

export interface WorldState {
  incidents: Incident[];
  locations: Location[];
  resources: Resource[];
  teams: Team[];
}
