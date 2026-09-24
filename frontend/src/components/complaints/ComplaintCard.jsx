import { MapPin, Clock, User } from 'lucide-react'
import { formatDate, getPriorityColor, getStatusColor, truncate } from '../../utils/formatters'

const ComplaintCard = ({ complaint, onClick }) => {
  return (
    <div
      onClick={() => onClick?.(complaint)}
      className="card cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(complaint.priority)}`}>
            {complaint.priority}
          </span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(complaint.status)}`}>
            {complaint.status}
          </span>
        </div>
        <span className="text-xs text-slate-400">{complaint.complaint_id}</span>
      </div>
      <h3 className="font-semibold text-slate-800 mb-2">{complaint.category}</h3>
      <p className="text-sm text-slate-600 mb-4">{truncate(complaint.original_text, 120)}</p>
      <div className="flex items-center gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <User size={12} /> {complaint.citizen_name}
        </span>
        <span className="flex items-center gap-1">
          <MapPin size={12} /> {complaint.location}
        </span>
        <span className="flex items-center gap-1">
          <Clock size={12} /> {formatDate(complaint.created_at)}
        </span>
      </div>
    </div>
  )
}

export default ComplaintCard