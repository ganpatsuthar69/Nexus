import { useEffect, useState } from 'react';
import { fetchWorldState } from '../api/client';
import type { WorldState as WorldStateType } from '../types';

export default function WorldState() {
  const [state, setState] = useState<WorldStateType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchWorldState();
        setState(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !state) {
    return (
      <div className="panel col-span-8">
        <h3>Live World State</h3>
        <div className="skeleton skeleton-title"></div>
        <div className="skeleton skeleton-line" style={{ height: '100px' }}></div>
      </div>
    );
  }

  if (error) {
    return <div className="panel col-span-8"><h3>Live World State</h3><p>Error: {error}</p></div>;
  }

  return (
    <div className="panel col-span-8 animate-fade-in">
      <h3>Live World State</h3>
      
      <div className="dashboard-grid" style={{ padding: 0, gap: '1rem', marginTop: '1rem' }}>
        <div className="panel col-span-4" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)' }}>
          <h4>Locations ({state?.locations.length})</h4>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '0.5rem' }}>
            {state?.locations.map(loc => (
              <li key={loc.id} className="flex justify-between text-sm mb-2 pb-2" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span>{loc.name}</span>
                <span className={loc.current_status === 'critical' ? 'badge badge-red' : 'badge badge-blue'}>
                  {loc.current_status}
                </span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="panel col-span-4" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)' }}>
          <h4>Resources ({state?.resources.length})</h4>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '0.5rem' }}>
            {state?.resources.map(res => (
              <li key={res.id} className="flex justify-between text-sm mb-2 pb-2" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span>{res.name}</span>
                <span className={res.status === 'available' ? 'badge badge-green' : 'badge badge-orange'}>
                  {res.status}
                </span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="panel col-span-4" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)' }}>
          <h4>Teams ({state?.teams.length})</h4>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '0.5rem' }}>
            {state?.teams.map(team => (
              <li key={team.id} className="flex justify-between text-sm mb-2 pb-2" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span>{team.name}</span>
                <span className={team.status === 'available' ? 'badge badge-green' : 'badge badge-orange'}>
                  {team.status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
