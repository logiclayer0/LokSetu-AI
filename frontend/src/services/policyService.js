import api from './api'

export const policyService = {
  simulate: async (data) => {
    const response = await api.post('/policy/simulate', data)
    return response.data
  },
  getRecommendations: async () => {
    const response = await api.get('/policy/recommendations')
    return response.data
  },
}