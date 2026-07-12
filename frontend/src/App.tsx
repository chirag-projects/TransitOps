import { useEffect, useState } from 'react'

import { LoginPage, type LoginPayload } from './components/LoginPage.tsx'
import { Sidebar, type SidebarItem } from './components/Sidebar.tsx'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1/login'
const AUTH_TOKEN_KEY = 'x_auth_token'
const AUTH_USER_KEY = 'transitops_user'

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

type AuthUser = {
  username?: string
  role?: string
}

function isExpiredJwt(token: string) {
  try {
    const payloadPart = token.split('.')[1]

    if (!payloadPart) {
      return true
    }

    const normalizedPayload = payloadPart.replace(/-/g, '+').replace(/_/g, '/')
    const decodedPayload = JSON.parse(atob(normalizedPayload)) as { exp?: number }

    if (!decodedPayload.exp) {
      return true
    }

    return decodedPayload.exp * 1000 <= Date.now()
  } catch {
    return true
  }
}

function App() {
  const [activeTab, setActiveTab] = useState(menuItems[0].label)
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [authUser, setAuthUser] = useState<AuthUser | null>(null)
  const [loginError, setLoginError] = useState<string | null>(null)

  useEffect(() => {
    const storedToken = localStorage.getItem(AUTH_TOKEN_KEY)
    const storedUser = localStorage.getItem(AUTH_USER_KEY)

    if (storedToken && !isExpiredJwt(storedToken)) {
      setAuthToken(storedToken)
    } else if (storedToken) {
      localStorage.removeItem(AUTH_TOKEN_KEY)
      localStorage.removeItem(AUTH_USER_KEY)
    }

    if (storedUser) {
      try {
        setAuthUser(JSON.parse(storedUser) as AuthUser)
      } catch {
        localStorage.removeItem(AUTH_USER_KEY)
      }
    }
  }, [])

  const handleLogin = async (payload: LoginPayload) => {
    setLoginError(null)

    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    const responseData = (await response.json().catch(() => null)) as
      | { token?: string; user?: AuthUser; detail?: string }
      | null

    if (!response.ok) {
      throw new Error(responseData?.detail ?? 'Unable to sign in. Check your credentials and try again.')
    }

    if (!responseData?.token) {
      throw new Error('Authentication succeeded, but no token was returned.')
    }

    localStorage.setItem(AUTH_TOKEN_KEY, responseData.token)
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(responseData.user ?? {}))
    setAuthToken(responseData.token)
    setAuthUser(responseData.user ?? null)
  }

  const handleLogout = () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)
    setAuthToken(null)
    setAuthUser(null)
    setActiveTab(menuItems[0].label)
  }

  if (!authToken) {
    return (
      <LoginPage
        onLogin={handleLogin}
        error={loginError}
        onErrorChange={setLoginError}
      />
    )
  }

  return (
    <div className="app-shell">
      <Sidebar items={menuItems} activeItem={activeTab} onSelect={setActiveTab} />

      <main className="content-area">
        <header className="topbar">
          <div>
            <p className="topbar__label">Signed in as</p>
            <h1 className="topbar__title">{authUser?.username ?? 'TransitOps user'}</h1>
          </div>

          <button type="button" className="topbar__logout" onClick={handleLogout}>
            Log out
          </button>
        </header>

        <section className="content-card">
          <p className="eyebrow">Current tab</p>
          <h2>{activeTab}</h2>
          <p>
            This dashboard is intentionally minimal. The token from the login page is stored as
            <span className="inline-code">x_auth_token</span> so the user can stay signed in.
          </p>
        </section>
      </main>
    </div>
  )
}

export default App
