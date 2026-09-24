import { useSelector, useDispatch } from 'react-redux'
import { setCredentials, logout as logoutAction } from '../store/authSlice'
import api from '../services/api'

export const useAuth = () => {
  const dispatch = useDispatch()
  const { user, token, isAuthenticated } = useSelector((state) => state.auth)

  const login = async (email, password, role) => {
    const response = await api.post('/auth/login-with-role', {
      email,
      password,
      role,
    })
    const userData = {
      email,
      role: response.data.role,
      full_name: email.split('@')[0],
    }
    dispatch(setCredentials({ user: userData, token: response.data.access_token }))
    return response.data
  }

  const register = async (data) => {
    const response = await api.post('/auth/register', data)
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    dispatch(logoutAction())
    window.location.href = '/login'
  }

  return { user, token, isAuthenticated, login, register, logout }
}