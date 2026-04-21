import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Home, Bell, Lightbulb, Droplets } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Irrigation from './pages/Irrigation'
import Alerts from './pages/Alerts'
import Tips from './pages/Tips'
import './index.css'

const NAV_ITEMS = [
  { to: '/', icon: Home, label: 'Dashboard' },
  { to: '/irrigation', icon: Droplets, label: 'Irrigation' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/tips', icon: Lightbulb, label: 'Tips' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        {/* ── Top bar ──────────────────────────────── */}
        <header className="topbar">
          <div className="topbar-brand">
            <div className="brand-logo">🌾</div>
            <div>
              <div className="brand-name">Govi Netha</div>
              <div className="brand-sub">Smart Irrigation</div>
            </div>
          </div>
          <NavLink to="/alerts" className="topbar-bell">
            <Bell size={20} />
          </NavLink>
        </header>

        {/* ── Page content ─────────────────────────── */}
        <main className="page-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/irrigation" element={<Irrigation />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/tips" element={<Tips />} />
          </Routes>
        </main>

        {/* ── Bottom nav ───────────────────────────── */}
        <nav className="bottom-nav">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </BrowserRouter>
  )
}