import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// ── Shared ─────────────────────────────────────────────────────
export const fetchLatestReading  = () => api.get('/sensors/latest').then(r => r.data)
export const fetchSensorHistory  = (limit = 30) => api.get(`/sensors/history?limit=${limit}`).then(r => r.data)
export const fetchAllAlerts      = () => api.get('/sensors/alerts').then(r => r.data)

// ── Component 1 — Irrigation (Saqib) ──────────────────────────
export const fetchIrrigationStatus     = () => api.get('/irrigation/status').then(r => r.data)
export const fetchIrrigationPrediction = () => api.get('/irrigation/prediction').then(r => r.data)
export const fetchIrrigationHistory    = (limit = 30) => api.get(`/irrigation/history?limit=${limit}`).then(r => r.data)

// ── Component 2 — NPK (Januki) ─────────────────────────────────
export const fetchNPKStatus         = () => api.get('/npk/status').then(r => r.data)
export const fetchNPKRecommendation = () => api.get('/npk/recommendation').then(r => r.data)
export const fetchNPKHistory        = (limit = 30) => api.get(`/npk/history?limit=${limit}`).then(r => r.data)

// ── Component 3 — pH (Ravisha) ─────────────────────────────────
export const fetchPHStatus     = () => api.get('/ph/status').then(r => r.data)
export const fetchPHCorrection = () => api.get('/ph/correction').then(r => r.data)
export const fetchPHHistory    = (limit = 30) => api.get(`/ph/history?limit=${limit}`).then(r => r.data)

// ── Component 4 — Stress (Roshana) ────────────────────────────
export const fetchStressLevel      = () => api.get('/stress/level').then(r => r.data)
export const fetchStressPrediction = () => api.get('/stress/prediction').then(r => r.data)
export const fetchStressHistory    = (limit = 30) => api.get(`/stress/history?limit=${limit}`).then(r => r.data)
