import { useEffect, useState } from 'react';
import { fetchHealth, type HealthResponse } from '../api';
import './StatusCard.css';

export function StatusCard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const poll = async () => {
    try {
      const data = await fetchHealth();
      setHealth(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    poll();
    const interval = setInterval(poll, 10_000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const statusClass = health?.status === 'ok' ? 'status-ok' : 'status-error';

  return (
    <div className="status-card">
      <div className="status-card__header">
        <div className={`status-indicator ${statusClass}`} />
        <h2>System Health</h2>
      </div>
      {loading && <p className="status-card__loading">Connecting…</p>}
      {error && (
        <div className="status-card__error">
          <span className="error-icon">⚠</span>
          <div>
            <p className="error-label">Backend Unreachable</p>
            <p className="error-detail">{error}</p>
          </div>
        </div>
      )}
      {health && (
        <div className="status-card__details">
          <div className="detail-row">
            <span className="detail-label">Status</span>
            <span className={`detail-value badge ${statusClass}`}>
              {health.status.toUpperCase()}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Service</span>
            <span className="detail-value">{health.service}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Version</span>
            <span className="detail-value mono">{health.version}</span>
          </div>
        </div>
      )}
      <button className="status-card__refresh" onClick={poll} disabled={loading}>
        ↻ Refresh
      </button>
    </div>
  );
}
