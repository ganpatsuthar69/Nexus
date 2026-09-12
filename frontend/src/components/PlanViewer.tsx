import { useEffect, useState } from 'react';
import { fetchIncidents, fetchIncidentPlans } from '../api/client';
import type { Incident, Plan } from '../types';

export default function PlanViewer() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('');
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchIncidents().then(data => {
      setIncidents(data);
      if (data.length > 0 && !selectedIncidentId) {
        setSelectedIncidentId(data[0].id);
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedIncidentId) return;
    
    const load = async () => {
      setLoading(true);
      try {
        const data = await fetchIncidentPlans(selectedIncidentId);
        setPlans(data.sort((a, b) => b.version - a.version)); // Newest first
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [selectedIncidentId]);

  return (
    <div className="panel col-span-6 animate-fade-in">
      <div className="flex justify-between items-center mb-4">
        <h3>Plan Viewer</h3>
        {incidents.length > 0 && (
          <select 
            value={selectedIncidentId} 
            onChange={(e) => setSelectedIncidentId(e.target.value)}
            style={{ background: 'rgba(255,255,255,0.1)', color: 'white', border: '1px solid var(--border-color)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}
          >
            {incidents.map(inc => (
              <option key={inc.id} value={inc.id}>{inc.title}</option>
            ))}
          </select>
        )}
      </div>

      {loading && plans.length === 0 ? (
        <div className="skeleton skeleton-line"></div>
      ) : plans.length === 0 ? (
        <p className="text-sm">No plans available for this incident.</p>
      ) : (
        <div className="flex flex-col gap-4 max-h-[400px] overflow-y-auto">
          {plans.map(p => (
            <div key={p.id} style={{ 
              border: '1px solid rgba(255,255,255,0.1)', 
              borderRadius: '8px', 
              padding: '1rem',
              opacity: p.status === 'abandoned' ? 0.6 : 1
            }}>
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-white">v{p.version}: {p.goal}</span>
                <span className={`badge ${p.status === 'abandoned' ? 'badge-gray' : p.status === 'draft' ? 'badge-orange' : 'badge-green'}`}>
                  {p.status}
                </span>
              </div>
              {p.reason && <p className="text-xs mb-3 italic">"{p.reason}"</p>}
              
              <div className="flex flex-col gap-2 pl-4" style={{ borderLeft: '2px solid rgba(255,255,255,0.1)' }}>
                {p.tasks?.length ? p.tasks.map(t => (
                  <div key={t.id} className="flex justify-between text-sm">
                    <span style={{ color: t.status === 'completed' ? 'var(--accent-green)' : 'var(--text-main)' }}>
                      {t.status === 'completed' ? '✓ ' : '○ '} {t.title}
                    </span>
                    <span className="text-xs text-muted">{t.status.toUpperCase()}</span>
                  </div>
                )) : <p className="text-xs text-muted">No tasks defined yet.</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
