import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const predictions = {
  getPrediction: (playerId1, playerId2) =>
    api.post('/predictions', {
      player_a_id: playerId1,
      player_b_id: playerId2,
    }),
  
  batchPredictions: (matches) =>
    api.post('/predictions/batch', { matches }),
}

export const fixtures = {
  getUpcoming: (limit = 10) =>
    api.get(`/fixtures?limit=${limit}&status=UPCOMING`),
  
  getAll: () =>
    api.get('/fixtures'),
}

export const players = {
  getAll: () =>
    api.get('/players'),
  
  getById: (id) =>
    api.get(`/players/${id}`),
  
  getStats: (id) =>
    api.get(`/players/${id}/stats`),
}

export const matches = {
  getAll: () =>
    api.get('/matches'),
  
  getById: (id) =>
    api.get(`/matches/${id}`),
}

export default api
