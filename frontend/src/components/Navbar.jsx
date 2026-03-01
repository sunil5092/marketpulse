import React from 'react';

export default function Navbar({ apiOnline, onTrigger, triggering, activePage, setPage }) {
  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'rgba(8,12,16,0.93)', backdropFilter: 'blur(14px)',
      borderBottom: '1px solid var(--border)',
      padding: '0.8rem 1.8rem',
      display: 'flex', alignItems: 'center', gap: '1.5rem',
    }}>
      <span style={{ fontFamily: 'var(--font-display)', fontWeight: 800,
        fontSize: '1.1rem', color: 'var(--accent)', letterSpacing: '-0.02em', marginRight: '0.5rem' }}>
        MarketPulse 📈
      </span>

      {/* Page tabs */}
      {['Dashboard', 'Stocks', 'News', 'Pipeline'].map(p => (
        <button key={p} onClick={() => setPage(p)}
          style={{ background: 'transparent', border: 'none',
            color: activePage === p ? 'var(--text)' : 'var(--muted)',
            fontSize: 12, padding: '0.3rem 0',
            borderBottom: activePage === p ? '2px solid var(--accent)' : '2px solid transparent',
          }}>
          {p}
        </button>
      ))}

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* API status */}
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: 5,
          background: apiOnline ? 'rgba(126,231,135,0.1)' : 'rgba(247,129,102,0.1)',
          border: `1px solid ${apiOnline ? 'rgba(126,231,135,0.3)' : 'rgba(247,129,102,0.3)'}`,
          color: apiOnline ? 'var(--green)' : 'var(--red)',
          padding: '0.2rem 0.7rem', borderRadius: 999, fontSize: 10,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%',
            background: apiOnline ? 'var(--green)' : 'var(--red)',
            display: 'block', animation: apiOnline ? 'pulse 2s infinite' : 'none' }}/>
          {apiOnline ? 'API Online' : 'API Offline'}
        </span>

        {/* Run pipeline button */}
        <button onClick={onTrigger} disabled={triggering}
          style={{ background: triggering ? 'var(--border)' : 'var(--accent)',
            color: 'var(--bg)', border: 'none', borderRadius: 4,
            padding: '0.45rem 1rem', fontSize: 11, fontWeight: 700,
            cursor: triggering ? 'not-allowed' : 'pointer' }}>
          {triggering ? 'Running...' : '▶ Run Pipeline'}
        </button>
      </div>

      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}`}</style>
    </nav>
  );
}
