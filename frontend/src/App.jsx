import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

import Dashboard from './pages/Dashboard'
import Complaints from './pages/Complaints'
import Analytics from './pages/Analytics'
import PolicySimulator from './pages/PolicySimulator'
import Login from './pages/Login'
import Register from './pages/Register'
import NotFound from './pages/NotFound'
import MyComplaints from './pages/MyComplaints'
import NewComplaint from './pages/NewComplaint'
import DepartmentComplaints from './pages/DepartmentComplaints'
import AdminPanel from './pages/AdminPanel'
import Layout from './components/common/Layout'

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthenticated } = useSelector((state) => state.auth)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to={user?.role === 'citizen' ? '/my-complaints' : '/'} replace />
  }
  return children
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="complaints"
          element={
            <ProtectedRoute allowedRoles={['admin', 'officer']}>
              <Complaints />
            </ProtectedRoute>
          }
        />
        <Route
          path="analytics"
          element={
            <ProtectedRoute allowedRoles={['admin', 'officer', 'analyst']}>
              <Analytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="policy"
          element={
            <ProtectedRoute allowedRoles={['admin', 'analyst']}>
              <PolicySimulator />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminPanel />
            </ProtectedRoute>
          }
        />
        <Route
          path="my-complaints"
          element={
            <ProtectedRoute allowedRoles={['citizen']}>
              <MyComplaints />
            </ProtectedRoute>
          }
        />
        <Route
          path="new-complaint"
          element={
            <ProtectedRoute allowedRoles={['citizen']}>
              <NewComplaint />
            </ProtectedRoute>
          }
        />
        <Route
          path="department"
          element={
            <ProtectedRoute allowedRoles={['officer']}>
              <DepartmentComplaints />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App