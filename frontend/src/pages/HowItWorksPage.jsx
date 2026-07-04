import './HowItWorksPage.css'

const modelSteps = [
  {
    title: 'Fixtures arrive',
    body: 'Tournament fixtures are acquired and stored with surface, round, scheduled date, and player identifiers.',
  },
  {
    title: 'Player state is built',
    body: 'The engine maintains Elo, surface Elo, surface winrate, recent form, workload, and rest-day state for each player.',
  },
  {
    title: 'Feature differences are created',
    body: 'Prediction features are player A minus player B: Elo diff, surface Elo diff, recent form diff, surface winrate diff, workload diff, rest diff, and h2h.',
  },
  {
    title: 'XGBoost scores the matchup',
    body: 'The trained model returns player A win probability. The frontend displays that probability and derives player B probability.',
  },
]

export default function HowItWorksPage() {
  return (
    <div className="how-page">
      <section className="page-header">
        <div>
          <p className="section-eyebrow">Model background</p>
          <h1>How the prediction is actually happening.</h1>
        </div>
        <span>XGBoost pipeline</span>
      </section>

      <section className="model-flow">
        {modelSteps.map((step, index) => (
          <article key={step.title}>
            <span>{String(index + 1).padStart(2, '0')}</span>
            <h2>{step.title}</h2>
            <p>{step.body}</p>
          </article>
        ))}
      </section>

      <section className="feature-board">
        <div>
          <p className="section-eyebrow">Feature builder</p>
          <h2>Core matchup signals</h2>
        </div>

        <ul>
          <li>Overall Elo difference</li>
          <li>Surface Elo difference for Clay, Grass, or Hard</li>
          <li>Recent form difference</li>
          <li>Surface winrate difference</li>
          <li>Matches played in last 7 days difference</li>
          <li>Days since last match difference</li>
          <li>Head-to-head placeholder</li>
        </ul>
      </section>
    </div>
  )
}
