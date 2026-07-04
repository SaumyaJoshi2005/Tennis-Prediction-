import axios from 'axios'

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL ||
    'http://localhost:5000/api',

  headers: {
    'Content-Type': 'application/json',
  },

  timeout: 10000,
})

export const predictions = {

  getToday() {

    return api.get(
      '/predictions/today'
    )

  }

}

export const fixtures = {

  getAll() {

    return api.get(
      '/fixtures'
    )

  }

}

export const players = {

  getAll() {

    return api.get(
      '/players'
    )

  }

}

export default api
