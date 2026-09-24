import api from './api'

export const analyticsService = {
  getOverview: async () => {
    const response = await api.get('/analytics/overview')
    return response.data
  },
  getCategories: async () => {
    const response = await api.get('/analytics/categories')
    return response.data
  },
  getHotspots: async () => {
    const response = await api.get('/analytics/hotspots')
    return response.data
  },
  getPriority: async () => {
    const response = await api.get('/analytics/priority')
    return response.data
  },
}