import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  items: [],
  selected: null,
  loading: false,
  error: null,
}

const complaintsSlice = createSlice({
  name: 'complaints',
  initialState,
  reducers: {
    setComplaints: (state, action) => {
      state.items = action.payload
    },
    addComplaint: (state, action) => {
      state.items.unshift(action.payload)
    },
    setSelected: (state, action) => {
      state.selected = action.payload
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
  },
})

export const { setComplaints, addComplaint, setSelected, setLoading, setError } = complaintsSlice.actions
export default complaintsSlice.reducer