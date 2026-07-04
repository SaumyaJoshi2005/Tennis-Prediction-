import pool from "../config/db.js";

export async function getPlayers() {
  const result = await pool.query(`
    SELECT
      p.player_id,
      p.player_name,
      p.hand,
      p.country,
      p.birth_date,
      p.height_cm,
      ps.elo,
      ps.clay_elo,
      ps.hard_elo,
      ps.grass_elo,
      ps.recent_form,
      ps.matches_last_7d,
      ps.days_since_last_match,
      ps.total_matches,
      ps.last_match_date
    FROM players p
    LEFT JOIN player_state ps
      ON ps.player_id = p.player_id
    ORDER BY p.player_name ASC
  `);

  return result.rows;
}
