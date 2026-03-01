import React, { useEffect, useState } from 'react';
import { api } from '../api';

const card = { background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, padding: '1.25rem', marginBottom: '1rem' };
const lbl  = { fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--accent)', marginBottom: '0.6rem' };

const SENTIMENTS = ['All', 'positive', 'negative', 'neutral'];
const TICKERS    = ['All', 'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX'];

function Badge({ sentiment }) {
  const m = {
    positive: { c: 'var(--green)', b: 'rgba(126,231,135,0.1)', bd: 'rgba(126,231,135,0.3)' },
    negative: { c: 'var(--red)',   b: 'rgba(247,129,102,0.1)', bd: 'rgba(247,129,102,0.3)' },
    neutral:  { c: 'var(--muted)', b: 'rgba(139,148,158,0.1)', bd: 'rgba(139,148,158,0.3)' },
  };
  const s = m[sentiment] || m.neutral;
  return (
    <span style={{ background: s.b, border: `1px solid ${s.bd}`, color: s.c,
      padding: '0.15rem 0.55rem', borderRadius: 3, fontSize: 10, fontWeight: 600 }}>
      {sentiment}
    </span>
  );
}

export default function News() {
  const [articles,  setArticles]  = useState([]);
  const [summary,   setSummary]   = useState(null);
  const [ticker,    setTicker]    = useState('All');
  const [sentiment, setSentiment] = useState('All');
  const [loading,   setLoading]   = useState(false);

  useEffect(() => {
    setLoading(true);
    const t = ticker    === 'All' ? null : ticker;
    const s = sentiment === 'All' ? null : sentiment;
    Promise.all([
      api.news(t, s),
      api.newsSentiment(t),
    ])
      .then(([arts, sum]) => { setArticles(arts); setSummary(sum); })
      .finally(() => setLoading(false));
  }, [ticker, sentiment]);

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>

      {/* Filters */}
      <div style={{ ...card, display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'flex-start' }}>
        <div>
          <p style={lbl}>Ticker</p>
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {TICKERS.map(t => (
              <button key={t} onClick={() => setTicker(t)}
                style={{ background: ticker === t ? 'var(--accent)' : 'var(--surface2)',
                  color: ticker === t ? 'var(--bg)' : 'var(--muted)',
                  border: `1px solid ${ticker === t ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 4, padding: '0.3rem 0.7rem', fontSize: 11 }}>
                {t}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p style={lbl}>Sentiment</p>
          <div style={{ display: 'flex', gap: 4 }}>
            {SENTIMENTS.map(s => (
              <button key={s} onClick={() => setSentiment(s)}
                style={{ background: sentiment === s ? 'var(--accent)' : 'var(--surface2)',
                  color: sentiment === s ? 'var(--bg)' : 'var(--muted)',
                  border: `1px solid ${sentiment === s ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 4, padding: '0.3rem 0.7rem', fontSize: 11, textTransform: 'capitalize' }}>
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Sentiment summary bar */}
      {summary && summary.total > 0 && (
        <div style={card}>
          <p style={lbl}>Sentiment Breakdown — {summary.total} articles</p>
          <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '0.75rem' }}>
            {[['Positive', summary.positive_pct, 'var(--green)'],
              ['Negative', summary.negative_pct, 'var(--red)'],
              ['Neutral',  summary.neutral_pct,  'var(--muted)']].map(([label, pct, color]) => (
              <div key={label} style={{ fontSize: 12 }}>
                <span style={{ color: 'var(--dim)' }}>{label} </span>
                <strong style={{ color }}>{pct}%</strong>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden', background: 'var(--surface2)' }}>
            <div style={{ width: `${summary.positive_pct}%`, background: 'var(--green)' }}/>
            <div style={{ width: `${summary.negative_pct}%`, background: 'var(--red)' }}/>
            <div style={{ width: `${summary.neutral_pct}%`,  background: 'var(--dim)' }}/>
          </div>
        </div>
      )}

      {/* Articles */}
      <div style={card}>
        <p style={lbl}>{loading ? 'Loading...' : `${articles.length} articles`}</p>
        {articles.length === 0 && !loading && (
          <p style={{ color: 'var(--muted)' }}>No articles found. Run the pipeline to fetch news.</p>
        )}
        {articles.map((a, i) => (
          <div key={a.id} style={{ padding: '0.9rem 0', borderBottom: i < articles.length - 1 ? '1px solid var(--border)' : 'none' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem' }}>
              <a href={a.url} target="_blank" rel="noreferrer"
                style={{ color: 'var(--text)', fontSize: 13, lineHeight: 1.5, flex: 1 }}>
                {a.title}
              </a>
              <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexShrink: 0 }}>
                {a.ticker && <span style={{ color: 'var(--accent)', fontSize: 10, fontWeight: 600 }}>{a.ticker}</span>}
                <Badge sentiment={a.sentiment} />
              </div>
            </div>
            {a.description && (
              <p style={{ color: 'var(--muted)', fontSize: 11, marginTop: 4, lineHeight: 1.6 }}>
                {a.description.slice(0, 160)}{a.description.length > 160 ? '...' : ''}
              </p>
            )}
            <p style={{ color: 'var(--dim)', fontSize: 10, marginTop: 4 }}>
              {a.source && `${a.source} · `}
              {a.published_at ? new Date(a.published_at).toLocaleDateString() : ''}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
