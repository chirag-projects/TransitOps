import { useState } from 'react'

import { Sidebar, type SidebarItem } from './components/Sidebar'
import './App.css'

const menuItems: SidebarItem[] = [
  { label: 'Dashboard' },
  { label: 'Fleet' },
  { label: 'Drivers' },
  { label: 'Trips' },
  { label: 'Maintenance' },
  { label: 'Fuel & Expenses' },
  { label: 'Analytics' },
  { label: 'Settings' },
]

function App() {
  const [activeTab, setActiveTab] = useState(menuItems[0].label)

  return (
    <div className="app-shell">
      <Sidebar items={menuItems} activeItem={activeTab} onSelect={setActiveTab} />

      <main className="content-area">
        <section className="content-card">
          <p className="eyebrow">Current tab</p>
          <h1>{activeTab}</h1>
          <p>
            This screen is intentionally minimal. Use the sidebar to switch between tabs and
            keep the selected option open in the main panel.
          </p>
        </section>
      </main>
    </div>
  )
}

export default App
