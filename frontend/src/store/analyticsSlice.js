import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  overview: null,
  categories: null,
  hotspots: null,
  priority: null,
  loading: false,
}

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setOverview: (state, action) => {
      state.overview = action.payload
    },
    setCategories: (state, action) => {
      state.categories = action.payload
    },
    setHotspots: (state, action) => {
      state.hotspots = action.payload
    },
    setPriority: (state, action) => {
      state.priority = action.payload
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
  },
})

export const { setOverview, setCategories, setHotspots, setPriority, setLoading } = analyticsSlice.actions
export default analyticsSlice.reducer