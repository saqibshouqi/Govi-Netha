import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, LineChart, Line } from 'recharts'
import { fetchNPKStatus, fetchPHStatus, fetchNPKHistory, fetchPHHistory } from '../api'

export default function Soil() {
  const [npk,       setNpk]       = useState(null)
  const [ph,        setPh]        = useState(null)
  const [npkHist,   setNpkHist]   = useState([])
  const [phHist,    setPhHist]    = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    Promise.allSettled([
      fetchNPKStatus(), fetchPHStatus(), fetchNPKHistory(20), fetchPHHistory(20)
    ]).then(([n, p, nh, ph_]) => {
      if (n.status  === 'fulfilled') setNpk(n.value)
      if (p.status  === 'fulfilled') setPh(p.value)
      if (nh.status === 'fulfilled') setNpkHist(nh.value)
      if (ph_.status === 'fulfilled') setPhHist(ph_.value)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="loading">Loading soil data…</p>

  const npkBarData = npk ? [
    { name: 'N', value: npk.nitrogen?.value,   fill: '#16a34a' },
    { name: 'P', value: npk.phosphorus?.value, fill: '#d97706' },
    { name: 'K', value: npk.potassium?.value,  fill: '#f97316' },
  ] : []

  return (
    <div>
      <div className="section-title">Soil Health</div>

      {/* pH card */}
      {ph && (
        <div className="card" style={{ background: ph.severity === 'normal' ? '#f3e8ff' : undefined }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <div className="card-title">Soil pH Level</div>
              <div style={{ fontSize: 11, color: '#7c3aed' }}>
                {ph.status === 'optimal' ? 'Optimal for paddy' : ph.status?.replace(/_/g, ' ')}
              </div>
            </div>
            <span className={`badge ${ph.severity}`}>{ph.severity?.toUpperCase()}</span>
          </div>
          <div className="card-value" style={{ color: '#7c3aed', fontSize: 36, marginTop: 8 }}>
            {ph.ph?.toFixed(1)} <span className="card-unit">pH</span>
          </div>
          {/* pH scale bar */}
          <div style={{ position: 'relative', marginTop: 12 }}>
            <div style={{ height: 8, borderRadius: 99,
              background: 'linear-gradient(to right, #ef4444, #eab308, #22c55e, #eab308, #ef4444)' }} />
            {/* Marker */}
            <div style={{
              position: 'absolute', top: -4, width: 16, height: 16,
              background: '#7c3aed', borderRadius: '50%', border: '2px solid white',
              left: `calc(${((ph.ph - 4) / 10) * 100}% - 8px)`, transform: 'translateY(0)',
            }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, marginTop: 4, color: 'var(--text-muted)' }}>
              <span>4</span><span>Optimal: 5.5–7.0</span><span>8</span>
            </div>
          </div>
          <p style={{ fontSize: 12, marginTop: 8, color: 'var(--text-primary)' }}>{ph.message}</p>
        </div>
      )}

      {/* NPK bar chart */}
      <div className="card">
        <div className="section-title" style={{ fontSize: 14 }}>NPK Levels</div>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={npkBarData} barSize={50}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#16a34a"
              label={{ position: 'top', fontSize: 12, fontWeight: 700 }}
              isAnimationActive>
              {npkBarData.map((entry, i) => (
                <rect key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* NPK detail cards */}
      {npk && ['nitrogen', 'phosphorus', 'potassium'].map(key => {
        const d = npk[key]
        if (!d) return null
        const cls = d.status === 'low' ? 'critical' : d.status === 'below_optimal' ? 'warning' : 'normal'
        const pct = Math.min(100, (d.value / (key === 'potassium' ? 250 : key === 'nitrogen' ? 150 : 100)) * 100)
        const barColor = d.status === 'low' ? 'red' : d.status === 'below_optimal' ? 'amber' : 'green'
        return (
          <div key={key} className="card" style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: 700, textTransform: 'capitalize' }}>{key}</span>
              <span className={`badge ${cls}`}>{d.status?.replace(/_/g, ' ').toUpperCase()}</span>
            </div>
            <div style={{ fontSize: 22, fontWeight: 700, margin: '4px 0' }}>
              {d.value?.toFixed(0)} <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>mg/kg</span>
            </div>
            <div className="progress-bar-wrap">
              <div className={`progress-bar ${barColor}`} style={{ width: `${pct}%` }} />
            </div>
          </div>
        )
      })}

      {/* pH trend chart */}
      {phHist.length > 1 && (
        <div className="card">
          <div className="section-title" style={{ fontSize: 14 }}>pH Trend</div>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={phHist}>
              <XAxis dataKey="created_at" tickFormatter={v => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} hide />
              <YAxis domain={[4, 9]} />
              <Tooltip labelFormatter={v => new Date(v).toLocaleString()} />
              <ReferenceLine y={5.5} stroke="#d97706" strokeDasharray="4 2" />
              <ReferenceLine y={7.0} stroke="#d97706" strokeDasharray="4 2" />
              <Line type="monotone" dataKey="ph" stroke="#7c3aed" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
