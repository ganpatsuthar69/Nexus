
import IncidentOverview from './components/IncidentOverview';
import WorldState from './components/WorldState';
import AgentActivity from './components/AgentActivity';
import DecisionCenter from './components/DecisionCenter';
import PlanViewer from './components/PlanViewer';
import './index.css';

function App() {
  return (
    <div>
      <header style={{ padding: '1.5rem', background: 'rgba(15, 23, 42, 0.8)', borderBottom: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(12px)' }}>
        <h1 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: 'var(--accent-blue)' }}>NEXUS</span> Dashboard
          <span className="badge badge-blue" style={{ fontSize: '0.6rem', marginLeft: 'auto' }}>AUTONOMOUS AGENT ACTIVE</span>
        </h1>
      </header>
      
      <main className="dashboard-grid">
        <IncidentOverview />
        <WorldState />
        
        <DecisionCenter />
        <PlanViewer />
        
        <AgentActivity />
      </main>
    </div>
  );
}

export default App;
