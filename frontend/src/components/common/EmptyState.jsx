import { Inbox } from 'lucide-react'

const EmptyState = ({ title = 'No data found', description = 'There is nothing to display here yet.' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
        <Inbox size={28} className="text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-700">{title}</h3>
      <p className="text-sm text-slate-500 mt-1 max-w-md">{description}</p>
    </div>
  )
}

export default EmptyState