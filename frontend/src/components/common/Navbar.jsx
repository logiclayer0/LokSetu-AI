import { useState } from 'react'
import { Bell, Search, User, Moon, Sun, CheckCircle, AlertCircle } from 'lucide-react'
import { useSelector } from 'react-redux'
import { useDarkMode } from '../../hooks/useDarkMode'

const Navbar = () => {
  const user = useSelector((state) => state.auth.user)
  const { isDark, toggle } = useDarkMode()
  const [showNotifications, setShowNotifications] = useState(false)

  const roleLabel = user?.role
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1)
    : 'User'

  const notifications = [
    { id: 1, title: 'Welcome to LokSetu AI', message: 'Your account is ready.', type: 'success', time: 'Just now' },
    { id: 2, title: 'AI Engine Active', message: 'Groq LLaMA 3.3 70B is connected.', type: 'success', time: '2 min ago' },
  ]

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
        >
          {isDark ? <Sun size={18} className="text-yellow-500" /> : <Moon size={18} className="text-slate-600" />}
        </button>

        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          >
            <Bell size={18} className="text-slate-600 dark:text-slate-300" />
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg z-50">
              <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                <h3 className="font-semibold text-slate-800 dark:text-slate-100">Notifications</h3>
              </div>
              <div className="max-h-64 overflow-y-auto">
                {notifications.length === 0 ? (
                  <p className="p-4 text-sm text-slate-500 dark:text-slate-400 text-center">No notifications</p>
                ) : (
                  notifications.map((n) => (
                    <div key={n.id} className="p-4 border-b border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50">
                      <div className="flex items-start gap-3">
                        {n.type === 'success' ? (
                          <CheckCircle size={16} className="text-green-600 mt-0.5 flex-shrink-0" />
                        ) : (
                          <AlertCircle size={16} className="text-orange-600 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{n.title}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{n.message}</p>
                          <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{n.time}</p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

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
