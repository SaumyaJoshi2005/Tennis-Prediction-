import { useApi } from '../hooks/useApi'
import { fixtures } from '../services/api'
import './FixturesPage.css'

export default function FixturesPage() {
  const { data, loading, error } = useApi(() => fixtures.getUpcoming(20))

  if (loading) return <div>Loading fixtures...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div className="fixtures-page">
      <h1>Upcoming Fixtures</h1>

      {data && data.length > 0 ? (
        <div className="fixtures-list">
          {data.map((fixture) => (
            <div key={fixture.fixture_id} className="fixture-card">
              <h3>{fixture.tournament}</h3>
              <p>Round: {fixture.round}</p>
              <p>Match Date: {fixture.match_date || 'TBD'}</p>
              <p>Status: {fixture.status}</p>
            </div>
          ))}
        </div>
      ) : (
        <p>No upcoming fixtures found</p>
      )}
    </div>
  )
}
