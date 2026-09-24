import { NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, BarChart3, FlaskConical, LogOut, FileText, PlusCircle, Settings } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useSelector } from 'react-redux'

const Sidebar = () => {
  const { logout } = useAuth()
  const user = useSelector((state) => state.auth.user)
  const role = user?.role || 'citizen'

  const adminLinks = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/complaints', label: 'Complaints', icon: MessageSquare },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/policy', label: 'Policy Simulator', icon: FlaskConical },
    { to: '/admin', label: 'Admin Panel', icon: Settings },
  ]

  const citizenLinks = [
    { to: '/my-complaints', label: 'My Complaints', icon: FileText },
    { to: '/new-complaint', label: 'New Complaint', icon: PlusCircle },
  ]

  const officerLinks = [
    { to: '/department', label: 'Department Complaints', icon: MessageSquare },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  ]

  const analystLinks = [
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/policy', label: 'Policy Simulator', icon: FlaskConical },
  ]

  const linksByRole = {
    admin: adminLinks,
    citizen: citizenLinks,
    officer: officerLinks,
    analyst: analystLinks,
  }

  const links = linksByRole[role] || citizenLinks

  return (
    <aside className="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col">
      <div className="p-6 border-b border-slate-200 dark:border-slate-700">
        <h1 className="text-xl font-bold text-primary-700 dark:text-primary-400">LokSetu AI</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 capitalize">{role} Portal</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-slate-200 dark:border-slate-700">
        {user && (
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 px-3 truncate">
            {user.email}
          </p>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 w-full transition-colors"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  )
}

export default Sidebar