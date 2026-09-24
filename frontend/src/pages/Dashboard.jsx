import { useEffect, useState } from 'react'
import { MessageSquare, CheckCircle, AlertTriangle, TrendingUp } from 'lucide-react'
import StatCard from '../components/dashboard/StatCard'
import { analyticsService } from '../services/analyticsService'

const Dashboard = () => {
  const [overview, setOverview] = useState(null)

  useEffect(() => {
    analyticsService.getOverview().then(setOverview).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Overview of citizen complaints and infrastructure priorities</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Complaints" value={overview?.total_complaints ?? 0} icon={MessageSquare} color="primary" />
        <StatCard title="Resolved" value={overview?.resolved ?? 0} icon={CheckCircle} color="green" />
        <StatCard title="Pending" value={overview?.pending ?? 0} icon={AlertTriangle} color="orange" />
        <StatCard title="High Priority" value={overview?.high_priority ?? 0} icon={TrendingUp} color="red" />
      </div>
    </div>
  )
}

export default Dashboard