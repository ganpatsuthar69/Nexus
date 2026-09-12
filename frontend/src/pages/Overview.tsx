import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, AlertCircle, Calendar, ShieldAlert } from 'lucide-react';
import { fetchIncidents, createIncident } from '../api/client';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { IncidentDetailModal } from '../components/IncidentDetailModal';
import { CreateIncidentModal } from '../components/CreateIncidentModal';

export const Overview = () => {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);

  // Poll every 10s
  const { data: incidents, isLoading, isError, error } = useQuery({
    queryKey: ['incidents'],
    queryFn: fetchIncidents,
    refetchInterval: 10000,
  });

  const createMutation = useMutation({
    mutationFn: createIncident,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      setIsCreateModalOpen(false);
    },
  });

  if (isLoading) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Incident Overview</h1>
        </div>
        <LoadingSpinner size={48} />
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Incident Overview</h1>
        </div>
        <div className="panel" style={{ textAlign: 'center', padding: '3rem', color: 'var(--accent-red)' }}>
          <AlertCircle size={48} style={{ margin: '0 auto 1rem' }} />
          <h3>Failed to load incidents</h3>
          <p>{error instanceof Error ? error.message : 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  const isEmpty = !incidents || incidents.length === 0;

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Incident Overview</h1>
        <button className="btn btn-primary flex items-center gap-2" onClick={() => setIsCreateModalOpen(true)}>
          <Plus size={16} /> New Incident
        </button>
      </div>

      {isEmpty ? (
        <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.7 }}>
          <ShieldAlert size={64} style={{ marginBottom: '1rem', color: 'var(--text-muted)' }} />
          <h2>No Active Incidents</h2>
          <p>The system is currently monitoring for new anomalies.</p>
          <button className="btn btn-outline mt-4" onClick={() => setIsCreateModalOpen(true)}>
            Create one manually
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {incidents.map((incident) => (
            <div 
              key={incident.id} 
              className="panel" 
              style={{ cursor: 'pointer', transition: 'all 0.2s' }}
              onClick={() => setSelectedIncidentId(incident.id)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.125rem' }}>{incident.title}</h3>
                <span className={`badge badge-${incident.status === 'open' ? 'red' : incident.status === 'in_progress' ? 'orange' : 'green'}`}>
                  {incident.status.replace('_', ' ')}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <ShieldAlert size={14} className={incident.severity === 'critical' ? 'text-red' : ''} />
                  {incident.severity.toUpperCase()}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Calendar size={14} />
                  {new Date(incident.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {isCreateModalOpen && (
        <CreateIncidentModal 
          onClose={() => setIsCreateModalOpen(false)} 
          onSubmit={(data) => createMutation.mutate(data)}
          isSubmitting={createMutation.isPending}
        />
      )}

      {selectedIncidentId && (
        <IncidentDetailModal 
          incidentId={selectedIncidentId} 
          onClose={() => setSelectedIncidentId(null)} 
        />
      )}
    </div>
  );
};
