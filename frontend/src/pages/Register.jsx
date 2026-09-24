import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'

const Register = () => {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'citizen',
  })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register(form)
      toast.success('Account created. Please sign in.')
      navigate('/login')
    } catch (err) {
      toast.error('Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold text-primary-700 mb-1">LokSetu AI</h1>
        <p className="text-sm text-slate-500 mb-6">Create your account</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            name="full_name"
            placeholder="Full Name"
            className="input-field"
            value={form.full_name}
            onChange={handleChange}
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            className="input-field"
            value={form.email}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            className="input-field"
            value={form.password}
            onChange={handleChange}
            required
          />
          <select
            name="role"
            className="input-field"
            value={form.role}
            onChange={handleChange}
          >
            <option value="citizen">Citizen</option>
            <option value="admin">Admin</option>
            <option value="officer">Officer</option>
            <option value="analyst">Analyst</option>
          </select>
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        <p className="text-sm text-slate-500 mt-4 text-center">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-600 font-medium">Sign In</Link>
        </p>
      </div>
    </div>
  )
}

export default Register