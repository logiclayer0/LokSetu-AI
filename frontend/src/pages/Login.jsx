import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('admin')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password, role)
      toast.success('Logged in')
      if (role === 'citizen') navigate('/my-complaints')
      else if (role === 'officer') navigate('/department')
      else if (role === 'analyst') navigate('/analytics')
      else navigate('/')
    } catch (err) {
      toast.error('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold text-primary-700 mb-1">LokSetu AI</h1>
        <p className="text-sm text-slate-500 mb-6">Sign in to your account</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" placeholder="Email" className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <select className="input-field" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="admin">Admin</option>
            <option value="citizen">Citizen</option>
            <option value="officer">Officer</option>
            <option value="analyst">Analyst</option>
          </select>
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-sm text-slate-500 mt-4 text-center">
          New here? <Link to="/register" className="text-primary-600 font-medium">Create account</Link>
        </p>
      </div>
    </div>
  )
}

export default Login