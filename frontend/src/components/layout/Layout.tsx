import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

export const Layout = () => {
  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      width: '100vw',
      overflow: 'hidden',
      backgroundColor: 'var(--bg-dark)',
      color: 'var(--text-primary)'
    }}>
      <Sidebar />
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <TopBar />
        <main style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1.5rem',
          position: 'relative'
        }}>
          {/* This renders the matched child route component */}
          <Outlet />
        </main>
      </div>
    </div>
  );
};
