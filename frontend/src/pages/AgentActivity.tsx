import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Activity, CheckCircle2, XCircle, Clock, ListTree, Users, ArrowDown, Wifi, WifiOff, RefreshCw, TerminalSquare
} from 'lucide-react';

interface AgentEvent {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  details: any;
  created_at: string;
}

const MAX_ENTRIES = 200;

export const AgentActivity = () => {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [isAutoScrollPaused, setIsAutoScrollPaused] = useState(false);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  
  const feedRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<number | undefined>(undefined);
  const reconnectAttemptsRef = useRef(0);

  const connectSSE = useCallback(() => {
    setConnectionState('connecting');
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const eventSource = new EventSource(`${API_URL}/api/agent/activity`);

    eventSource.onopen = () => {
      setConnectionState('connected');
      reconnectAttemptsRef.current = 0;
    };

    eventSource.addEventListener('agent_activity', (e) => {
      try {
        const data: AgentEvent = JSON.parse(e.data);
        setEvents(prev => {
          // Prepend new event to keep reverse-chronological order
          const newEvents = [data, ...prev.filter(evt => evt.id !== data.id)];
          return newEvents.slice(0, MAX_ENTRIES);
        });
      } catch (err) {
        console.error('Error parsing agent activity event:', err);
      }
    });

    eventSource.onerror = () => {
      setConnectionState('disconnected');
      eventSource.close();
      
      // Exponential backoff reconnect
      const timeout = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
      reconnectAttemptsRef.current += 1;
      
      reconnectTimeoutRef.current = setTimeout(() => {
        connectSSE();
      }, timeout);
    };

    return eventSource;
  }, []);

  useEffect(() => {
    const es = connectSSE();
    return () => {
      es.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, [connectSSE]);

  const handleScroll = () => {
    if (!feedRef.current) return;
    // We are scrolling a reverse-chronological list (newest at top).
    // If scrollTop > 0, we have scrolled down to see older items.
    const { scrollTop } = feedRef.current;
    if (scrollTop > 50) {
      setIsAutoScrollPaused(true);
    } else {
      setIsAutoScrollPaused(false);
    }
  };

  const jumpToNewest = () => {
    if (feedRef.current) {
      feedRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
    setIsAutoScrollPaused(false);
  };

  const toggleExpand = (id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const getEventIcon = (action: string, entity_type: string) => {
    if (action.includes('created') && entity_type === 'plan') return <ListTree size={18} style={{ color: 'var(--accent-blue)' }} />;
    if (action.includes('executed') || action.includes('tool')) return <TerminalSquare size={18} style={{ color: 'var(--accent-orange)' }} />;
    if (action.includes('verification') && action.includes('passed')) return <CheckCircle2 size={18} style={{ color: 'var(--accent-green)' }} />;
    if (action.includes('failed') || action.includes('error')) return <XCircle size={18} style={{ color: 'var(--accent-red)' }} />;
    if (action.includes('decision') || action.includes('human')) return <Users size={18} style={{ color: 'var(--accent-blue)' }} />;
    return <Activity size={18} style={{ color: 'var(--text-muted)' }} />;
  };

  const formatPayload = (details: any) => {
    if (!details) return null;
    return (
      <pre style={{
        marginTop: '0.5rem',
        padding: '0.75rem',
        background: 'rgba(0,0,0,0.3)',
        borderRadius: '6px',
        fontSize: '0.75rem',
        overflowX: 'auto',
        color: 'var(--text-muted)'
      }}>
        {JSON.stringify(details, null, 2)}
      </pre>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.5rem', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>Agent Activity Feed</h1>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
          {connectionState === 'connected' && (
            <span className="badge badge-green" style={{ gap: '0.25rem' }}>
              <Wifi size={14} /> Live Stream Connected
            </span>
          )}
          {connectionState === 'connecting' && (
            <span className="badge badge-orange" style={{ gap: '0.25rem' }}>
              <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> Reconnecting...
            </span>
          )}
          {connectionState === 'disconnected' && (
            <span className="badge badge-red" style={{ gap: '0.25rem' }}>
              <WifiOff size={14} /> Disconnected
            </span>
          )}
        </div>
      </div>

      <div className="panel" style={{ flex: 1, padding: 0, display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
        
        {isAutoScrollPaused && (
          <div style={{
            position: 'absolute', top: '1rem', left: '50%', transform: 'translateX(-50%)', zIndex: 10
          }}>
            <button 
              onClick={jumpToNewest}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderRadius: '9999px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
            >
              <ArrowDown size={16} /> Jump to latest
            </button>
          </div>
        )}

        <div 
          ref={feedRef}
          onScroll={handleScroll}
          style={{ 
            flex: 1, 
            overflowY: 'auto', 
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column', // reverse chronological means new items are appended at top of list
            gap: '1rem' 
          }}
        >
          {events.length === 0 && connectionState !== 'connecting' ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '3rem' }}>
              <Activity size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
              <p>No agent activity recorded yet.</p>
            </div>
          ) : (
            events.map((evt) => (
              <div 
                key={evt.id} 
                style={{ 
                  background: 'rgba(255,255,255,0.02)', 
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'flex',
                  gap: '1rem',
                  transition: 'background-color 0.2s',
                  cursor: 'pointer'
                }}
                onClick={() => toggleExpand(evt.id)}
              >
                <div style={{ marginTop: '0.25rem' }}>
                  {getEventIcon(evt.action, evt.entity_type)}
                </div>
                
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                    <div style={{ fontWeight: 500 }}>
                      <span style={{ color: 'var(--text-muted)', marginRight: '0.5rem' }}>{evt.actor}</span>
                      {evt.action.replace(/_/g, ' ')} {evt.entity_type}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <Clock size={12} /> {new Date(evt.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                  
                  {expandedIds.has(evt.id) && formatPayload(evt.details)}
                </div>
              </div>
            ))
          )}

          {events.length === MAX_ENTRIES && (
            <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              Showing last {MAX_ENTRIES} entries. Older history requires a manual query.
            </div>
          )}
        </div>
      </div>
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};
