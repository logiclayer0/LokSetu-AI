export const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return new Intl.NumberFormat('en-IN').format(num)
}

export const truncate = (str, length = 100) => {
  if (!str) return ''
  return str.length > length ? `${str.substring(0, length)}...` : str
}

export const getPriorityColor = (priority) => {
  const colors = {
    Low: 'bg-green-100 text-green-800',
    Medium: 'bg-yellow-100 text-yellow-800',
    High: 'bg-orange-100 text-orange-800',
    Critical: 'bg-red-100 text-red-800',
  }
  return colors[priority] || 'bg-slate-100 text-slate-800'
}

export const getStatusColor = (status) => {
  const colors = {
    Pending: 'bg-yellow-100 text-yellow-800',
    'In Progress': 'bg-blue-100 text-blue-800',
    Resolved: 'bg-green-100 text-green-800',
    Rejected: 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-slate-100 text-slate-800'
}