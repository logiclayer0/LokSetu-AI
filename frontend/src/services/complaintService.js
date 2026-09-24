import api from './api'

export const complaintService = {
  create: async (data) => {
    const response = await api.post('/complaints/', data)
    return response.data
  },
  createVoice: async (formData) => {
    const response = await api.post('/complaints/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  list: async (filters = {}) => {
    const response = await api.get('/complaints/', { params: filters })
    return response.data
  },
  getById: async (id) => {
    const response = await api.get(`/complaints/${id}`)
    return response.data
  },
  updateStatus: async (id, status) => {
    const response = await api.patch(`/complaints/${id}/status`, null, {
      params: { new_status: status },
    })
    return response.data
  },
}