import { useEffect, useState } from 'react'

import { predictions } from '../services/api'

import TournamentSection from '../components/prediction/TournamentSection'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorMessage from '../components/common/ErrorMessage'
import EmptyState from '../components/common/EmptyState'
import { getTournamentTier, sortByTournamentTier } from '../utils/helpers'

import './PredictionsPage.css'

function PredictionsPage() {

    const [matches, setMatches] = useState([])

    const [loading, setLoading] = useState(true)

    const [error, setError] = useState(null)

    useEffect(() => {

        async function loadPredictions() {

            try {

                const response =
                    await predictions.getToday()

                setMatches(Array.isArray(response.data) ? response.data : [])

            }

            catch (err) {

                console.error(err)

                setError(
                    'Unable to load predictions.'
                )

            }

            finally {

                setLoading(false)

            }

        }

        loadPredictions()

    }, [])

    if (loading) {

        return <LoadingSpinner />

    }

    if (error) {

        return (

            <ErrorMessage
                message={error}
            />

        )

    }

    if (matches.length === 0) {

        return (

            <EmptyState
                message="No predictions available."
            />

        )

    }

    const groupedMatches = [...matches].sort(sortByTournamentTier).reduce((groups, match) => {
        const tournament = match.tournament || 'Tournament TBD'

        return {
            ...groups,
            [tournament]: [...(groups[tournament] || []), match],
        }
    }, {})

    return (

        <div className="page">

            <div className="page-header">
                <div>
                    <p className="section-eyebrow">Model output</p>
                    <h1>Generated Predictions</h1>
                </div>

                <span>{matches.length} matches</span>
            </div>

            {Object.entries(groupedMatches)
                .sort(([tournamentA], [tournamentB]) => (
                    getTournamentTier(tournamentA).rank - getTournamentTier(tournamentB).rank
                ))
                .map(([tournament, tournamentMatches]) => (
                <TournamentSection
                    key={tournament}
                    tournament={tournament}
                    matches={tournamentMatches}
                />
            ))}

        </div>

    )

}

export default PredictionsPage
