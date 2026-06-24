import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import HomePage from './pages/HomePage'
import PredictionsPage from './pages/PredictionsPage'
import PlayersPage from './pages/PlayersPage'
import FixturesPage from './pages/FixturesPage'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <h1>Tennis Match Prediction</h1>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/predictions">Predictions</a></li>
            <li><a href="/fixtures">Fixtures</a></li>
            <li><a href="/players">Players</a></li>
          </ul>
        </nav>

        <main className="container">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/fixtures" element={<FixturesPage />} />
            <Route path="/players" element={<PlayersPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
