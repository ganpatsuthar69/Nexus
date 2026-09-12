import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ListTodo, CheckCircle2, Clock, XCircle, User, History
} from 'lucide-react';
import { fetchIncidents, fetchIncidentPlans } from '../api/client';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const Plans = () => {
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('');
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);

  const { data: incidents, isLoading: isIncidentsLoading } = useQuery({
    queryKey: ['incidents'],
    queryFn: fetchIncidents,
  });

  const activeIncidentId = selectedIncidentId || (incidents && incidents.length > 0 ? incidents[0].id : '');

  const { data: plans, isLoading: isPlansLoading } = useQuery({
    queryKey: ['plans', activeIncidentId],
    queryFn: () => fetchIncidentPlans(activeIncidentId),
    enabled: !!activeIncidentId,
    refetchInterval: 10000,
  });

  // Sort plans by version descending
  const sortedPlans = useMemo(() => {
    if (!plans) return [];
    return [...plans].sort((a, b) => b.version - a.version);
  }, [plans]);

  // Determine which plan version to display
  const currentPlan = useMemo(() => {
    if (!sortedPlans.length) return null;
    if (selectedVersion !== null) {
      return sortedPlans.find(p => p.version === selectedVersion) || sortedPlans[0];
    }
    return sortedPlans[0]; // Latest
  }, [sortedPlans, selectedVersion]);

  // If incident changes, reset version selection to latest
  useMemo(() => {
    if (activeIncidentId) {
      setSelectedVersion(null);
    }
  }, [activeIncidentId]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 size={16} className="text-green" style={{ color: 'var(--accent-green)' }} />;
      case 'in_progress': return <Clock size={16} className="text-orange" style={{ color: 'var(--accent-orange)' }} />;
      case 'failed': return <XCircle size={16} className="text-red" style={{ color: 'var(--accent-red)' }} />;
      case 'pending': 
      default: return <Clock size={16} className="text-gray" style={{ color: 'var(--text-muted)' }} />;
    }
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'var(--accent-red)';
    if (priority >= 5) return 'var(--accent-orange)';
    return 'var(--text-main)';
  };

  if (isIncidentsLoading) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Plan Viewer</h1>
        </div>
        <LoadingSpinner size={48} />
      </div>
    );
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0 }}>
          <ListTodo size={28} style={{ color: 'var(--accent-blue)' }} /> 
          Plan Viewer
        </h1>

        <select
          value={activeIncidentId}
          onChange={(e) => setSelectedIncidentId(e.target.value)}
          style={{
            padding: '0.5rem 1rem',
            background: 'rgba(0,0,0,0.2)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            color: 'white',
            width: '250px'
          }}
        >
          {incidents?.length === 0 && <option value="">No active incidents</option>}
          {incidents?.map(inc => (
            <option key={inc.id} value={inc.id}>{inc.title}</option>
          ))}
        </select>
      </div>

      {!activeIncidentId ? (
        <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.7 }}>
          <ListTodo size={64} style={{ marginBottom: '1rem', color: 'var(--text-muted)' }} />
          <h2>No Incident Selected</h2>
          <p>Select an active incident from the dropdown to view its plan history.</p>
        </div>
      ) : isPlansLoading ? (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <LoadingSpinner size={48} />
        </div>
      ) : sortedPlans.length === 0 ? (
        <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.7 }}>
          <ListTodo size={64} style={{ marginBottom: '1rem', color: 'var(--text-muted)' }} />
          <h2>No Plans Available</h2>
          <p>The agent hasn't generated any plans for this incident yet.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
          
          {/* Main Plan Area */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <span className="badge badge-blue">v{currentPlan?.version}</span>
                    <span className={`badge badge-${currentPlan?.status === 'active' ? 'green' : currentPlan?.status === 'superseded' ? 'gray' : 'orange'}`}>
                      {currentPlan?.status.toUpperCase()}
                    </span>
                  </div>
                  <h2 style={{ margin: 0 }}>{currentPlan?.goal}</h2>
                </div>
              </div>
              
              {currentPlan?.reason && (
                <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', borderLeft: '3px solid var(--accent-blue)', fontSize: '0.875rem' }}>
                  <strong>Reasoning: </strong>{currentPlan.reason}
                </div>
              )}
            </div>

            <div>
              <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                Tasks ({currentPlan?.tasks?.length || 0})
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {!currentPlan?.tasks || currentPlan.tasks.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)' }}>No tasks defined in this plan version.</p>
                ) : (
                  currentPlan.tasks.map(task => (
                    <div 
                      key={task.id} 
                      className="panel"
                      style={{ 
                        padding: '1rem',
                        borderLeft: `4px solid ${
                          task.status === 'completed' ? 'var(--accent-green)' : 
                          task.status === 'failed' ? 'var(--accent-red)' : 
                          task.status === 'in_progress' ? 'var(--accent-orange)' : 'var(--text-muted)'
                        }` 
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {getStatusIcon(task.status)}
                          <strong style={{ fontSize: '1rem' }}>{task.title}</strong>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {task.requires_human && (
                            <span className="badge badge-orange" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                              <User size={12} /> Requires Human
                            </span>
                          )}
                          <span className="badge badge-gray" style={{ color: getPriorityColor(task.priority) }}>
                            P{task.priority}
                          </span>
                        </div>
                      </div>
                      
                      {task.description && (
                        <p style={{ fontSize: '0.875rem', marginBottom: '0.75rem', marginTop: '0.25rem' }}>{task.description}</p>
                      )}
                      
                      <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {task.assigned_team_id && <span>Team: {task.assigned_team_id}</span>}
                        {task.assigned_resource_id && <span>Resource: {task.assigned_resource_id}</span>}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Version History Sidebar */}
          <div className="panel" style={{ width: '300px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
              <History size={18} /> Version History
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {sortedPlans.map(p => (
                <button
                  key={p.id}
                  onClick={() => setSelectedVersion(p.version)}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    padding: '0.75rem',
                    background: (selectedVersion === p.version) || (selectedVersion === null && p.version === sortedPlans[0].version) ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    border: (selectedVersion === p.version) || (selectedVersion === null && p.version === sortedPlans[0].version) ? '1px solid var(--accent-blue)' : '1px solid var(--border-color)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    color: 'white',
                    textAlign: 'left'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 500 }}>Version {p.version}</span>
                    <span style={{ fontSize: '0.75rem', color: p.status === 'active' ? 'var(--accent-green)' : 'var(--text-muted)' }}>
                      {p.status}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {new Date(p.created_at).toLocaleString()}
                  </div>
                </button>
              ))}
            </div>
          </div>

        </div>
      )}
    </div>
  );
};
