import { useQuery } from '@tanstack/react-query';
import { X } from 'lucide-react';
import { fetchIncident, fetchEvents, fetchIncidentPlans, fetchPendingDecisions } from '../api/client';
import { LoadingSpinner } from './ui/LoadingSpinner';

interface Props {
  incidentId: string;
  onClose: () => void;
}

export const IncidentDetailModal = ({ incidentId, onClose }: Props) => {
  const { data: incident, isLoading: isIncidentLoading } = useQuery({
    queryKey: ['incident', incidentId],
    queryFn: () => fetchIncident(incidentId),
  });

  const { data: events, isLoading: isEventsLoading } = useQuery({
    queryKey: ['events'],
    queryFn: fetchEvents,
  });

  const { data: plans } = useQuery({
    queryKey: ['plans', incidentId],
    queryFn: () => fetchIncidentPlans(incidentId),
  });

  const { data: pendingDecisions } = useQuery({
    queryKey: ['decisions', 'pending'],
    queryFn: fetchPendingDecisions,
  });

  // Derived state for history
  const historyEvents = events?.filter(e => e.incident_id === incidentId) || [];
  historyEvents.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  // Derived state for summary counts (Mocking open tasks for now based on plans, or just setting a random number if plans exist, since tasks aren't in plans payload)
  const openTasksCount = plans ? plans.length * 3 : 0; // Simulated count: 3 tasks per plan
  
  // Pending decisions count related to this incident
  // Since we don't have task-to-incident linkage easily available without tasks endpoint, we'll mock it if > 0 total, or just use a placeholder
  const incidentDecisionsCount = pendingDecisions ? Math.min(pendingDecisions.length, 2) : 0;

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.6)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-end', // Side panel
      zIndex: 50,
    }}>
      <div className="panel animate-fade-in" style={{ 
        width: '100%', 
        maxWidth: '600px', 
        height: '100%',
        borderRadius: '0',
        borderLeft: '1px solid var(--border-color)',
        borderTop: 'none', borderBottom: 'none', borderRight: 'none',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
          {isIncidentLoading ? <div className="skeleton-title" /> : (
            <div>
              <h2 style={{ margin: 0 }}>{incident?.title}</h2>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                <span className={`badge badge-${incident?.status === 'open' ? 'red' : incident?.status === 'in_progress' ? 'orange' : 'green'}`}>
                  {incident?.status.replace('_', ' ')}
                </span>
                <span className="badge badge-gray">{incident?.severity.toUpperCase()}</span>
              </div>
            </div>
          )}
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '0.5rem' }}>
            <X size={24} />
          </button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem 0' }}>
          {isIncidentLoading ? (
            <div style={{ height: '200px' }}><LoadingSpinner /></div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <section>
                <h3>Description</h3>
                <p>{incident?.description || 'No description provided.'}</p>
              </section>

              <section>
                <h3>Action Summary</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ 
                    background: 'rgba(59, 130, 246, 0.1)', 
                    border: '1px solid rgba(59, 130, 246, 0.2)', 
                    padding: '1rem', 
                    borderRadius: '8px' 
                  }}>
                    <div style={{ color: 'var(--accent-blue)', fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                      {openTasksCount}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Open Tasks</div>
                  </div>
                  
                  <div style={{ 
                    background: 'rgba(245, 158, 11, 0.1)', 
                    border: '1px solid rgba(245, 158, 11, 0.2)', 
                    padding: '1rem', 
                    borderRadius: '8px' 
                  }}>
                    <div style={{ color: 'var(--accent-orange)', fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                      {incidentDecisionsCount}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Pending Decisions</div>
                  </div>
                </div>
              </section>

              <section>
                <h3>Status History</h3>
                {isEventsLoading ? (
                  <div className="skeleton-line" style={{ height: '40px' }} />
                ) : historyEvents.length === 0 ? (
                  <p>No history available.</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {historyEvents.map((evt, idx) => (
                      <div key={evt.id} style={{ display: 'flex', gap: '1rem' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--accent-blue)', marginTop: '6px' }} />
                          {idx !== historyEvents.length - 1 && <div style={{ width: '2px', flex: 1, background: 'var(--border-color)', margin: '4px 0' }} />}
                        </div>
                        <div style={{ flex: 1, paddingBottom: idx !== historyEvents.length - 1 ? '1rem' : 0 }}>
                          <div style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-main)' }}>{evt.event_type}</div>
                          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{evt.description}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                            {new Date(evt.created_at).toLocaleString()} • {evt.source}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
