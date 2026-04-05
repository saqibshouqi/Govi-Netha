import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchStressLevel, fetchStressPrediction, fetchStressHistory } from '../api'

export default function Stress() {
  const [level,   setLevel]   = useState(null)
  const [pred,    setPred]    = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      fetchStressLevel(), fetchStressPrediction(), fetchStressHistory(20)
    ]).then(([l, p, h]) => {
      if (l.status === 'fulfilled') setLevel(l.value)
      if (p.status === 'fulfilled') setPred(p.value)
      if (h.status === 'fulfilled') setHistory(h.value)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="loading">Analysing crop stress…</p>

  const idx  = level?.stress_index ?? 0
  const cls  = level?.severity ?? 'normal'
  const gaugeColor = cls === 'critical' ? '#dc2626' : cls === 'warning' ? '#d97706' : '#16a34a'

  const statusDesc = {
    'Low (0–30)':    'Excellent conditions. Continue current practices.',
    'Medium (31–70)':'Moderate stress — monitor and intervene if trend worsens.',
    'High (70+)':    'Critical stress — immediate action required.',
  }

  return (
    <div>
      <div className="section-title">Crop Stress</div>

      {/* Gauge card */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #1d4ed8, #3b82f6)', color: '#fff' }}>
        <div style={{ fontSize: 13, opacity: 0.8, marginBottom: 4 }}>Overall Stress Level</div>
        <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 12 }}>Real-time analysis</div>
        <div className="gauge-wrap" style={{ paddingTop: 8 }}>
          <StressGauge value={idx} color={gaugeColor} />
          <div style={{ marginTop: 12, background: 'rgba(255,255,255,0.2)', borderRadius: 99,
            padding: '4px 16px', fontSize: 14, fontWeight: 700 }}>
            Status: {level?.status === 'low' ? 'Low' : level?.status === 'medium' ? 'Medium' : 'Critical'}
          </div>
        </div>
      </div>

      {/* Stress scale legend */}
      <div className="card">
        <div className="section-title" style={{ fontSize: 14 }}>What does this mean?</div>
        {Object.entries(statusDesc).map(([k, v]) => (
          <div key={k} style={{ fontSize: 13, marginBottom: 6 }}>
            <span style={{ fontWeight: 600 }}>• {k}:</span> {v}
          </div>
        ))}
      </div>

      {/* Contributing factors */}
      {level?.contributing_factors && (
        <div>
          <div className="section-title">Contributing Factors</div>
          {Object.entries(level.contributing_factors).map(([key, f]) => (
            <div key={key} className="card" style={{ marginBottom: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700, textTransform: 'capitalize' }}>{key}</span>
                <span className={`badge ${f.status === 'normal' ? 'normal' : 'warning'}`}>
                  {f.status?.toUpperCase()}
                </span>
              </div>
              <div style={{ fontSize: 22, fontWeight: 700, margin: '4px 0' }}>
                {f.value?.toFixed(1)} <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{f.unit}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ML prediction */}
      {pred?.recommendations && (
        <div className="card">
          <div className="section-title" style={{ fontSize: 14 }}>AI Recommendations</div>
          {pred.recommendations.map((r, i) => (
            <p key={i} style={{ fontSize: 13, marginBottom: 6, color: 'var(--brand-green)' }}>• {r}</p>
          ))}
        </div>
      )}

      {/* History chart */}
      {history.length > 1 && (
        <div className="card">
          <div className="section-title" style={{ fontSize: 14 }}>Temperature Trend</div>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={history}>
              <XAxis dataKey="created_at"
                tickFormatter={v => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                hide />
              <YAxis domain={[15, 45]} />
              <Tooltip labelFormatter={v => new Date(v).toLocaleString()} />
              <Line type="monotone" dataKey="temperature" stroke="#f97316" dot={false} strokeWidth={2} name="Temp °C" />
              <Line type="monotone" dataKey="humidity"    stroke="#3b82f6" dot={false} strokeWidth={2} name="Humidity %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

/** Simple SVG arc gauge */
function StressGauge({ value, color }) {
  const radius = 60
  const stroke = 12
  const norm   = value / 100
  const circ   = Math.PI * radius   // half-circle
  const offset = circ * (1 - norm)

  return (
    <svg width="160" height="90" viewBox="0 0 160 90">
      {/* Background arc */}
      <path d={describeArc(80, 80, radius)} fill="none"
        stroke="rgba(255,255,255,0.3)" strokeWidth={stroke} strokeLinecap="round" />
      {/* Value arc */}
      <path d={describeArc(80, 80, radius)} fill="none"
        stroke={color} strokeWidth={stroke} strokeLinecap="round"
        strokeDasharray={`${circ} ${circ}`}
        strokeDashoffset={offset}
        style={{ transition: 'stroke-dashoffset 0.6s ease' }} />
      {/* Label */}
      <text x="80" y="72" textAnchor="middle" fill="#fff" fontSize="26" fontWeight="800">{value}</text>
      <text x="80" y="87" textAnchor="middle" fill="rgba(255,255,255,0.7)" fontSize="11">out of 100</text>
    </svg>
  )
}

function describeArc(cx, cy, r) {
  // Half-circle from left to right (bottom)
  return `M ${cx - r},${cy} A ${r},${r} 0 0 1 ${cx + r},${cy}`
}
