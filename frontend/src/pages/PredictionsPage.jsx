import { useState } from 'react'
import { predictions } from '../services/api'
import './PredictionsPage.css'

export default function PredictionsPage() {
  const [playerId1, setPlayerId1] = useState('')
  const [playerId2, setPlayerId2] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handlePredict = async (e) => {
    e.preventDefault()
    if (!playerId1 || !playerId2) {
      alert('Please enter both player IDs')
      return
    }

    setLoading(true)
    try {
      const response = await predictions.getPrediction(playerId1, playerId2)
      setResult(response.data)
    } catch (error) {
      console.error('Prediction error:', error)
      alert('Error fetching prediction')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="predictions-page">
      <h1>Match Predictions</h1>

      <form onSubmit={handlePredict} className="prediction-form">
        <div className="form-group">
          <label>Player A ID:</label>
          <input
            type="number"
            value={playerId1}
            onChange={(e) => setPlayerId1(e.target.value)}
            placeholder="Enter player ID"
          />
        </div>

        <div className="form-group">
          <label>Player B ID:</label>
          <input
            type="number"
            value={playerId2}
            onChange={(e) => setPlayerId2(e.target.value)}
            placeholder="Enter player ID"
          />
        </div>

        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? 'Predicting...' : 'Get Prediction'}
        </button>
      </form>

      {result && (
        <div className="prediction-result">
          <h2>Prediction Result</h2>
          <div className="result-box">
            <p>Player A Win Probability: {(result.prediction?.player_a_win_probability * 100).toFixed(2)}%</p>
            <p>Player B Win Probability: {(result.prediction?.player_b_win_probability * 100).toFixed(2)}%</p>
            <p>Confidence: {(result.prediction?.confidence * 100).toFixed(2)}%</p>
          </div>
        </div>
      )}
    </div>
  )
}
