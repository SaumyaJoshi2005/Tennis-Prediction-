import { useMemo, useState } from 'react'
import { useApi } from '../hooks/useApi'
import { players } from '../services/api'
import Button from '../components/common/Button'
import EmptyState from '../components/common/EmptyState'
import ErrorMessage from '../components/common/ErrorMessage'
import LoadingSpinner from '../components/common/LoadingSpinner'
import PlayerCard from '../components/player/PlayerCard'
import { getPlayerName } from '../utils/helpers'
import './PlayersPage.css'

const pageSize = 12

export default function PlayersPage() {
  const [query, setQuery] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [page, setPage] = useState(1)
  const { data = [], loading, error } = useApi(players.getAll)

  const playerList = Array.isArray(data) ? data : []

  const filteredPlayers = useMemo(() => {
    return playerList
      .filter((player) => {
        const haystack = [
          getPlayerName(player),
          player.country,
          player.hand,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()

        return haystack.includes(query.trim().toLowerCase())
      })
      .sort((playerA, playerB) => {
        if (sortBy === 'elo') {
          return (Number(playerB.elo) || 0) - (Number(playerA.elo) || 0)
        }

        if (sortBy === 'country') {
          return String(playerA.country || '').localeCompare(String(playerB.country || ''))
        }

        return getPlayerName(playerA).localeCompare(getPlayerName(playerB))
      })
  }, [playerList, query, sortBy])

  const pageCount = Math.max(1, Math.ceil(filteredPlayers.length / pageSize))
  const visiblePlayers = filteredPlayers.slice((page - 1) * pageSize, page * pageSize)

  const handleQueryChange = (event) => {
    setQuery(event.target.value)
    setPage(1)
  }

  const handleSortChange = (event) => {
    setSortBy(event.target.value)
    setPage(1)
  }

  if (loading) return <LoadingSpinner text="Loading players..." />
  if (error) return <ErrorMessage message="Unable to load players." />

  return (
    <div className="players-page">
      <div className="page-header">
        <div>
          <p className="section-eyebrow">Profiles</p>
          <h1>Players</h1>
        </div>

        <span>{filteredPlayers.length} players</span>
      </div>

      <div className="player-toolbar">
        <label>
          <span>Search</span>
          <input
            type="search"
            value={query}
            onChange={handleQueryChange}
            placeholder="Search by player, country, or hand"
          />
        </label>

        <label>
          <span>Sort</span>
          <select value={sortBy} onChange={handleSortChange}>
            <option value="name">Name</option>
            <option value="elo">Overall Elo</option>
            <option value="country">Country</option>
          </select>
        </label>
      </div>

      {visiblePlayers.length === 0 ? (
        <EmptyState message="No players match your filters." />
      ) : (
        <div className="players-grid">
          {visiblePlayers.map((player) => (
            <PlayerCard
              key={player.player_id || getPlayerName(player)}
              player={player}
            />
          ))}
        </div>
      )}

      {pageCount > 1 && (
        <div className="pagination">
          <Button
            variant="secondary"
            disabled={page === 1}
            onClick={() => setPage((currentPage) => Math.max(1, currentPage - 1))}
          >
            Previous
          </Button>

          <span>
            Page {page} of {pageCount}
          </span>

          <Button
            variant="secondary"
            disabled={page === pageCount}
            onClick={() => setPage((currentPage) => Math.min(pageCount, currentPage + 1))}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
