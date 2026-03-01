import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { api } from '../api';
import { WATCHLIST_DEFAULT } from '../constants';

const card = {
  background: 'var(--surface)', border: '1px solid var(--border)',
  borderRadius: 8, padding: '1.25rem', marginBottom: '1rem',
};
const lbl = {
  fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase',
  color: 'var(--accent)', marginBottom: '0.6rem',
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{ background: 'var(--surface2)', border: '1px solid var(--border)',
      borderRadius: 6, padding: '0.75rem 1rem', fontSize: 11 }}>
      <p style={{ color: 'var(--muted)', marginBottom: 4 }}>{new Date(label).toLocaleDateString()}</p>
      <p>Close: <strong style={{ color: 'var(--accent)' }}>${d.close?.toFixed(2)}</strong></p>
      <p style={{ color: 'var(--dim)' }}>Open: ${d.open?.toFixed(2)} · High: ${d.high?.toFixed(2)} · Low: ${d.low?.toFixed(2)}</p>
      <p style={{ color: 'var(--muted)' }}>Vol: {(d.volume / 1e6).toFixed(1)}M</p>
    </div>
  );
};

export default function Stocks() {
  const [ticker,  setTicker]  = useState('AAPL');
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  useEffect(() => {
    setLoading(true); setError(null);
    api.stockHistory(ticker, 30)
      .then(d => setHistory(d))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [ticker]);

  const prices = history?.prices || [];
  const chartData = prices.map(p => ({ ...p, date: p.date }));
  const closes = prices.map(p => p.close);
  const minClose = closes.length ? Math.min(...closes) : 0;
  const maxClose = closes.length ? Math.max(...closes) : 0;
  const latest = prices[prices.length - 1];
  const prev   = prices[prices.length - 2];
  const isUp   = latest && prev && latest.close >= prev.close;

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1000, margin: '0 auto' }}>

      {/* Ticker selector */}
      <div style={{ ...card, display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <p style={{ ...lbl, width: '100%', marginBottom: '0.75rem' }}>Select Ticker</p>
        {['AAPL','GOOGL','MSFT','AMZN','NVDA','TSLA','META','NFLX'].map(t => (
          <button key={t} onClick={() => setTicker(t)}
            style={{
              background: ticker === t ? 'var(--accent)' : 'var(--surface2)',
              color:      ticker === t ? 'var(--bg)' : 'var(--muted)',
              border:     `1px solid ${ticker === t ? 'var(--accent)' : 'var(--border)'}`,
              borderRadius: 4, padding: '0.35rem 0.9rem', fontSize: 12, fontWeight: 600,
            }}>
            {t}
          </button>
        ))}
      </div>

      {loading && <p style={{ color: 'var(--muted)', padding: '1rem' }}>Loading {ticker}...</p>}

      {error && (
        <div style={{ ...card, color: 'var(--red)' }}>
          ⚠ {error} — Run the pipeline first to fetch data.
        </div>
      )}

      {!loading && !error && latest && (
        <>
          {/* Price header */}
          <div style={{ ...card, display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <div>
              <p style={lbl}>{ticker}</p>
              <p style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 800 }}>
                ${latest.close.toFixed(2)}
              </p>
            </div>
            {prev && (
              <span style={{
                background: isUp ? 'rgba(126,231,135,0.12)' : 'rgba(247,129,102,0.12)',
                border: `1px solid ${isUp ? 'rgba(126,231,135,0.3)' : 'rgba(247,129,102,0.3)'}`,
                color: isUp ? 'var(--green)' : 'var(--red)',
                padding: '0.4rem 1rem', borderRadius: 4, fontSize: 14, fontWeight: 700,
              }}>
                {isUp ? '▲' : '▼'} {Math.abs(((latest.close - prev.close) / prev.close) * 100).toFixed(2)}%
              </span>
            )}
            <div style={{ marginLeft: 'auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem 1.5rem' }}>
              {[
                ['30d High', `$${maxClose.toFixed(2)}`],
                ['30d Low',  `$${minClose.toFixed(2)}`],
                ['Day High', `$${latest.high.toFixed(2)}`],
                ['Day Low',  `$${latest.low.toFixed(2)}`],
              ].map(([k, v]) => (
                <div key={k} style={{ fontSize: 11 }}>
                  <span style={{ color: 'var(--dim)' }}>{k} </span>
                  <strong>{v}</strong>
                </div>
              ))}
            </div>
          </div>

          {/* Chart */}
          <div style={card}>
            <p style={lbl}>30-Day Price History</p>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis
                  dataKey="date"
                  tickFormatter={d => new Date(d).toLocaleDateString('en', { month: 'short', day: 'numeric' })}
                  tick={{ fill: 'var(--muted)', fontSize: 10 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  domain={['auto', 'auto']}
                  tick={{ fill: 'var(--muted)', fontSize: 10 }}
                  tickFormatter={v => `$${v.toFixed(0)}`}
                  width={55}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="close"
                  stroke={isUp ? 'var(--green)' : 'var(--red)'}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: 'var(--accent)' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Raw data table */}
          <div style={card}>
            <p style={lbl}>Price Data ({prices.length} rows)</p>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)' }}>
                    {['Date','Open','High','Low','Close','Volume','Chg%'].map(h => (
                      <th key={h} style={{ textAlign: 'left', padding: '0.4rem 0.6rem', color: 'var(--muted)', fontWeight: 400 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[...prices].reverse().map((p, i) => {
                    const up = p.pct_change >= 0;
                    return (
                      <tr key={i} style={{ borderBottom: '1px solid var(--surface2)' }}>
                        <td style={{ padding: '0.4rem 0.6rem', color: 'var(--muted)' }}>{new Date(p.date).toLocaleDateString()}</td>
                        <td style={{ padding: '0.4rem 0.6rem' }}>${p.open?.toFixed(2)}</td>
                        <td style={{ padding: '0.4rem 0.6rem', color: 'var(--green)' }}>${p.high?.toFixed(2)}</td>
                        <td style={{ padding: '0.4rem 0.6rem', color: 'var(--red)' }}>${p.low?.toFixed(2)}</td>
                        <td style={{ padding: '0.4rem 0.6rem', fontWeight: 600 }}>${p.close?.toFixed(2)}</td>
                        <td style={{ padding: '0.4rem 0.6rem', color: 'var(--muted)' }}>{p.volume ? `${(p.volume/1e6).toFixed(1)}M` : '—'}</td>
                        <td style={{ padding: '0.4rem 0.6rem', color: p.pct_change == null ? 'var(--dim)' : up ? 'var(--green)' : 'var(--red)', fontWeight: 600 }}>
                          {p.pct_change == null ? '—' : `${up ? '+' : ''}${p.pct_change.toFixed(2)}%`}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
