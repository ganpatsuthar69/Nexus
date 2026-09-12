import { useEffect, useState } from 'react';
import { fetchPendingDecisions, resolveDecision } from '../api/client';
import type { Decision } from '../types';

export default function DecisionCenter() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const load = async () => {
    try {
      const data = await fetchPendingDecisions();
      setDecisions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleResolve = async (id: string, option: string) => {
    setResolvingId(id);
    try {
      await resolveDecision(id, option);
      await load();
    } catch (err) {
      console.error("Failed to resolve", err);
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div className="panel col-span-6 animate-fade-in" style={{ border: '1px solid rgba(239, 68, 68, 0.3)' }}>
      <div className="flex justify-between items-center mb-4">
        <h3>Human Decision Center</h3>
        <span className="badge badge-red">{decisions.length} PENDING</span>
      </div>

      {loading && decisions.length === 0 ? (
        <div className="skeleton skeleton-line"></div>
      ) : decisions.length === 0 ? (
        <p className="text-sm">No decisions currently require human intervention.</p>
      ) : (
        <div className="flex flex-col gap-4">
          {decisions.map(d => (
            <div key={d.id} style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '1rem', borderRadius: '8px' }}>
              <p className="text-white font-medium mb-3">{d.question}</p>
              <div className="flex gap-2">
                {d.options.map(opt => (
                  <button 
                    key={opt}
                    onClick={() => handleResolve(d.id, opt)}
                    disabled={resolvingId === d.id}
                    className="btn btn-outline"
                    style={{ flex: 1 }}
                  >
                    {resolvingId === d.id ? 'Processing...' : opt.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
