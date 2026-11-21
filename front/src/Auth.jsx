import { t, useLanguage } from './i18n'
import { createContext, useContext, useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { api } from './api'
const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)
export function AuthProvider({ children }) {
  useLanguage()

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    api
      .restore()
      .then(setUser)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])
  return (
    <AuthContext.Provider value={{ user, loading, error, updateUser: setUser }}>
      {children}
    </AuthContext.Provider>
  )
}
export function Protected({ children }) {
  useLanguage()

  const { loading, error } = useAuth()
  if (loading) return <div className="page-loading">{t('ui.preparing_the_platform')}</div>
  if (error)
    return (
      <div className="panel" role="alert">
        {t('ui.local_server_unavailable')} {error}
        {t('ui.start_last_train_then_retry')}{' '}
        <button onClick={() => window.location.reload()}>{t('ui.retry')}</button>
      </div>
    )
  return children
}
export function AuthPage() {
  useLanguage()

  return <Navigate to="/dashboard" replace />
}
