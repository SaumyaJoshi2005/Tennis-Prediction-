/**
 * Utility function to format probability as percentage
 */
export const formatProbability = (prob) => {
  return (prob * 100).toFixed(2) + '%'
}

/**
 * Utility function to format date
 */
export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Utility function to determine winner prediction
 */
export const getWinnerPrediction = (prob_a, prob_b) => {
  return prob_a > prob_b ? 'Player A' : 'Player B'
}
