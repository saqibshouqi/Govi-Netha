import { useEffect, useState } from 'react'
import { Droplets, Thermometer, Wind, FlaskConical } from 'lucide-react'
import {
  fetchLatestReading,
  fetchIrrigationStatus,
  fetchNPKStatus,
  fetchPHStatus,
  fetchStressLevel,
  fetchAllAlerts,
} from '../api'

export default function Dashboard() {
  const [reading,    setReading]    = useState(null)
  const [irrigation, setIrrigation] = useState(null)
  const [npk,        setNpk]        = useState(null)
  const [ph,         setPh]         = useState(null)
  const [stress,     setStress]     = useState(null)
  const [alerts,     setAlerts]     = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const [r, irr, n, p, s, al] = await Promise.all([
          fetchLatestReading(),
          fetchIrrigationStatus(),
          fetchNPKStatus(),
          fetchPHStatus(),
          fetchStressLevel(),
          fetchAllAlerts(),
        ])
        setReading(r);    setIrrigation(irr)
        setNpk(n);        setPh(p)
        setStress(s);     setAlerts(al)
      } catch (e) {
        setError('Could not load data — is the backend running?')
      } finally {
        setLoading(false)
      }
    }
    load()
    const interval = setInterval(load, 30000)   // auto-refresh every 30s
    return () => clearInterval(interval)
  }, [])

  if (loading) return <p className="loading">Loading dashboard…</p>
  if (error)   return <p className="error">{error}</p>

  const criticalAlerts = alerts.filter(a => a.severity === 'critical')

  // Overall farm status
  const severities = [irrigation, npk, ph, stress].map(x => x?.severity)
  const farmStatus = severities.includes('critical') ? 'critical'
                   : severities.includes('warning')  ? 'warning' : 'normal'

  return (
    <div>
      {/* Critical alerts banner */}
      {criticalAlerts.map((a, i) => (
        <div key={i} className="banner critical">
          <span className="banner-title">⚠ Critical Alert</span>
          <span className="banner-body">{a.message}</span>
          <span className="banner-time">{new Date(a.timestamp).toLocaleString()}</span>
        </div>
      ))}

      {/* Farm status */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div className="card-title">Farm Status</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            Last updated: {reading ? new Date(reading.created_at).toLocaleTimeString() : '—'}
          </div>
        </div>
        <span className={`badge ${farmStatus}`}>
          {farmStatus === 'normal' ? '✓ Healthy' : farmStatus.toUpperCase()}
        </span>
      </div>

      {/* Sensor readings grid */}
      <div className="sensor-grid">
        <SensorCard icon={<Droplets size={18} color="#3b82f6" />}
          label="Soil Moisture" value={reading?.moisture?.toFixed(1)} unit="%" />
        <SensorCard icon={<Thermometer size={18} color="#f97316" />}
          label="Temperature" value={reading?.temperature?.toFixed(1)} unit="°C" />
        <SensorCard icon={<Wind size={18} color="#8b5cf6" />}
          label="Humidity" value={reading?.humidity?.toFixed(1)} unit="%" />
        <SensorCard icon={<FlaskConical size={18} color="#6366f1" />}
          label="Soil pH" value={reading?.ph?.toFixed(1)} unit="" />
      </div>

      {/* NPK levels */}
      <div className="card">
        <div className="section-title" style={{ fontSize: 14 }}>NPK Levels</div>
        <NPKBar label="Nitrogen (N)"   value={reading?.nitrogen}   max={150} />
        <NPKBar label="Phosphorus (P)" value={reading?.phosphorus} max={100} color="amber" />
        <NPKBar label="Potassium (K)"  value={reading?.potassium}  max={250} color="red" />
      </div>

      {/* Component status row */}
      <div className="section-title">System Status</div>
      <StatusRow label="Irrigation" data={irrigation} />
      <StatusRow label="Soil pH"    data={ph} />
      <StatusRow label="Crop Stress" data={stress} />
    </div>
  )
}

function SensorCard({ icon, label, value, unit }) {
  return (
    <div className="card" style={{ margin: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>{icon}
        <span className="card-title" style={{ margin: 0 }}>{label}</span>
      </div>
      <div className="card-value">{value ?? '—'}<span className="card-unit">{unit}</span></div>
    </div>
  )
}

function NPKBar({ label, value, max, color = 'green' }) {
  const pct = value ? Math.min(100, (value / max) * 100) : 0
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
        <span>{label}</span><span style={{ fontWeight: 600 }}>{value?.toFixed(0) ?? '—'}</span>
      </div>
      <div className="progress-bar-wrap">
        <div className={`progress-bar ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function StatusRow({ label, data }) {
  if (!data) return null
  return (
    <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontWeight: 600 }}>{label}</span>
      <span className={`badge ${data.severity}`}>{data.severity?.toUpperCase()}</span>
    </div>
  )
}
