import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { complaintService } from '../services/complaintService'
import { useSelector } from 'react-redux'

const NewComplaint = () => {
  const user = useSelector((state) => state.auth.user)
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    citizen_name: user?.full_name || '',
    citizen_phone: '',
    location: '',
    description: '',
  })

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await complaintService.create({ ...form, language: 'auto' })
      toast.success('Complaint submitted. AI is analyzing...')
      navigate('/my-complaints')
    } catch (err) {
      toast.error('Failed to submit complaint')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">New Complaint</h1>
        <p className="text-sm text-slate-500 mt-1">
          Describe your issue in any language. Our AI will categorize it automatically.
        </p>
      </div>
      <form onSubmit={handleSubmit} className="card space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Your Name</label>
            <input type="text" name="citizen_name" className="input-field" value={form.citizen_name} onChange={handleChange} required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
            <input type="text" name="citizen_phone" className="input-field" value={form.citizen_phone} onChange={handleChange} required />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Location</label>
          <input type="text" name="location" className="input-field" value={form.location} onChange={handleChange} placeholder="e.g., Sector 12, Delhi" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Describe your complaint</label>
          <textarea rows={4} name="description" className="input-field" value={form.description} onChange={handleChange} placeholder="e.g., Sector 12 mein sadak par bada gaddha hai..." required />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={submitting}>
          {submitting ? 'Submitting... AI is analyzing...' : 'Submit Complaint'}
        </button>
      </form>
    </div>
  )
}

export default NewComplaint