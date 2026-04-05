import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Home, Bell, Lightbulb, Leaf, Activity } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Alerts    from './pages/Alerts'
import Tips      from './pages/Tips'
import Soil      from './pages/Soil'
import Stress    from './pages/Stress'
import './index.css'

const NAV_ITEMS = [
  { to: '/',       icon: Home,       label: 'Dashboard' },
  { to: '/alerts', icon: Bell,       label: 'Alerts'    },
  { to: '/tips',   icon: Lightbulb,  label: 'Tips'      },
  { to: '/soil',   icon: Leaf,       label: 'Soil'      },
  { to: '/stress', icon: Activity,   label: 'Stress'    },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        {/* ── Top bar ─────────────────────────────── */}
        <header className="topbar">
          <div className="topbar-brand">
            <span className="brand-name">Govi Netha</span>
            <span className="brand-sub">Smart Agriculture</span>
          </div>
          <NavLink to="/alerts" className="topbar-bell">
            <Bell size={22} />
          </NavLink>
        </header>

        {/* ── Page content ────────────────────────── */}
        <main className="page-content">
          <Routes>
            <Route path="/"       element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />}    />
            <Route path="/tips"   element={<Tips />}      />
            <Route path="/soil"   element={<Soil />}      />
            <Route path="/stress" element={<Stress />}    />
          </Routes>
        </main>

        {/* ── Bottom nav ──────────────────────────── */}
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
