import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, MapPin, Package, Users, AlertTriangle } from 'lucide-react';
import { fetchWorldState } from '../api/client';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { WorldState as WorldStateType } from '../types';

export const WorldState = () => {
  const [search, setSearch] = useState('');
  const [changedIds, setChangedIds] = useState<Set<string>>(new Set());
  const prevDataRef = useRef<WorldStateType | undefined>(undefined);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['world-state'],
    queryFn: fetchWorldState,
    refetchInterval: 10000, // 10s polling
  });

  useEffect(() => {
    if (data && prevDataRef.current) {
      const newChanged = new Set<string>();
      
      const checkChanges = (current: any[], prev: any[], type: string) => {
        current.forEach(item => {
          const prevItem = prev.find(p => p.id === item.id);
          // Assuming 'status' is the field for resources/teams, and 'current_status' for locations
          const statusField = type === 'location' ? 'current_status' : 'status';
          if (prevItem && prevItem[statusField] !== item[statusField]) {
            newChanged.add(item.id);
          }
        });
      };

      checkChanges(data.locations, prevDataRef.current.locations, 'location');
      checkChanges(data.resources, prevDataRef.current.resources, 'resource');
      checkChanges(data.teams, prevDataRef.current.teams, 'team');

      if (newChanged.size > 0) {
        setChangedIds(newChanged);
        // Clear highlights after 3 seconds
        const timer = setTimeout(() => {
          setChangedIds(new Set());
        }, 3000);
        return () => clearTimeout(timer);
      }
    }
    prevDataRef.current = data;
  }, [data]);

  if (isLoading) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>World State</h1>
        </div>
        <LoadingSpinner size={48} />
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>World State</h1>
        </div>
        <div className="panel" style={{ textAlign: 'center', padding: '3rem', color: 'var(--accent-red)' }}>
          <AlertTriangle size={48} style={{ margin: '0 auto 1rem' }} />
          <h3>Failed to load world state</h3>
          <p>{error instanceof Error ? error.message : 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  const searchLower = search.toLowerCase();
  const locations = data?.locations.filter(l => l.name.toLowerCase().includes(searchLower)) || [];
  const resources = data?.resources.filter(r => r.name.toLowerCase().includes(searchLower)) || [];
  const teams = data?.teams.filter(t => t.name.toLowerCase().includes(searchLower)) || [];

  const getHighlightStyle = (id: string) => ({
    transition: 'background-color 1s ease',
    backgroundColor: changedIds.has(id) ? 'rgba(245, 158, 11, 0.3)' : 'transparent',
  });

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'var(--accent-red)';
    if (priority >= 5) return 'var(--accent-orange)';
    return 'var(--accent-green)';
  };

  const getLocationName = (id: string) => {
    return data?.locations.find(l => l.id === id)?.name || 'Unknown Location';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>World State</h1>
        <div style={{ position: 'relative', width: '300px' }}>
          <Search size={18} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem 1rem 0.5rem 2.25rem',
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              color: 'white'
            }}
          />
        </div>
      </div>

      <section>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem', marginBottom: '1rem' }}>
          <MapPin size={20} style={{ color: 'var(--accent-blue)' }} /> Locations
        </h2>
        {locations.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No locations found.</p>
        ) : (
          <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(0,0,0,0.2)' }}>
                  <th style={{ padding: '1rem' }}>Name</th>
                  <th style={{ padding: '1rem' }}>Status</th>
                  <th style={{ padding: '1rem' }}>Priority</th>
                </tr>
              </thead>
              <tbody>
                {locations.map(loc => (
                  <tr key={loc.id} style={{ borderBottom: '1px solid var(--border-color)', ...getHighlightStyle(loc.id) }}>
                    <td style={{ padding: '1rem', fontWeight: 500 }}>{loc.name}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className="badge badge-gray">{loc.current_status.replace('_', ' ')}</span>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: getPriorityColor(loc.priority) }} />
                        {loc.priority}/10
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem', marginBottom: '1rem' }}>
          <Package size={20} style={{ color: 'var(--accent-blue)' }} /> Resources
        </h2>
        {resources.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No resources found.</p>
        ) : (
          <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(0,0,0,0.2)' }}>
                  <th style={{ padding: '1rem' }}>Name</th>
                  <th style={{ padding: '1rem' }}>Type</th>
                  <th style={{ padding: '1rem' }}>Status</th>
                  <th style={{ padding: '1rem' }}>Capacity</th>
                  <th style={{ padding: '1rem' }}>Location</th>
                </tr>
              </thead>
              <tbody>
                {resources.map(res => (
                  <tr key={res.id} style={{ borderBottom: '1px solid var(--border-color)', ...getHighlightStyle(res.id) }}>
                    <td style={{ padding: '1rem', fontWeight: 500 }}>{res.name}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{res.resource_type}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className="badge badge-gray">{res.status.replace('_', ' ')}</span>
                    </td>
                    <td style={{ padding: '1rem' }}>{res.capacity}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{getLocationName(res.location_id)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem', marginBottom: '1rem' }}>
          <Users size={20} style={{ color: 'var(--accent-blue)' }} /> Teams
        </h2>
        {teams.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No teams found.</p>
        ) : (
          <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(0,0,0,0.2)' }}>
                  <th style={{ padding: '1rem' }}>Name</th>
                  <th style={{ padding: '1rem' }}>Type</th>
                  <th style={{ padding: '1rem' }}>Status</th>
                  <th style={{ padding: '1rem' }}>Capacity</th>
                </tr>
              </thead>
              <tbody>
                {teams.map(team => (
                  <tr key={team.id} style={{ borderBottom: '1px solid var(--border-color)', ...getHighlightStyle(team.id) }}>
                    <td style={{ padding: '1rem', fontWeight: 500 }}>{team.name}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{team.team_type}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className="badge badge-gray">{team.status.replace('_', ' ')}</span>
                    </td>
                    <td style={{ padding: '1rem' }}>{team.capacity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
