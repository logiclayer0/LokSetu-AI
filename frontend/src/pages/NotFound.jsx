import { Link } from 'react-router-dom'

const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-primary-700">404</h1>
        <p className="text-slate-600 mt-2">Page not found</p>
        <Link to="/" className="btn-primary inline-block mt-6">Go Home</Link>
      </div>
    </div>
  )
}

export default NotFound