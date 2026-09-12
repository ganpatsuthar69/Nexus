import { useState, useEffect } from 'react';
import { Wifi, WifiOff, RefreshCw } from 'lucide-react';

type ConnectionStatus = 'connected' | 'reconnecting' | 'disconnected';

export const TopBar = () => {
  // Simulated connection status for Phase 4 live stream
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connected');
  const currentIncident = 'INC-2026-OMEGA'; // Mock data for now

  // Optional: Simulate reconnecting logic
  useEffect(() => {
    if (connectionStatus === 'reconnecting') {
      const timer = setTimeout(() => {
        setConnectionStatus('connected');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [connectionStatus]);

  return (
    <header style={{
      height: '64px',
      background: 'rgba(15, 23, 42, 0.8)',
      borderBottom: '1px solid rgba(255,255,255,0.1)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 1.5rem',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-primary)' }}>
          Active Incident: <span style={{ color: 'var(--accent-red)' }}>{currentIncident}</span>
        </h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem',
          padding: '0.375rem 0.75rem',
          borderRadius: '9999px',
          background: 'rgba(0,0,0,0.2)',
          border: '1px solid rgba(255,255,255,0.1)',
          fontSize: '0.875rem'
        }}>
          {connectionStatus === 'connected' && (
            <>
              <Wifi size={16} style={{ color: 'var(--accent-green)' }} />
              <span style={{ color: 'var(--accent-green)' }}>Live Stream Active</span>
            </>
          )}
          {connectionStatus === 'reconnecting' && (
            <>
              <RefreshCw size={16} className="spin" style={{ color: 'var(--accent-orange)' }} />
              <span style={{ color: 'var(--accent-orange)' }}>Reconnecting...</span>
            </>
          )}
          {connectionStatus === 'disconnected' && (
            <>
              <WifiOff size={16} style={{ color: 'var(--accent-red)' }} />
              <span style={{ color: 'var(--accent-red)' }}>Stream Disconnected</span>
            </>
          )}
        </div>
        
        <button 
          onClick={() => setConnectionStatus(prev => prev === 'connected' ? 'reconnecting' : 'connected')}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            fontSize: '0.75rem',
            textDecoration: 'underline'
          }}
        >
          Toggle Status
        </button>
      </div>
      <style>
        {`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </header>
  );
};
