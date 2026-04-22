import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// Sensors (shared)
export const fetchLatestReading = () =>
  api.get('/sensors/latest').then(r => r.data)

export const fetchSensorHistory = (limit = 30) =>
  api.get(`/sensors/history?limit=${limit}`).then(r => r.data)

export const fetchAllAlerts = () =>
  api.get('/sensors/alerts').then(r => r.data)

// Irrigation
export const fetchIrrigationStatus = () =>
  api.get('/irrigation/status').then(r => r.data)

export const fetchIrrigationPrediction = () =>
  api.get('/irrigation/prediction').then(r => r.data)

export const fetchIrrigationHistory = (limit = 30) =>
  api.get(`/irrigation/history?limit=${limit}`).then(r => r.data)