import { useEffect, useState } from 'react'
import { Database, Server, Cpu, Users, MessageSquare, FlaskConical, MapPin } from 'lucide-react'
import api from '../services/api'

const AdminPanel = () => {
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/admin/system-health').then((r) => setHealth(r.data)).catch(() => {})
    api.get('/admin/stats').then((r) => setStats(r.data)).catch(() => {})
  }, [])

  const healthItems = health
    ? [
        {
          label: 'Database',
          value: health.database,
          icon: Database,
        },
        {
          label: 'API Server',
          value: health.api,
          icon: Server,
        },
        {
          label: 'AI Engine',
          value: health.ai_engine,
          icon: Cpu,
        },
      ]
    : []

  const statItems = stats
    ? [
        { label: 'Total Users', value: stats.total_users, icon: Users },
        { label: 'Total Complaints', value: stats.total_complaints, icon: MessageSquare },
        { label: 'Policies Simulated', value: stats.total_policies_simulated, icon: FlaskConical },
        { label: 'Active Regions', value: stats.active_regions, icon: MapPin },
      ]
    : []

  const getStatusColor = (value) => {
    if (value === 'healthy' || value === 'configured') return 'text-green-600 dark:text-green-400'
    if (value === 'not configured' || value === 'unknown') return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getStatusBg = (value) => {
    if (value === 'healthy' || value === 'configured') return 'bg-green-50 dark:bg-green-900/20'
    if (value === 'not configured' || value === 'unknown') return 'bg-yellow-50 dark:bg-yellow-900/20'
    return 'bg-red-50 dark:bg-red-900/20'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Admin Panel</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          System health and platform statistics
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">System Health</h3>
          {health ? (
            <div className="space-y-3">
              {healthItems.map(({ label, value, icon: Icon }) => (
                <div
                  key={label}
                  className={`flex items-center justify-between p-3 rounded-lg ${getStatusBg(value)}`}
                >
                  <div className="flex items-center gap-3">
                    <Icon size={18} className="text-slate-600 dark:text-slate-300" />
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{label}</span>
                  </div>
                  <span className={`text-sm font-semibold capitalize ${getStatusColor(value)}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 dark:text-slate-400">Loading...</p>
          )}
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Platform Stats</h3>
          {stats ? (
            <div className="space-y-3">
              {statItems.map(({ label, value, icon: Icon }) => (
                <div
                  key={label}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-700/50"
                >
                  <div className="flex items-center gap-3">
                    <Icon size={18} className="text-slate-600 dark:text-slate-300" />
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{label}</span>
                  </div>
                  <span className="text-lg font-bold text-slate-800 dark:text-slate-100">
                    {Number(value || 0).toLocaleString('en-IN')}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 dark:text-slate-400">Loading...</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminPanel
