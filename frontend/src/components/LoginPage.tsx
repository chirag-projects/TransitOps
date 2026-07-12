import { useState, type FormEvent } from 'react'

import './LoginPage.css'

export type LoginPayload = {
  username: string
  password: string
  role?: string
}

type LoginPageProps = {
  onLogin: (payload: LoginPayload) => Promise<void>
  error: string | null
  onErrorChange: (value: string | null) => void
}

const roleOptions = ['Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst']

export function LoginPage({ onLogin, error, onErrorChange }: LoginPageProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('Dispatcher')
  const [rememberMe, setRememberMe] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    onErrorChange(null)

    try {
      await onLogin({ username, password, role })
    } catch (loginError) {
      onErrorChange(loginError instanceof Error ? loginError.message : 'Login failed')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <aside className="auth-panel auth-panel--brand">
        <div className="auth-brand">
          <div className="auth-brand__mark" aria-hidden="true" />
          <div>
            <h1>TransitOps</h1>
            <p>Smart transport operations platform</p>
          </div>
        </div>

        <div className="auth-copy">
          <h2>One login, four roles.</h2>
          <ul>
            {roleOptions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <p className="auth-footer">TransitOps © 2026 · Role based access</p>
      </aside>

      <main className="auth-panel auth-panel--form">
        <div className="auth-form-card">
          <p className="auth-kicker">Sign in to your account</p>
          <h2>Enter your credentials to continue</h2>

          {error ? <div className="auth-error">{error}</div> : null}

          <form className="auth-form" onSubmit={handleSubmit}>
            <label>
              <span>Username</span>
              <input
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="e.g. user@transitops.in"
                autoComplete="username"
                required
              />
            </label>

            <label>
              <span>Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
            </label>

            <label>
              <span>Role</span>
              <select value={role} onChange={(event) => setRole(event.target.value)}>
                {roleOptions.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <div className="auth-form__row">
              <label className="auth-check">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) => setRememberMe(event.target.checked)}
                />
                <span>Remember me</span>
              </label>

              <button type="button" className="auth-link">
                Forgot password?
              </button>
            </div>

            <button type="submit" className="auth-submit" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="auth-help">
            <p>Access is granted by role after login:</p>
            <ul>
              <li>Fleet Manager → Fleet, Maintenance</li>
              <li>Dispatcher → Dashboard, Trips</li>
              <li>Safety Officer → Drivers, Compliance</li>
              <li>Financial Analyst → Fuel & Expenses, Analytics</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}