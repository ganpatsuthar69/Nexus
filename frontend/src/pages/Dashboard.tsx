import { StatusCard } from '../components';
import './Dashboard.css';

export function Dashboard() {
  return (
    <main className="dashboard">
      {/* Background gradient orbs */}
      <div className="bg-orb bg-orb--1" aria-hidden="true" />
      <div className="bg-orb bg-orb--2" aria-hidden="true" />
      <div className="bg-orb bg-orb--3" aria-hidden="true" />

      <header className="dashboard__header">
        <div className="logo">
          <span className="logo__icon">◆</span>
          <h1 className="logo__text">NEXUS</h1>
        </div>
        <p className="dashboard__tagline">
          Autonomous Real-World Coordination Agent
        </p>
      </header>

      <section className="dashboard__grid">
        <StatusCard />

        {/* Placeholder cards for future panels */}
        <div className="placeholder-card">
          <h3>Incident Feed</h3>
          <p>Live event stream will appear here.</p>
        </div>

        <div className="placeholder-card">
          <h3>Agent Activity</h3>
          <p>Supervisor → Sub-agent decisions in real time.</p>
        </div>

        <div className="placeholder-card">
          <h3>World State</h3>
          <p>Resources, assignments, and locations map.</p>
        </div>
      </section>

      <footer className="dashboard__footer">
        <span>NEXUS v0.1.0</span>
        <span className="separator">·</span>
        <span>Agents for Humans Hackathon</span>
      </footer>
    </main>
  );
}
