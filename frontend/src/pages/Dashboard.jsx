import React, { useEffect, useState } from 'react';
import { api } from '../api';

const card = {
  background: 'var(--surface)', border: '1px solid var(--border)',
  borderRadius: 8, padding: '1.25rem',
};
const lbl = {
  fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase',
  color: 'var(--accent)', marginBottom: '0.6rem',
};

function StockCard({ s }) {
  const pos = s.pct_change >= 0;
  return (
    <div style={{ ...card, borderLeft: `3px solid ${pos ? 'var(--green)' : 'var(--red)'}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem' }}>{s.ticker}</p>
          <p style={{ fontSize: '1.4rem', fontWeight: 600, marginTop: 2 }}>${s.latest_close.toFixed(2)}</p>
        </div>
        <span style={{
          background: pos ? 'rgba(126,231,135,0.12)' : 'rgba(247,129,102,0.12)',
          border: `1px solid ${pos ? 'rgba(126,231,135,0.3)' : 'rgba(247,129,102,0.3)'}`,
          color: pos ? 'var(--green)' : 'var(--red)',
          padding: '0.25rem 0.6rem', borderRadius: 3, fontSize: 12, fontWeight: 700,
        }}>
          {pos ? '▲' : '▼'} {Math.abs(s.pct_change).toFixed(2)}%
        </span>
      </div>
      <div style={{ marginTop: '0.9rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
        {[
          ['High', `$${s.day_high.toFixed(2)}`],
          ['Low',  `$${s.day_low.toFixed(2)}`],
          ['7d High', `$${s.week_high.toFixed(2)}`],
          ['7d Low',  `$${s.week_low.toFixed(2)}`],
        ].map(([k, v]) => (
          <div key={k}>
            <span style={{ color: 'var(--dim)', fontSize: 10 }}>{k} </span>
            <span style={{ fontSize: 11 }}>{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function NewsBadge({ sentiment }) {
  const map = {
    positive: { c: 'var(--green)', b: 'rgba(126,231,135,0.1)' },
    negative: { c: 'var(--red)',   b: 'rgba(247,129,102,0.1)' },
    neutral:  { c: 'var(--muted)', b: 'rgba(139,148,158,0.1)' },
  };
  const s = map[sentiment] || map.neutral;
  return (
    <span style={{ background: s.b, color: s.c, padding: '0.1rem 0.5rem',
      borderRadius: 3, fontSize: 10, fontWeight: 600 }}>
      {sentiment}
    </span>
  );
}

export default function Dashboard() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  useEffect(() => {
    api.dashboard()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p style={{ color: 'var(--muted)', padding: '2rem' }}>Loading dashboard...</p>;
  if (error)   return (
    <div style={{ padding: '2rem' }}>
      <p style={{ color: 'var(--red)', marginBottom: '0.5rem' }}>⚠ Could not load dashboard: {error}</p>
      <p style={{ color: 'var(--muted)', fontSize: 12 }}>
        Make sure the backend is running and you've triggered the pipeline at least once.
      </p>
    </div>
  );

  const run = data.last_pipeline_run;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1100, margin: '0 auto' }}>

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          ['Total Data Points', data.total_data_points.toLocaleString(), 'var(--accent)'],
          ['Stocks Tracked',    data.watchlist.length, 'var(--green)'],
          ['Last Run Status',   run ? run.status : 'No runs yet', run?.status === 'success' ? 'var(--green)' : 'var(--red)'],
        ].map(([label, value, color]) => (
          <div key={label} style={card}>
            <p style={lbl}>{label}</p>
            <p style={{ fontSize: '1.6rem', fontWeight: 700, color }}>{value}</p>
          </div>
        ))}
      </div>

      {/* Stock cards */}
      {data.watchlist.length > 0 ? (
        <>
          <p style={{ ...lbl, marginBottom: '0.9rem' }}>Watchlist</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(220px,1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            {data.watchlist.map(s => <StockCard key={s.ticker} s={s} />)}
          </div>
        </>
      ) : (
        <div style={{ ...card, marginBottom: '1.5rem', textAlign: 'center', padding: '2rem' }}>
          <p style={{ color: 'var(--muted)' }}>No stock data yet. Click <strong style={{ color: 'var(--accent)' }}>▶ Run Pipeline</strong> to fetch data.</p>
        </div>
      )}

      {/* Recent news */}
      <div style={card}>
        <p style={lbl}>Recent News ({data.recent_news.length})</p>
        {data.recent_news.length === 0 ? (
          <p style={{ color: 'var(--muted)' }}>No news yet — run the pipeline to fetch articles.</p>
        ) : (
          data.recent_news.map((n, i) => (
            <div key={n.id} style={{
              padding: '0.8rem 0',
              borderBottom: i < data.recent_news.length - 1 ? '1px solid var(--border)' : 'none',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                <a href={n.url} target="_blank" rel="noreferrer"
                  style={{ color: 'var(--text)', fontSize: 13, lineHeight: 1.5, flex: 1 }}>
                  {n.title}
                </a>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexShrink: 0 }}>
                  {n.ticker && <span style={{ color: 'var(--accent)', fontSize: 10 }}>{n.ticker}</span>}
                  <NewsBadge sentiment={n.sentiment} />
                </div>
              </div>
              {n.source && (
                <p style={{ color: 'var(--dim)', fontSize: 10, marginTop: 4 }}>
                  {n.source} · {n.published_at ? new Date(n.published_at).toLocaleDateString() : ''}
                </p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
