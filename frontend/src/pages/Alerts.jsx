import { useEffect, useState } from 'react'
import { fetchAllAlerts } from '../api'

export default function Alerts() {
  const [alerts,  setAlerts]  = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllAlerts()
      .then(setAlerts)
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="loading">Loading alerts…</p>

  const critical = alerts.filter(a => a.severity === 'critical')
  const warning  = alerts.filter(a => a.severity === 'warning')
  const normal   = alerts.filter(a => a.severity === 'normal')

  return (
    <div>
      <div className="section-title">Alerts
        <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--text-muted)', marginLeft: 8 }}>
          Real-time notifications from Edge AI
        </span>
      </div>

      {/* Summary counts */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <CountChip count={critical.length} label="Critical" cls="critical" />
        <CountChip count={warning.length}  label="Warnings" cls="warning" />
        <CountChip count={normal.length}   label="Normal"   cls="normal" />
      </div>

      {alerts.length === 0 && (
        <div className="banner normal">
          <span className="banner-title">✓ All Clear</span>
          <span className="banner-body">No active alerts. All parameters are within normal range.</span>
        </div>
      )}

      {[...critical, ...warning, ...normal].map((a, i) => (
        <AlertCard key={i} alert={a} />
      ))}
    </div>
  )
}

function CountChip({ count, label, cls }) {
  return (
    <div className="card" style={{ flex: 1, margin: 0, textAlign: 'center', padding: '10px 8px' }}>
      <div style={{ fontSize: 22, fontWeight: 800 }} className={cls === 'critical' ? 'text-red' : ''}>
        {count}
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{label}</div>
    </div>
  )
}

function AlertCard({ alert }) {
  const icons = { critical: '🔴', warning: '🟡', normal: '🟢' }
  return (
    <div className={`banner ${alert.severity}`} style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span className="banner-title">{icons[alert.severity]} {alert.component?.toUpperCase()} — {alert.severity?.toUpperCase()}</span>
        <span className={`badge ${alert.severity}`}>{alert.severity?.toUpperCase()}</span>
      </div>
      <span className="banner-body">{alert.message}</span>
      <span className="banner-time">{new Date(alert.timestamp).toLocaleString()}</span>
    </div>
  )
}
