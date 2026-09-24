import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSlice'
import complaintsReducer from './complaintsSlice'
import analyticsReducer from './analyticsSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    complaints: complaintsReducer,
    analytics: analyticsReducer,
  },
})