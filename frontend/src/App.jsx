import { useState } from 'react'
import {
  LayoutDashboard,
  MessageCircle,
  Brain,
  Trophy,
  Wallet,
  Bell,
  Search,
} from 'lucide-react'

import Dashboard from './pages/Dashboard'
import AIAssistant from './pages/AIAssistant'
import MemoryLab from './pages/MemoryLab'
import MemoryChallenge from './pages/MemoryChallenge'
import './index.css'

const navigation = [
  { label: 'Dashboard', icon: LayoutDashboard },
  { label: 'AI Assistant', icon: MessageCircle },
  { label: 'Memory Lab', icon: Brain },
  
]

function App() {
  const [activePage, setActivePage] = useState('Dashboard')

  const pages = {
    Dashboard: <Dashboard />,
    'AI Assistant': <AIAssistant />,
    'Memory Lab': <MemoryLab />,
    
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Wallet size={22} /></div>
          <div>
            <h2>Expense-Manager</h2>
            <span>PERSONAL FINANCE</span>
          </div>
        </div>

        <p className="nav-heading">WORKSPACE</p>

        <nav>
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${activePage === label ? 'active' : ''}`}
              onClick={() => setActivePage(label)}
            >
              <Icon size={19} />
              <span>{label}</span>
              
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="budget-mini">
            <div className="budget-icon"><Wallet size={18} /></div>
            <p>Monthly budget</p>
            <h3>₹20,000</h3>
            <div className="progress-track"><div className="progress-fill" /></div>
            <span>38% of budget used</span>
          </div>

          <div className="profile">
            <div className="avatar">M</div>
            <div><strong>My Account</strong><span>Personal workspace</span></div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {activePage}</div>
          <div className="top-actions">
            <button className="icon-button" aria-label="Search"><Search size={19} /></button>
            <button className="icon-button notification" aria-label="Notifications"><Bell size={19} /></button>
            <div className="top-avatar">M</div>
          </div>
        </header>

        {pages[activePage]}
      </main>
    </div>
  )
}

export default App
