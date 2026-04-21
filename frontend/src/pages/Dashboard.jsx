import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronRight, RefreshCw } from 'lucide-react'
import {
  fetchLatestReading,
  fetchIrrigationStatus,
  fetchAllAlerts,
} from '../api'

export default function Dashboard() {
  const [reading, setReading] = useState(null)
  const [irrigation, setIrrigation] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const navigate = useNavigate()

  const load = async () => {
    try {
      const [r, irr, al] = await Promise.all([
        fetchLatestReading(),
        fetchIrrigationStatus(),
        fetchAllAlerts(),
      ])
      setReading(r)
      setIrrigation(irr)
      setAlerts(al)
      setLastUpdate(new Date())
      setError(null)
    } catch {
      setError('Could not load data — is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 30_000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={load} />

  const moisture = reading?.moisture ?? 0
  const critAlerts = alerts.filter(a => a.severity === 'critical')

  const heroGradient =
    moisture < 40 ? 'linear-gradient(135deg, #dc2626, #ef4444)' :
      moisture < 60 ? 'linear-gradient(135deg, #d97706, #f59e0b)' :
        'linear-gradient(135deg, #16a34a, #22c55e)'

  const moistureLabel =
    moisture < 40 ? 'Critically Low' :
      moisture < 60 ? 'Below Optimal' : 'Healthy'

  return (
    <div>
      {/* Critical alert banners */}
      {critAlerts.map((a, i) => (
        <div key={i} className="banner critical">
          <span className="banner-title">⚠ Critical Alert</span>
          <span className="banner-body">{a.message}</span>
          <span className="banner-time">{new Date(a.timestamp).toLocaleString()}</span>
        </div>
      ))}

      {/* Hero moisture card */}
      <div style={{
        background: heroGradient,
        borderRadius: 20,
        padding: '24px 20px',
        marginBottom: 12,
        color: '#fff',
        boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative circles */}
        <div style={{ position: 'absolute', top: -50, right: -30, width: 180, height: 180, background: 'rgba(255,255,255,0.08)', borderRadius: '50%' }} />
        <div style={{ position: 'absolute', bottom: -30, right: 30, width: 110, height: 110, background: 'rgba(255,255,255,0.05)', borderRadius: '50%' }} />

        <div style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontSize: 11, opacity: 0.8, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
              <span className="live-dot" /> Soil Moisture
            </div>
            <div style={{ fontSize: 58, fontWeight: 900, lineHeight: 1, letterSpacing: -2 }}>
              {moisture.toFixed(1)}
              <span style={{ fontSize: 22, fontWeight: 500, opacity: 0.8, marginLeft: 4 }}>%</span>
            </div>
            <div style={{ marginTop: 6, fontSize: 13, fontWeight: 600, opacity: 0.9 }}>{moistureLabel}</div>
            <div style={{ marginTop: 4, fontSize: 11, opacity: 0.65 }}>
              Updated {lastUpdate ? lastUpdate.toLocaleTimeString() : '—'}
            </div>
          </div>
          <MoistureRing value={moisture} />
        </div>

        {/* Threshold bar */}
        <div style={{ marginTop: 18 }}>
          <div style={{ height: 6, background: 'rgba(255,255,255,0.25)', borderRadius: 99, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${Math.min(100, moisture)}%`, background: 'rgba(255,255,255,0.85)', borderRadius: 99, transition: 'width 0.8s ease' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, opacity: 0.65, marginTop: 4 }}>
            <span>0%</span><span>Critical 40%</span><span>Warning 60%</span><span>100%</span>
          </div>
        </div>
      </div>

      {/* Temp + Humidity + Edge AI stats */}
      <div className="stat-row">
        <div className="stat-card">
          <div style={{ fontSize: 20, marginBottom: 2 }}>🌡️</div>
          <div className="stat-value">
            {reading?.temperature?.toFixed(1) ?? '—'}
            <span className="stat-unit">°C</span>
          </div>
          <div className="stat-label">Temperature</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 20, marginBottom: 2 }}>💨</div>
          <div className="stat-value">
            {reading?.humidity?.toFixed(1) ?? '—'}
            <span className="stat-unit">%</span>
          </div>
          <div className="stat-label">Humidity</div>
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 20, marginBottom: 2 }}>
            {reading?.edge_state === 2 ? '🔴' : reading?.edge_state === 1 ? '🟡' : '🟢'}
          </div>
          <div style={{
            fontSize: 11, fontWeight: 700,
            color: reading?.edge_state === 2 ? '#dc2626' : reading?.edge_state === 1 ? '#d97706' : '#16a34a',
          }}>
            {reading?.edge_label ?? 'OK'}
          </div>
          <div className="stat-label">Edge AI</div>
        </div>
      </div>

      {/* Irrigation status → tappable link to /irrigation */}
      {irrigation && (
        <div
          className="card"
          style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
          onClick={() => navigate('/irrigation')}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && navigate('/irrigation')}
        >
          <div style={{ flex: 1, marginRight: 12 }}>
            <div className="card-title">Irrigation Status</div>
            <div style={{ fontWeight: 600, fontSize: 14, marginTop: 2, lineHeight: 1.4 }}>
              {irrigation.message}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
            <span className={`badge ${irrigation.severity}`}>{irrigation.severity?.toUpperCase()}</span>
            <ChevronRight size={16} color="var(--text-muted)" />
          </div>
        </div>
      )}

      {/* Auto-refresh note */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--text-muted)', justifyContent: 'center', marginTop: 4 }}>
        <RefreshCw size={11} /> Auto-refreshes every 30 seconds
      </div>
    </div>
  )
}

/** Circular progress ring for moisture */
function MoistureRing({ value }) {
  const r = 30
  const stroke = 5
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - Math.min(100, Math.max(0, value)) / 100)
  return (
    <svg width="76" height="76" viewBox="0 0 76 76">
      <circle cx="38" cy="38" r={r} fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth={stroke} />
      <circle cx="38" cy="38" r={r} fill="none" stroke="rgba(255,255,255,0.85)" strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${circ} ${circ}`}
        strokeDashoffset={offset}
        transform="rotate(-90 38 38)"
        style={{ transition: 'stroke-dashoffset 0.8s ease' }}
      />
      <text x="38" y="43" textAnchor="middle" fill="#fff" fontSize="15" fontWeight="800">
        {Math.round(value)}%
      </text>
    </svg>
  )
}

function LoadingState() {
  return (
    <div className="loading-wrap">
      <div className="loading-spinner" />
      <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Loading dashboard…</div>
    </div>
  )
}

function ErrorState({ message, onRetry }) {
  return (
    <div style={{ padding: 16 }}>
      <div className="banner critical">
        <span className="banner-title">⚠ Connection Error</span>
        <span className="banner-body">{message}</span>
      </div>
      <button
        onClick={onRetry}
        style={{ display: 'block', margin: '0 auto', padding: '10px 24px', background: 'var(--brand-green)', color: '#fff', border: 'none', borderRadius: 10, fontWeight: 700, cursor: 'pointer', fontSize: 13 }}
      >
        Retry
      </button>
    </div>
  )
}