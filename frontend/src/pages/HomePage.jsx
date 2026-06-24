import './HomePage.css'

export default function HomePage() {
  return (
    <div className="home-page">
      <h1>Tennis Match Prediction Model</h1>
      
      <div className="hero">
        <p>Advanced machine learning predictions for professional tennis matches</p>
      </div>

      <div className="features">
        <div className="feature-card">
          <h3>Live Predictions</h3>
          <p>Get real-time match predictions with confidence scores</p>
        </div>
        
        <div className="feature-card">
          <h3>Player Analytics</h3>
          <p>Explore detailed player statistics and performance metrics</p>
        </div>
        
        <div className="feature-card">
          <h3>Tournament Fixtures</h3>
          <p>View upcoming matches and historical results</p>
        </div>
      </div>

      <div className="cta">
        <a href="/predictions" className="btn btn-primary">Get Started</a>
      </div>
    </div>
  )
}
