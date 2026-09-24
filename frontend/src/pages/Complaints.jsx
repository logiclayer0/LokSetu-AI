import { useState } from 'react'
import toast from 'react-hot-toast'
import { useComplaints } from '../hooks/useComplaints'
import { complaintService } from '../services/complaintService'
import ComplaintCard from '../components/complaints/ComplaintCard'
import Loader from '../components/common/Loader'
import EmptyState from '../components/common/EmptyState'

const Complaints = () => {
  const { complaints, loading, error, refetch } = useComplaints()
  const [selected, setSelected] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    citizen_name: '',
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
      await complaintService.create({
        ...form,
        language: 'auto',
      })
      toast.success('Complaint submitted. AI is analyzing...')
      setForm({ citizen_name: '', citizen_phone: '', location: '', description: '' })
      setShowForm(false)
      refetch()
    } catch (err) {
      toast.error('Failed to submit complaint')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Complaints</h1>
          <p className="text-sm text-slate-500 mt-1">All citizen grievances in one place</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary"
        >
          {showForm ? 'Cancel' : '+ New Complaint'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Your Name</label>
              <input
                type="text"
                name="citizen_name"
                className="input-field"
                value={form.citizen_name}
                onChange={handleChange}
                placeholder="e.g., Ramesh Kumar"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
              <input
                type="text"
                name="citizen_phone"
                className="input-field"
                value={form.citizen_phone}
                onChange={handleChange}
                placeholder="e.g., 9876543210"
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Location</label>
            <input
              type="text"
              name="location"
              className="input-field"
              value={form.location}
              onChange={handleChange}
              placeholder="e.g., Sector 12, Delhi"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Describe your complaint (Hindi, English, or any language)
            </label>
            <textarea
              rows={4}
              name="description"
              className="input-field"
              value={form.description}
              onChange={handleChange}
              placeholder="e.g., Sector 12 mein sadak par bada gaddha hai, bike wale gir jate hain..."
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? 'Submitting... AI is analyzing...' : 'Submit Complaint'}
          </button>
        </form>
      )}

      {loading && <Loader />}
      {error && <p className="text-red-600 text-sm">{error}</p>}
      {!loading && complaints.length === 0 && <EmptyState title="No complaints yet" />}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {complaints.map((c) => (
          <ComplaintCard key={c.complaint_id} complaint={c} onClick={setSelected} />
        ))}
      </div>
    </div>
  )
}

export default Complaints