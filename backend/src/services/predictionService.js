import pool from "../config/db.js";

export async function getPredictions() {

  const result = await pool.query(`
    SELECT
      f.fixture_id,
      f.tournament,
      f.round,
      f.surface,
      f.match_date,

      pa.player_name AS player_a,
      pb.player_name AS player_b,

      f.winner_predicted,
      f.player_a_win_probability

    FROM fixtures f

    JOIN players pa
      ON pa.player_id = f.player_a_id

    JOIN players pb
      ON pb.player_id = f.player_b_id

    WHERE f.status = 'PREDICTED'

    ORDER BY f.match_date
  `);

  return result.rows;
}