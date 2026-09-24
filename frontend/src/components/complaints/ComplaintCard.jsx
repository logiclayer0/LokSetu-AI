import { MapPin, Clock, User, Building2 } from 'lucide-react'
import { formatDate, getPriorityColor, getStatusColor, truncate } from '../../utils/formatters'

const ComplaintCard = ({ complaint, onClick }) => {
  return (
    <div
      onClick={() => onClick?.(complaint)}
      className="card cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(complaint.priority)}`}>
            {complaint.priority}
          </span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(complaint.status)}`}>
            {complaint.status}
          </span>
        </div>
        <span className="text-xs text-slate-400 dark:text-slate-500">{complaint.complaint_id}</span>
      </div>

      <div className="mb-3">
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">
          {complaint.category || 'Uncategorized'}
        </h3>
        {complaint.department && (
          <div className="flex items-center gap-1 mt-1 text-xs text-slate-500 dark:text-slate-400">
            <Building2 size={12} />
            <span>{complaint.department}</span>
          </div>
        )}
      </div>

      <p className="text-sm text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
        {truncate(complaint.original_text, 140)}
      </p>

      <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 flex-wrap">
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
