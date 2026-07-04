import { useApi } from '../hooks/useApi'
import { fixtures } from '../services/api'
import EmptyState from '../components/common/EmptyState'
import ErrorMessage from '../components/common/ErrorMessage'
import FixtureCard from '../components/fixture/FixtureCard'
import LoadingSpinner from '../components/common/LoadingSpinner'
import './FixturesPage.css'

export default function FixturesPage() {
  const { data = [], loading, error } = useApi(fixtures.getAll)

  if (loading) return <LoadingSpinner text="Loading fixtures..." />
  if (error) return <ErrorMessage message="Unable to load fixtures." />

  const fixtureList = Array.isArray(data) ? data : []

  if (fixtureList.length === 0) {
    return <EmptyState message="No fixtures available." />
  }

  return (
    <div className="fixtures-page">
      <div className="page-header">
        <div>
          <p className="section-eyebrow">Schedule</p>
          <h1>Fixtures</h1>
        </div>

        <span>{fixtureList.length} matches</span>
      </div>

      <div className="fixtures-list">
          {fixtureList.map((fixture) => (
            <FixtureCard
              key={fixture.fixture_id}
              fixture={fixture}
            />
          ))}
      </div>
    </div>
  )
}
