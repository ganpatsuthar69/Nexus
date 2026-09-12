import { NavLink } from 'react-router-dom';
import { 
  Activity, 
  Globe2, 
  TerminalSquare, 
  GitPullRequest, 
  ListTodo,
  LayoutDashboard
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/world-state', label: 'World State', icon: Globe2 },
  { path: '/activity', label: 'Agent Activity', icon: Activity },
  { path: '/decisions', label: 'Decisions', icon: GitPullRequest },
  { path: '/plans', label: 'Plans', icon: ListTodo },
];

export const Sidebar = () => {
  return (
    <aside style={{
      width: '250px',
      background: 'rgba(15, 23, 42, 0.95)',
      borderRight: '1px solid rgba(255,255,255,0.1)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backdropFilter: 'blur(12px)',
    }}>
      <div style={{
        padding: '1.5rem',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
      }}>
        <h1 style={{ 
          margin: 0, 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.75rem',
          fontSize: '1.25rem',
          color: 'var(--text-primary)'
        }}>
          <TerminalSquare size={24} style={{ color: 'var(--accent-blue)' }} />
          <span><span style={{ color: 'var(--accent-blue)', fontWeight: 'bold' }}>NEXUS</span> Base</span>
        </h1>
      </div>

      <nav style={{ padding: '1rem 0', flex: 1 }}>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {navItems.map((item) => (
            <li key={item.path} style={{ padding: '0 1rem' }}>
              <NavLink
                to={item.path}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem 1rem',
                  borderRadius: '0.5rem',
                  textDecoration: 'none',
                  color: isActive ? 'white' : 'var(--text-secondary)',
                  background: isActive ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                  borderLeft: isActive ? '3px solid var(--accent-blue)' : '3px solid transparent',
                  transition: 'all 0.2s ease',
                  fontWeight: isActive ? 500 : 400
                })}
              >
                <item.icon size={20} />
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      <div style={{ padding: '1.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'center', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
        v0.1.0-alpha
      </div>
    </aside>
  );
};
