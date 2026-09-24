import { Bell, Search, User, Moon, Sun } from 'lucide-react'
import { useSelector } from 'react-redux'
import { useDarkMode } from '../../hooks/useDarkMode'

const Navbar = () => {
  const user = useSelector((state) => state.auth.user)
  const { isDark, toggle } = useDarkMode()
  const roleLabel = user?.role
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1)
    : 'User'

  return (
    <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3 flex-1 max-w-md">
        <Search size={18} className="text-slate-400 dark:text-slate-500" />
        <input
          type="text"
          placeholder="Search complaints, locations..."
          className="flex-1 bg-transparent outline-none text-sm text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500"
        />
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          title={isDark ? 'Light mode' : 'Dark mode'}
        >
          {isDark ? (
            <Sun size={18} className="text-yellow-500" />
          ) : (
            <Moon size={18} className="text-slate-600" />
          )}
        </button>
        <button className="relative p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
          <Bell size={18} className="text-slate-600 dark:text-slate-300" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
            <User size={16} className="text-white" />
          </div>
          <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{roleLabel}</span>
        </div>
      </div>
    </header>
  )
}

export default Navbar