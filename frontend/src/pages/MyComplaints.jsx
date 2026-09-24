import { useState } from 'react'
import { useComplaints } from '../hooks/useComplaints'
import ComplaintCard from '../components/complaints/ComplaintCard'
import Loader from '../components/common/Loader'
import EmptyState from '../components/common/EmptyState'

const MyComplaints = () => {
  const { complaints, loading, error } = useComplaints()
  const [selected, setSelected] = useState(null)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">My Complaints</h1>
        <p className="text-sm text-slate-500 mt-1">Track your submitted complaints</p>
      </div>
      {loading && <Loader />}
      {error && <p className="text-red-600 text-sm">{error}</p>}
      {!loading && complaints.length === 0 && (
        <EmptyState title="No complaints yet" description="Submit your first complaint from the 'New Complaint' page." />
      )}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {complaints.map((c) => (
          <ComplaintCard key={c.complaint_id} complaint={c} onClick={setSelected} />
        ))}
      </div>
    </div>
  )
}

export default MyComplaints