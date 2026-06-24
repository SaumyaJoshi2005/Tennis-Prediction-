import { useState, useEffect } from 'react'

/**
 * Custom hook for API calls
 */
export const useApi = (apiCall, dependencies = []) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let isMounted = true

    const fetchData = async () => {
      try {
        setLoading(true)
        const result = await apiCall()
        if (isMounted) {
          setData(result.data)
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Error fetching data')
          setData(null)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      isMounted = false
    }
  }, dependencies)

  return { data, loading, error }
}
