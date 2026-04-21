import { useEffect, useState } from 'react'
import {
    AreaChart, Area, XAxis, YAxis, Tooltip,
    ResponsiveContainer, ReferenceLine, CartesianGrid,
} from 'recharts'
import {
    fetchIrrigationStatus,
    fetchIrrigationPrediction,
    fetchIrrigationHistory,
} from '../api'

export default function Irrigation() {
    const [status, setStatus] = useState(null)
    const [pred, setPred] = useState(null)
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.allSettled([
            fetchIrrigationStatus(),
            fetchIrrigationPrediction(),
            fetchIrrigationHistory(30),
        ]).then(([s, p, h]) => {
            if (s.status === 'fulfilled') setStatus(s.value)
            if (p.status === 'fulfilled') setPred(p.value)
            if (h.status === 'fulfilled') setHistory(h.value)
        }).finally(() => setLoading(false))
    }, [])

    if (loading) return (
        <div className="loading-wrap">
            <div className="loading-spinner" />
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Analysing irrigation data…</div>
        </div>
    )

    const severity = status?.severity ?? 'normal'

    const heroStyle = {
        critical: { gradient: 'linear-gradient(135deg, #dc2626, #ef4444)', icon: '🚨' },
        warning: { gradient: 'linear-gradient(135deg, #d97706, #f59e0b)', icon: '⚠️' },
        normal: { gradient: 'linear-gradient(135deg, #16a34a, #22c55e)', icon: '✅' },
    }[severity] ?? { gradient: 'linear-gradient(135deg, #16a34a, #22c55e)', icon: '✅' }

    const predHours = pred?.irrigate_in_hours ?? null
    const predBadge = predHours === null ? 'normal'
        : predHours === 0 ? 'critical'
            : predHours < 4 ? 'warning' : 'normal'
    const predLabel = predBadge === 'critical' ? 'URGENT' : predBadge === 'warning' ? 'SOON' : 'SCHEDULED'

    // Colour the chart line based on latest moisture
    const lastMoisture = history.length ? history[history.length - 1]?.moisture ?? 50 : 50
    const lineColor = lastMoisture < 40 ? '#dc2626' : lastMoisture < 60 ? '#d97706' : '#16a34a'

    return (
        <div>
            <div className="section-title">Smart Irrigation</div>

            {/* ── Status hero ───────────────────────────────────────── */}
            <div style={{
                background: heroStyle.gradient,
                borderRadius: 20,
                padding: '22px 20px',
                marginBottom: 12,
                color: '#fff',
                boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
                position: 'relative',
                overflow: 'hidden',
            }}>
                <div style={{ position: 'absolute', top: -50, right: -30, width: 160, height: 160, background: 'rgba(255,255,255,0.08)', borderRadius: '50%' }} />

                <div style={{ fontSize: 11, opacity: 0.8, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
                    Current Status
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div style={{ fontSize: 44 }}>{heroStyle.icon}</div>
                    <div>
                        <div style={{ fontSize: 21, fontWeight: 800, letterSpacing: -0.3 }}>
                            {status?.status?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) ?? 'No Data'}
                        </div>
                        <div style={{ fontSize: 12, opacity: 0.8, marginTop: 3, lineHeight: 1.4 }}>
                            {status?.message ?? '—'}
                        </div>
                    </div>
                </div>

                {/* Moisture + Temp inline stats */}
                <div style={{ display: 'flex', gap: 24, marginTop: 18, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.2)' }}>
                    <div>
                        <div style={{ fontSize: 26, fontWeight: 900, lineHeight: 1 }}>
                            {status?.moisture_pct?.toFixed(1) ?? '—'}
                            <span style={{ fontSize: 13, fontWeight: 400, opacity: 0.8, marginLeft: 2 }}>%</span>
                        </div>
                        <div style={{ fontSize: 11, opacity: 0.7, marginTop: 3 }}>Moisture</div>
                    </div>
                    <div>
                        <div style={{ fontSize: 26, fontWeight: 900, lineHeight: 1 }}>
                            {status?.temperature_c?.toFixed(1) ?? '—'}
                            <span style={{ fontSize: 13, fontWeight: 400, opacity: 0.8, marginLeft: 2 }}>°C</span>
                        </div>
                        <div style={{ fontSize: 11, opacity: 0.7, marginTop: 3 }}>Temperature</div>
                    </div>
                </div>
            </div>

            {/* ── ML Prediction ─────────────────────────────────────── */}
            {pred && (
                <div className="card">
                    <div className="card-title" style={{ marginBottom: 12 }}>AI Prediction</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>
                                Next irrigation in
                            </div>
                            <div style={{ fontSize: 44, fontWeight: 900, lineHeight: 1, letterSpacing: -1, color: 'var(--text-primary)' }}>
                                {predHours === 0 ? 'Now' : predHours !== null ? `${predHours}h` : '—'}
                            </div>
                            {predHours > 0 && (
                                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 5 }}>
                                    💡 Best time: early morning 6–8 AM
                                </div>
                            )}
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <span className={`badge ${predBadge}`}>{predLabel}</span>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
                                {pred.source === 'ml_model' ? '🤖 ML Model' : '📏 Rule-based'}
                            </div>
                            {pred.confidence && (
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                                    Confidence: {pred.confidence}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Urgency progress bar */}
                    {predHours !== null && (
                        <div style={{ marginTop: 16 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginBottom: 5 }}>
                                <span>Irrigate now</span>
                                <span>Next 48 hours</span>
                            </div>
                            <div className="progress-bar-wrap">
                                <div
                                    className={`progress-bar ${predBadge === 'critical' ? 'red' : predBadge === 'warning' ? 'amber' : 'green'}`}
                                    style={{ width: `${Math.min(100, (predHours / 48) * 100)}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {pred.note && (
                        <div style={{ marginTop: 12, padding: '8px 12px', background: '#f0fdf4', borderRadius: 8, fontSize: 12, color: '#15803d' }}>
                            💡 {pred.note}
                        </div>
                    )}
                </div>
            )}

            {/* ── Moisture trend chart ──────────────────────────────── */}
            {history.length > 1 && (
                <div className="card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <div className="section-title" style={{ fontSize: 14, marginBottom: 0 }}>Moisture Trend</div>
                        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                            Last {history.length} readings
                        </span>
                    </div>

                    <ResponsiveContainer width="100%" height={190}>
                        <AreaChart data={history} margin={{ top: 5, right: 4, bottom: 0, left: -22 }}>
                            <defs>
                                <linearGradient id="moistureGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={lineColor} stopOpacity={0.25} />
                                    <stop offset="95%" stopColor={lineColor} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
                            <XAxis
                                dataKey="created_at"
                                tickFormatter={v => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                tick={{ fontSize: 10, fill: '#9ca3af' }}
                                axisLine={false} tickLine={false}
                            />
                            <YAxis
                                domain={[0, 100]}
                                tick={{ fontSize: 10, fill: '#9ca3af' }}
                                axisLine={false} tickLine={false}
                            />
                            <Tooltip
                                labelFormatter={v => new Date(v).toLocaleString()}
                                formatter={(v, name) => [
                                    `${Number(v).toFixed(1)}${name === 'moisture' ? '%' : '°C'}`,
                                    name === 'moisture' ? 'Moisture' : 'Temperature',
                                ]}
                                contentStyle={{ borderRadius: 10, border: '1px solid #e5e7eb', boxShadow: '0 4px 16px rgba(0,0,0,0.08)', fontSize: 12 }}
                            />
                            <ReferenceLine y={40} stroke="#dc2626" strokeDasharray="4 2" strokeWidth={1.5}
                                label={{ value: 'Critical 40%', position: 'insideTopRight', fontSize: 9, fill: '#dc2626' }} />
                            <ReferenceLine y={60} stroke="#d97706" strokeDasharray="4 2" strokeWidth={1.5}
                                label={{ value: 'Warning 60%', position: 'insideTopRight', fontSize: 9, fill: '#d97706' }} />
                            <Area
                                type="monotone" dataKey="moisture"
                                stroke={lineColor} strokeWidth={2.5}
                                fill="url(#moistureGradient)"
                                dot={false} activeDot={{ r: 4 }}
                                name="moisture"
                            />
                            <Area
                                type="monotone" dataKey="temperature"
                                stroke="#f97316" strokeWidth={1.5}
                                fill="none" dot={false}
                                name="temperature"
                            />
                        </AreaChart>
                    </ResponsiveContainer>

                    <div style={{ display: 'flex', gap: 18, marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                            <div style={{ width: 14, height: 3, background: lineColor, borderRadius: 99 }} />
                            Soil Moisture %
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                            <div style={{ width: 14, height: 3, background: '#f97316', borderRadius: 99 }} />
                            Temperature °C
                        </div>
                    </div>
                </div>
            )}

            {/* ── Threshold reference ───────────────────────────────── */}
            <div className="card">
                <div className="card-title" style={{ marginBottom: 12 }}>Threshold Guide</div>
                {[
                    { label: 'Irrigate Now', range: '< 40%', cls: 'critical', bg: 'var(--critical-bg)' },
                    { label: 'Irrigate Soon', range: '40–60%', cls: 'warning', bg: 'var(--warning-bg)' },
                    { label: 'Optimal', range: '> 60%', cls: 'normal', bg: 'var(--normal-bg)' },
                ].map(t => (
                    <div key={t.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: t.bg, borderRadius: 10, padding: '11px 14px', marginBottom: 8 }}>
                        <span className={`badge ${t.cls}`} style={{ fontSize: 11 }}>{t.label}</span>
                        <span style={{ fontSize: 13, fontWeight: 700 }}>{t.range}</span>
                    </div>
                ))}
            </div>
        </div>
    )
}