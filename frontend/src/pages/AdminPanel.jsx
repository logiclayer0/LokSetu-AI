import { useEffect, useState } from 'react'
import api from '../services/api'

const AdminPanel = () => {
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/admin/system-health').then((r) => setHealth(r.data)).catch(() => {})
    api.get('/admin/stats').then((r) => setStats(r.data)).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Admin Panel</h1>
        <p className="text-sm text-slate-500 mt-1">System health and platform statistics</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">System Health</h3>
          {health ? (
            <div className="space-y-2">
              {Object.entries(health).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="capitalize text-slate-600">{key}</span>
                  <span className={`font-medium ${value === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">Loading...</p>
          )}
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Platform Stats</h3>
          {stats ? (
            <div className="space-y-2">
              {Object.entries(stats).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="capitalize text-slate-600">{key.replace(/_/g, ' ')}</span>
                  <span className="font-medium text-slate-800">{value}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">Loading...</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminPanel