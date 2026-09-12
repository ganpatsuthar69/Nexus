import { useEffect, useState } from 'react';
import { fetchIncidents } from '../api/client';
import type { Incident } from '../types';

export default function IncidentOverview() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchIncidents();
        setIncidents(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 5000); // refresh every 5s
    return () => clearInterval(interval);
  }, []);

  if (loading && incidents.length === 0) {
    return (
      <div className="panel col-span-4 flex flex-col gap-4">
        <h3>Incident Overview</h3>
        <div className="skeleton skeleton-title"></div>
        <div className="skeleton skeleton-line"></div>
        <div className="skeleton skeleton-line"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel col-span-4">
        <h3>Incident Overview</h3>
        <p className="text-red-500 mt-2">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="panel col-span-4 flex flex-col gap-4 animate-fade-in">
      <h3>Incident Overview</h3>
      {incidents.length === 0 ? (
        <p>No active incidents.</p>
      ) : (
        incidents.map((inc) => (
          <div key={inc.id} className="panel" style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)' }}>
            <div className="flex justify-between items-center mb-2">
              <h4 style={{ margin: 0 }}>{inc.title}</h4>
              <span className={`badge ${inc.severity === 'high' || inc.severity === 'critical' ? 'badge-red' : 'badge-orange'}`}>
                {inc.severity}
              </span>
            </div>
            <p className="text-sm mb-2">{inc.description}</p>
            <div className="flex justify-between items-center text-xs">
              <span className={`badge ${inc.status === 'active' ? 'badge-blue' : 'badge-green'}`}>
                {inc.status}
              </span>
              <span className="text-muted">Updated: {new Date(inc.updated_at).toLocaleTimeString()}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
