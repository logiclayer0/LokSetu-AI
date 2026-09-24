import { useState, useEffect } from 'react'
import { complaintService } from '../services/complaintService'

export const useComplaints = (filters = {}) => {
  const [complaints, setComplaints] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchComplaints = async () => {
    setLoading(true)
    try {
      const data = await complaintService.list(filters)
      setComplaints(data.complaints || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComplaints()
  }, [])

  return { complaints, loading, error, refetch: fetchComplaints }
}