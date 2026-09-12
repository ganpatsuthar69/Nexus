import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ShieldCheck, Inbox, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';
import { fetchPendingDecisions, resolveDecision } from '../api/client';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { Decision } from '../types';

export const Decisions = () => {
  const queryClient = useQueryClient();
  const [selectedOptions, setSelectedOptions] = useState<Record<string, string>>({});
  const [lastResolved, setLastResolved] = useState<{ id: string, message: string } | null>(null);

  const { data: decisions, isLoading, isError, error } = useQuery({
    queryKey: ['decisions', 'pending'],
    queryFn: fetchPendingDecisions,
    refetchInterval: 15000,
  });

  const resolveMutation = useMutation({
    mutationFn: ({ id, option }: { id: string; option: string }) => resolveDecision(id, option),
    onMutate: async ({ id }) => {
      // Cancel any outgoing refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({ queryKey: ['decisions', 'pending'] });

      // Snapshot previous value
      const previousDecisions = queryClient.getQueryData<Decision[]>(['decisions', 'pending']);

      // Optimistically update
      if (previousDecisions) {
        queryClient.setQueryData<Decision[]>(
          ['decisions', 'pending'], 
          old => old?.filter(d => d.id !== id)
        );
      }

      setLastResolved({ id, message: `Decision submitted successfully.` });

      // Auto-hide success message after 5 seconds
      setTimeout(() => {
        setLastResolved(prev => prev?.id === id ? null : prev);
      }, 5000);

      return { previousDecisions };
    },
    onError: (err, _, context) => {
      // Rollback
      queryClient.setQueryData(['decisions', 'pending'], context?.previousDecisions);
      setLastResolved(null);
      console.error("Failed to submit decision:", err);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['decisions', 'pending'] });
    },
  });

  const handleSelectOption = (id: string, option: string) => {
    setSelectedOptions(prev => ({ ...prev, [id]: option }));
  };

  const handleSubmit = (id: string) => {
    const option = selectedOptions[id];
    if (!option) return;
    resolveMutation.mutate({ id, option });
  };

  if (isLoading) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Human Decision Center</h1>
        </div>
        <LoadingSpinner size={48} />
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Human Decision Center</h1>
        </div>
        <div className="panel" style={{ textAlign: 'center', padding: '3rem', color: 'var(--accent-red)' }}>
          <AlertCircle size={48} style={{ margin: '0 auto 1rem' }} />
          <h3>Failed to load decisions</h3>
          <p>{error instanceof Error ? error.message : 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  const isEmpty = !decisions || decisions.length === 0;

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0 }}>
          <ShieldCheck size={28} style={{ color: 'var(--accent-blue)' }} /> 
          Pending Decisions
        </h1>
      </div>

      {lastResolved && (
        <div className="animate-fade-in" style={{ 
          padding: '1rem', 
          background: 'rgba(16, 185, 129, 0.1)', 
          border: '1px solid rgba(16, 185, 129, 0.4)',
          borderRadius: '8px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-green)' }}>
            <CheckCircle2 size={20} />
            {lastResolved.message}
          </div>
          <Link to="/activity" className="btn btn-outline" style={{ fontSize: '0.875rem', padding: '0.25rem 0.75rem' }}>
            View Agent Activity
          </Link>
        </div>
      )}

      {isEmpty ? (
        <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.7 }}>
          <Inbox size={64} style={{ marginBottom: '1rem', color: 'var(--text-muted)' }} />
          <h2>You're all caught up!</h2>
          <p>Nothing needs your input right now. The autonomous agents are handling active incidents.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1.5rem', alignItems: 'start' }}>
          {decisions.map(decision => (
            <div key={decision.id} className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <HelpCircle size={24} style={{ color: 'var(--accent-orange)', marginTop: '2px', flexShrink: 0 }} />
                <div>
                  <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem' }}>{decision.question}</h3>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    <strong>Reasoning / Context: </strong>
                    {decision.reason || 'Agent encountered an ambiguous situation or requires human authorization.'}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem' }}>
                {decision.options.map(option => (
                  <label 
                    key={option}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      padding: '0.75rem',
                      background: selectedOptions[decision.id] === option ? 'rgba(59, 130, 246, 0.1)' : 'rgba(0,0,0,0.2)',
                      border: selectedOptions[decision.id] === option ? '1px solid var(--accent-blue)' : '1px solid var(--border-color)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    <input 
                      type="radio" 
                      name={`decision-${decision.id}`}
                      value={option}
                      checked={selectedOptions[decision.id] === option}
                      onChange={() => handleSelectOption(decision.id, option)}
                      style={{ margin: 0, cursor: 'pointer' }}
                    />
                    <span style={{ fontSize: '0.95rem' }}>{option}</span>
                  </label>
                ))}
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <button 
                  className="btn btn-primary"
                  disabled={!selectedOptions[decision.id] || resolveMutation.isPending}
                  onClick={() => handleSubmit(decision.id)}
                >
                  Submit Decision
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
