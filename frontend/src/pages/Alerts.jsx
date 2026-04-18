import { useEffect, useState } from 'react'
import { RefreshCw, CheckCircle } from 'lucide-react'
import { fetchAllAlerts } from '../api'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastFetch, setLastFetch] = useState(null)

  const load = () => {
    fetchAllAlerts()
      .then(data => { setAlerts(data); setLastFetch(new Date()) })
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 60_000)
    return () => clearInterval(interval)
  }, [])

  const critical = alerts.filter(a => a.severity === 'critical')
  const warning = alerts.filter(a => a.severity === 'warning')
  const normal = alerts.filter(a => a.severity === 'normal')

  return (
    <div>
      {/* Header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="section-title" style={{ marginBottom: 0 }}>Alerts</div>
        <button
          onClick={load}
          style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12, color: 'var(--text-muted)', background: 'none', border: '1px solid var(--border)', borderRadius: 8, padding: '5px 12px', cursor: 'pointer', fontWeight: 500 }}
        >
          <RefreshCw size={11} /> Refresh
        </button>
      </div>

      {/* Summary chips */}
      <div className="stat-row" style={{ marginBottom: 16 }}>
        <CountCard count={critical.length} label="Critical" activeColor="#dc2626" activeBg="#fef2f2" />
        <CountCard count={warning.length} label="Warnings" activeColor="#d97706" activeBg="#fffbeb" />
        <CountCard count={normal.length} label="Normal" activeColor="#16a34a" activeBg="#f0fdf4" />
      </div>

      {/* Loading */}
      {loading && alerts.length === 0 && (
        <div className="loading-wrap"><div className="loading-spinner" /></div>
      )}

      {/* Empty state */}
      {!loading && alerts.length === 0 && (
        <div style={{ textAlign: 'center', padding: '52px 24px' }}>
          <CheckCircle size={52} color="#16a34a" style={{ marginBottom: 14 }} />
          <div style={{ fontWeight: 700, fontSize: 18, marginBottom: 6 }}>All Clear</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>
            No active alerts. Soil moisture and temperature are within normal range.
          </div>
        </div>
      )}

      {/* Alert cards — critical first */}
      {[...critical, ...warning, ...normal].map((a, i) => (
        <AlertCard key={i} alert={a} />
      ))}

      {lastFetch && (
        <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
          Last checked: {lastFetch.toLocaleTimeString()}
        </div>
      )}
    </div>
  )
}

function CountCard({ count, label, activeColor, activeBg }) {
  const active = count > 0
  return (
    <div style={{
      flex: 1,
      background: active ? activeBg : '#fff',
      border: `1px solid ${active ? activeColor + '40' : 'var(--border)'}`,
      borderRadius: 12, padding: '12px 8px', textAlign: 'center',
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      transition: 'all 0.2s',
    }}>
      <div style={{ fontSize: 28, fontWeight: 900, color: active ? activeColor : 'var(--text-muted)', lineHeight: 1 }}>{count}</div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500, marginTop: 3 }}>{label}</div>
    </div>
  )
}

function AlertCard({ alert }) {
  const iconMap = { critical: '🔴', warning: '🟡', normal: '🟢' }
  const bgMap = { critical: 'var(--critical-bg)', warning: 'var(--warning-bg)', normal: '#fff' }
  return (
    <div style={{
      background: bgMap[alert.severity] ?? '#fff',
      border: '1px solid var(--border)',
      borderRadius: 14, padding: '14px 16px', marginBottom: 10,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <span style={{ fontSize: 16 }}>{iconMap[alert.severity]}</span>
          <span style={{ fontWeight: 700, fontSize: 13 }}>
            {alert.component?.toUpperCase()} — {alert.severity?.toUpperCase()}
          </span>
        </div>
        <span className={`badge ${alert.severity}`}>{alert.severity?.toUpperCase()}</span>
      </div>
      <p style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.55 }}>{alert.message}</p>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
        {new Date(alert.timestamp).toLocaleString()}
      </div>
    </div>
  )
}