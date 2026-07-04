import { Link } from 'react-router-dom'
import CustomPredictionPanel from '../components/prediction/CustomPredictionPanel'
import PlayerAvatar from '../components/player/PlayerAvatar'
import { useApi } from '../hooks/useApi'
import { players, predictions } from '../services/api'
import { formatProbability, getTournamentTier, normalizeProbability, sortByTournamentTier } from '../utils/helpers'
import './HomePage.css'

export default function HomePage() {
  const { data: predictionData = [] } = useApi(predictions.getToday)
  const { data: playerData = [] } = useApi(players.getAll)

  const dailyMatches = Array.isArray(predictionData) ? [...predictionData].sort(sortByTournamentTier) : []
  const playerList = Array.isArray(playerData) ? playerData : []
  const bigFixtures = dailyMatches.slice(0, 5)

  return (
    <div className="home-page">
      <section className="home-hero">
        <div className="home-hero-content">
          <p className="section-eyebrow">Tennis prediction engine v2</p>
          <h1>Daily model picks with a surface-aware prediction lab.</h1>
          <p>
            Grand Slams first, ATP 1000 next, then the rest of the tour. Explore
            official generated predictions or tune player features in the custom lab.
          </p>

          <div className="home-actions">
            <Link to="/predictions" className="btn btn-primary">
              Generated Predictions
            </Link>
            <Link to="/how-it-works" className="btn btn-secondary">
              How Prediction Works
            </Link>
          </div>
        </div>

        {bigFixtures.length > 0 && (
          <aside className="hero-scoreboard">
            <p className="section-eyebrow">Big generated fixtures</p>
            <div className="big-fixture-list">
              {bigFixtures.map((match) => {
                const probability = normalizeProbability(match.player_a_win_probability)
                const tier = getTournamentTier(match.tournament)

                return (
                  <Link
                    to="/predictions"
                    className="big-fixture"
                    key={match.fixture_id || `${match.player_a}-${match.player_b}`}
                  >
                    <div className="big-fixture-tier">
                      <span>{tier.label}</span>
                      <strong>{formatProbability(Math.max(probability, 1 - probability))}</strong>
                    </div>
                    <div className="big-fixture-players">
                      <PlayerAvatar player={match.player_a} size="sm" />
                      <div>
                        <strong>{match.player_a}</strong>
                        <span>vs {match.player_b}</span>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          </aside>
        )}
      </section>

      <CustomPredictionPanel players={playerList} />
    </div>
  )
}
