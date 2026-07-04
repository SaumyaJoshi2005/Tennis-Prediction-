import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import Layout from './components/layout/Layout'
import { ThemeProvider } from './contexts/ThemeContext'

import HomePage from './pages/HomePage'
import PredictionsPage from './pages/PredictionsPage'
import FixturesPage from './pages/FixturesPage'
import PlayersPage from './pages/PlayersPage'
import HowItWorksPage from './pages/HowItWorksPage'

function App() {

  return (

    <ThemeProvider>

    <Router>

      <Layout>

        <Routes>

          <Route
            path="/"
            element={<HomePage />}
          />

          <Route
            path="/predictions"
            element={<PredictionsPage />}
          />

          <Route
            path="/fixtures"
            element={<FixturesPage />}
          />

          <Route
            path="/players"
            element={<PlayersPage />}
          />

          <Route
            path="/how-it-works"
            element={<HowItWorksPage />}
          />

        </Routes>

      </Layout>

    </Router>

    </ThemeProvider>

  )

}

export default App
