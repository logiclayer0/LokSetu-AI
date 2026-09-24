import { useState } from 'react'
import toast from 'react-hot-toast'
import { Users, TrendingUp, AlertTriangle, Calendar, ShieldCheck, Lightbulb } from 'lucide-react'
import { policyService } from '../services/policyService'

const PolicySimulator = () => {
  const [form, setForm] = useState({
    policy_title: '',
    policy_description: '',
    target_region: '',
    budget_in_crores: 0,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await policyService.simulate(form)
      setResult(data)
      toast.success('Simulation complete')
    } catch (err) {
      toast.error('Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Policy Simulator</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Forecast the impact of policy decisions before implementation
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <form onSubmit={handleSubmit} className="card space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Policy Title</label>
            <input
              type="text"
              className="input-field"
              value={form.policy_title}
              onChange={(e) => setForm({ ...form, policy_title: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
            <textarea
              rows={4}
              className="input-field"
              value={form.policy_description}
              onChange={(e) => setForm({ ...form, policy_description: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Target Region</label>
            <input
              type="text"
              className="input-field"
              value={form.target_region}
              onChange={(e) => setForm({ ...form, target_region: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Budget (in Crores)</label>
            <input
              type="number"
              className="input-field"
              value={form.budget_in_crores}
              onChange={(e) => setForm({ ...form, budget_in_crores: parseFloat(e.target.value) || 0 })}
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? 'Simulating...' : 'Run Simulation'}
          </button>
        </form>

        <div className="space-y-4">
          {!result && (
            <div className="card flex flex-col items-center justify-center py-16 text-center">
              <Lightbulb size={40} className="text-slate-300 dark:text-slate-600 mb-3" />
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Fill the form and click "Run Simulation" to see AI-powered forecasts.
              </p>
            </div>
          )}

          {result && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="card">
                  <div className="flex items-center gap-2 mb-2">
                    <Users size={16} className="text-primary-600" />
                    <p className="text-xs text-slate-500 dark:text-slate-400">Beneficiaries</p>
                  </div>
                  <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                    {Number(result.estimated_beneficiaries || 0).toLocaleString('en-IN')}
                  </p>
                </div>
                <div className="card">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp size={16} className="text-green-600" />
                    <p className="text-xs text-slate-500 dark:text-slate-400">Budget Used</p>
                  </div>
                  <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                    {Number(result.budget_utilization_percent || 0)}%
                  </p>
                </div>
                <div className="card">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle size={16} className="text-orange-600" />
                    <p className="text-xs text-slate-500 dark:text-slate-400">Risk Score</p>
                  </div>
                  <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                    {Number(result.risk_score || 0)}/10
                  </p>
                </div>
                <div className="card">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar size={16} className="text-blue-600" />
                    <p className="text-xs text-slate-500 dark:text-slate-400">Timeline</p>
                  </div>
                  <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">
                    {Number(result.timeline_months || 0)} mo
                  </p>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center gap-2 mb-3">
                  <ShieldCheck size={18} className="text-primary-600" />
                  <h3 className="font-semibold text-slate-800 dark:text-slate-100">Expected Impact</h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300">
                  {result.expected_impact || 'No impact data available.'}
                </p>
                <div className="mt-4 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                  <span>Duplicate Risk</span>
                  <span className="font-medium">{Number(result.duplicate_risk_percent || 0)}%</span>
                </div>
                <div className="mt-2 w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-red-500 h-2 rounded-full"
                    style={{ width: `${Math.min(Number(result.duplicate_risk_percent || 0), 100)}%` }}
                  />
                </div>
              </div>

              {result.recommendations && result.recommendations.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-3">AI Recommendations</h3>
                  <ul className="space-y-2">
                    {result.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300">
                        <span className="w-5 h-5 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0">
                          {idx + 1}
                        </span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default PolicySimulator