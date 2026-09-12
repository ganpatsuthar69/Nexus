import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import { Layout } from './components/layout/Layout';
import { Overview } from './pages/Overview';
import { WorldState } from './pages/WorldState';
import { AgentActivity } from './pages/AgentActivity';
import { Decisions } from './pages/Decisions';
import { Plans } from './pages/Plans';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Overview />} />
              <Route path="world-state" element={<WorldState />} />
              <Route path="activity" element={<AgentActivity />} />
              <Route path="decisions" element={<Decisions />} />
              <Route path="plans" element={<Plans />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
