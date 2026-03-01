import React, { useEffect, useState } from 'react';
import { api } from '../api';

const card = { background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, padding: '1.25rem', marginBottom: '1rem' };
const lbl  = { fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--accent)', marginBottom: '0.75rem' };

function StatusBadge({ status }) {
  const m = {
    success: { c: 'var(--green)', b: 'rgba(126,231,135,0.1)', bd: 'rgba(126,231,135,0.3)' },
    failed:  { c: 'var(--red)',   b: 'rgba(247,129,102,0.1)', bd: 'rgba(247,129,102,0.3)' },
    running: { c: 'var(--yellow)',b: 'rgba(227,179,65,0.1)',  bd: 'rgba(227,179,65,0.3)' },
  };
  const s = m[status] || m.running;
  return (
    <span style={{ background: s.b, border: `1px solid ${s.bd}`, color: s.c,
      padding: '0.2rem 0.65rem', borderRadius: 3, fontSize: 11, fontWeight: 600 }}>
      {status === 'success' ? '✓' : status === 'failed' ? '✗' : '⟳'} {status}
    </span>
  );
}

export default function Pipeline() {
  const [runs,      setRuns]      = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [triggering,setTriggering]= useState(null);
  const [message,   setMessage]   = useState(null);

  const fetchRuns = () => {
    setLoading(true);
    api.pipelineRuns()
      .then(setRuns)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchRuns(); }, []);

  async function trigger(type) {
    setTriggering(type); setMessage(null);
    try {
      const fns = { full: api.triggerPipeline, prices: api.triggerPrices, news: api.triggerNews };
      const res = await fns[type]();
      setMessage({ type: 'success', text: res.message });
      setTimeout(fetchRuns, 3000);
    } catch (e) {
      setMessage({ type: 'error', text: e.message });
    } finally {
      setTriggering(null);
    }
  }

  const btnStyle = (active, color = 'var(--accent)') => ({
    background: active ? 'var(--border)' : color,
    color: active ? 'var(--dim)' : color === 'var(--accent)' ? 'var(--bg)' : 'var(--bg)',
    border: 'none', borderRadius: 4, padding: '0.6rem 1.2rem',
    fontSize: 12, fontWeight: 700, cursor: active ? 'not-allowed' : 'pointer',
  });

  return (
    <div style={{ padding: '1.5rem', maxWidth: 900, margin: '0 auto' }}>

      {/* Controls */}
      <div style={card}>
        <p style={lbl}>Manual Pipeline Controls</p>
        <p style={{ color: 'var(--muted)', fontSize: 12, marginBottom: '1rem' }}>
          The pipeline also runs automatically every 30 minutes via APScheduler.
        </p>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button onClick={() => trigger('full')}    disabled={!!triggering} style={btnStyle(!!triggering)}>
            {triggering === 'full' ? 'Running...' : '▶ Run Full Pipeline'}
          </button>
          <button onClick={() => trigger('prices')}  disabled={!!triggering}
            style={{ ...btnStyle(!!triggering, 'var(--green)'), color: 'var(--bg)' }}>
            {triggering === 'prices' ? 'Running...' : '📈 Prices Only'}
          </button>
          <button onClick={() => trigger('news')}    disabled={!!triggering}
            style={{ ...btnStyle(!!triggering, 'var(--yellow)'), color: 'var(--bg)' }}>
            {triggering === 'news' ? 'Running...' : '📰 News Only'}
          </button>
          <button onClick={fetchRuns} style={{ ...btnStyle(false, 'var(--surface2)'), color: 'var(--muted)', border: '1px solid var(--border)' }}>
            ↻ Refresh
          </button>
        </div>

        {message && (
          <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', borderRadius: 6,
            background: message.type === 'success' ? 'rgba(126,231,135,0.1)' : 'rgba(247,129,102,0.1)',
            border: `1px solid ${message.type === 'success' ? 'rgba(126,231,135,0.3)' : 'rgba(247,129,102,0.3)'}`,
            color: message.type === 'success' ? 'var(--green)' : 'var(--red)', fontSize: 12 }}>
            {message.text}
          </div>
        )}
      </div>

      {/* Architecture diagram */}
      <div style={card}>
        <p style={lbl}>ETL Pipeline Architecture</p>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--muted)', lineHeight: 2 }}>
          <p><span style={{ color: 'var(--accent)' }}>EXTRACT</span>   → Yahoo Finance API + NewsAPI</p>
          <p style={{ color: 'var(--dim)' }}>         ↓</p>
          <p><span style={{ color: 'var(--green)' }}>TRANSFORM</span>  → Clean nulls · Calculate % change · Sentiment classification · Dedup</p>
          <p style={{ color: 'var(--dim)' }}>         ↓</p>
          <p><span style={{ color: 'var(--yellow)' }}>LOAD</span>      → PostgreSQL (stock_prices + news_articles tables)</p>
          <p style={{ color: 'var(--dim)' }}>         ↓</p>
          <p><span style={{ color: 'var(--accent)' }}>SCHEDULE</span>  → APScheduler runs every 30 minutes automatically</p>
          <p style={{ color: 'var(--dim)' }}>         ↓</p>
          <p><span style={{ color: 'var(--muted)' }}>AUDIT</span>     → Every run logged to pipeline_runs table</p>
        </div>
      </div>

      {/* Run history */}
      <div style={card}>
        <p style={lbl}>Run History ({runs.length} runs)</p>
        {loading ? (
          <p style={{ color: 'var(--muted)' }}>Loading...</p>
        ) : runs.length === 0 ? (
          <p style={{ color: 'var(--muted)' }}>No runs yet — click Run Pipeline above.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  {['#','Type','Status','Inserted','Skipped','Duration','Started'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '0.4rem 0.75rem', color: 'var(--muted)', fontWeight: 400 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {runs.map((r, i) => (
                  <tr key={r.id} style={{ borderBottom: '1px solid var(--surface2)' }}>
                    <td style={{ padding: '0.5rem 0.75rem', color: 'var(--dim)' }}>#{r.id}</td>
                    <td style={{ padding: '0.5rem 0.75rem', color: 'var(--accent)' }}>{r.run_type}</td>
                    <td style={{ padding: '0.5rem 0.75rem' }}><StatusBadge status={r.status} /></td>
                    <td style={{ padding: '0.5rem 0.75rem', color: 'var(--green)' }}>{r.rows_inserted}</td>
                    <td style={{ padding: '0.5rem 0.75rem', color: 'var(--muted)' }}>{r.rows_skipped}</td>
                    <td style={{ padding: '0.5rem 0.75rem' }}>{r.duration_secs != null ? `${r.duration_secs}s` : '—'}</td>
                    <td style={{ padding: '0.5rem 0.75rem', color: 'var(--dim)' }}>
                      {new Date(r.started_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
