// Backend API Service Layer
// Handles communication with external APIs and database queries

export class ApiService {
  constructor() {
    this.baseUrl = process.env.PYTHON_API_URL || 'http://localhost:8000';
  }

  /**
   * Get match predictions
   */
  async getMatchPredictions(filters = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/api/predictions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters),
      });
      return await response.json();
    } catch (error) {
      console.error('Error fetching predictions:', error);
      throw error;
    }
  }

  /**
   * Get player stats
   */
  async getPlayerStats(playerId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/players/${playerId}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching player stats:', error);
      throw error;
    }
  }

  /**
   * Get upcoming fixtures
   */
  async getUpcomingFixtures(limit = 10) {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/fixtures?limit=${limit}&status=UPCOMING`
      );
      return await response.json();
    } catch (error) {
      console.error('Error fetching fixtures:', error);
      throw error;
    }
  }
}

export default new ApiService();
