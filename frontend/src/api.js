const BASE = process.env.REACT_APP_API_BASE || '';

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

async function post(path) {
  const res = await fetch(`${BASE}${path}`, { method: 'POST' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  health:            ()         => get('/api/health'),
  dashboard:         ()         => get('/api/dashboard'),
  stockHistory:      (ticker, limit=30) => get(`/api/stocks/${ticker}/history?limit=${limit}`),
  stockSummaries:    ()         => get('/api/stocks/summary'),
  news:              (ticker, sentiment) => {
    const params = new URLSearchParams();
    if (ticker)    params.append('ticker', ticker);
    if (sentiment) params.append('sentiment', sentiment);
    return get(`/api/news?${params}&limit=30`);
  },
  newsSentiment:     (ticker)   => get(`/api/news/sentiment-summary${ticker ? `?ticker=${ticker}` : ''}`),
  pipelineRuns:      ()         => get('/api/pipeline/runs'),
  triggerPipeline:   ()         => post('/api/pipeline/run'),
  triggerPrices:     ()         => post('/api/pipeline/run/prices'),
  triggerNews:       ()         => post('/api/pipeline/run/news'),
};
