export const normalizeProbability = (value) => {
  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return 0
  }

  return Math.min(Math.max(numericValue > 1 ? numericValue / 100 : numericValue, 0), 1)
}

export const formatProbability = (value, digits = 1) => {
  return `${(normalizeProbability(value) * 100).toFixed(digits)}%`
}

export const formatNumber = (value, digits = 0) => {
  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return 'N/A'
  }

  return numericValue.toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })
}

export const formatDate = (date) => {
  if (!date) {
    return 'TBD'
  }

  const parsedDate = new Date(date)

  if (Number.isNaN(parsedDate.getTime())) {
    return 'TBD'
  }

  return parsedDate.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export const getPlayerName = (player, fallback = 'Unknown player') => {
  return player?.player_name || player?.name || player?.player || fallback
}

const grandSlamTerms = [
  'australian open',
  'roland garros',
  'french open',
  'wimbledon',
  'us open',
]

const mastersTerms = [
  'masters',
  'atp 1000',
  'indian wells',
  'miami',
  'monte carlo',
  'madrid',
  'rome',
  'canada',
  'cincinnati',
  'shanghai',
  'paris',
]

export const getTournamentTier = (tournament = '') => {
  const normalizedTournament = tournament.toLowerCase()

  if (grandSlamTerms.some((term) => normalizedTournament.includes(term))) {
    return { label: 'Grand Slam', rank: 0 }
  }

  if (mastersTerms.some((term) => normalizedTournament.includes(term))) {
    return { label: 'ATP 1000', rank: 1 }
  }

  if (normalizedTournament.includes('500')) {
    return { label: 'ATP 500', rank: 2 }
  }

  if (normalizedTournament.includes('250')) {
    return { label: 'ATP 250', rank: 3 }
  }

  return { label: 'Tour / Challenger', rank: 4 }
}

export const sortByTournamentTier = (matchA, matchB) => {
  const tierA = getTournamentTier(matchA.tournament)
  const tierB = getTournamentTier(matchB.tournament)

  if (tierA.rank !== tierB.rank) {
    return tierA.rank - tierB.rank
  }

  return String(matchA.tournament || '').localeCompare(String(matchB.tournament || ''))
}
