import { useEffect, useState, useRef } from 'react';
import type { AgentActivity as AgentActivityType } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'nexus_dev_secret';

export default function AgentActivity() {
  const [activities, setActivities] = useState<AgentActivityType[]>([]);
  const [error, setError] = useState('');
  const [connected, setConnected] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Note: EventSource doesn't support headers, so we pass api_key in query
    const sse = new EventSource(`${API_URL}/api/agent/activity?api_key=${API_KEY}`);

    sse.onopen = () => {
      setConnected(true);
      setError('');
    };

    sse.addEventListener('agent_activity', (e) => {
      try {
        const data: AgentActivityType = JSON.parse(e.data);
        setActivities(prev => {
          // Avoid duplicates if the stream sends the same ID
          if (prev.find(a => a.id === data.id)) return prev;
          return [...prev, data].slice(-20); // Keep last 20
        });
      } catch (err) {
        console.error("Failed to parse SSE event", err);
      }
    });

    sse.onerror = () => {
      setError('Connection to Agent Stream lost. Reconnecting...');
      setConnected(false);
    };

    return () => sse.close();
  }, []);

  useEffect(() => {
    // Auto scroll to bottom
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activities]);

  return (
    <div className="panel col-span-12 flex flex-col" style={{ height: '400px' }}>
      <div className="flex justify-between items-center mb-4">
        <h3>Agent Activity Feed</h3>
        <span className={`badge ${connected ? 'badge-green' : 'badge-red'}`}>
          {connected ? '● LIVE STREAM' : '○ RECONNECTING'}
        </span>
      </div>
      
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
      
      <div className="flex-1 overflow-y-auto pr-2" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {activities.length === 0 ? (
          <p className="text-sm">Waiting for agent activity...</p>
        ) : (
          activities.map((act) => (
            <div key={act.id} className="animate-fade-in" style={{ 
              background: 'rgba(0,0,0,0.2)', 
              borderLeft: `4px solid ${act.action.includes('failed') || act.action.includes('degraded') ? 'var(--accent-red)' : 'var(--accent-blue)'}`,
              padding: '0.75rem', 
              borderRadius: '0 8px 8px 0' 
            }}>
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium" style={{ color: 'var(--text-main)' }}>{act.actor}</span>
                <span className="text-xs text-muted">{new Date(act.created_at).toLocaleTimeString()}</span>
              </div>
              <p className="text-sm text-white">
                <strong style={{ color: 'var(--accent-orange)' }}>{act.action}</strong> on <em>{act.entity_type}</em>
              </p>
              {act.details && Object.keys(act.details).length > 0 && (
                <pre className="text-xs mt-2" style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '4px', overflowX: 'auto' }}>
                  {JSON.stringify(act.details, null, 2)}
                </pre>
              )}
            </div>
          ))
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
