import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Stocks from './pages/Stocks';
import News from './pages/News';
import Pipeline from './pages/Pipeline';
import { api } from './api';
import './styles/global.css';

export default function App() {
  const [page,       setPage]       = useState('Dashboard');
  const [apiOnline,  setApiOnline]  = useState(false);
  const [triggering, setTriggering] = useState(false);

  useEffect(() => {
    api.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false));
    const id = setInterval(() => {
      api.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false));
    }, 15000);
    return () => clearInterval(id);
  }, []);

  async function handleTrigger() {
    setTriggering(true);
    try { await api.triggerPipeline(); } catch (e) { console.error(e); }
    finally { setTriggering(false); }
  }

  const pages = { Dashboard, Stocks, News, Pipeline };
  const PageComponent = pages[page] || Dashboard;

  return (
    <div>
      <Navbar
        apiOnline={apiOnline}
        onTrigger={handleTrigger}
        triggering={triggering}
        activePage={page}
        setPage={setPage}
      />
      <PageComponent />
      <footer style={{ textAlign: 'center', padding: '2rem', color: 'var(--dim)', fontSize: 10,
        borderTop: '1px solid var(--border)', marginTop: '2rem' }}>
        Built by{' '}
        <a href="https://www.linkedin.com/in/msunil2002/" target="_blank" rel="noreferrer"
          style={{ color: 'var(--accent)' }}>Sunil KM</a>
        {' '}· MS Applied CS @ SEMO ·{' '}
        <a href="https://github.com/sunil5092" target="_blank" rel="noreferrer"
          style={{ color: 'var(--muted)' }}>GitHub</a>
      </footer>
    </div>
  );
}
