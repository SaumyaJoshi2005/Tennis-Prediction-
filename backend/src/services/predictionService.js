import fs from "node:fs";
import pool from "../config/db.js";
import { getFixtures } from "./fixtureService.js";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ACTIVE_STATUSES = [
  "PENDING",
  "SCHEDULED",
  "UPCOMING",
  "IN_PROGRESS",
  "LIVE",
  "PREDICTED",
];

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "../../..");
const predictScript = path.join(projectRoot, "src", "inference", "predict_fixture_batch.py");

if (!fs.existsSync(predictScript)) {
  console.error(
    "Prediction script not found at:",
    predictScript
  );
}

function runPythonBatchPrediction(fixtures) {
  return new Promise((resolve) => {
    if (fixtures.length === 0) {
      resolve(new Map());
      return;
    }

    const pythonBin = process.env.PYTHON_BIN || "python";
    const child = spawn(
      pythonBin,
      [predictScript],
      {
        cwd: projectRoot,
        stdio: ["pipe", "pipe", "pipe"],
      }
    );

    let stdout = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.on("error", (error) => {
      console.error(
        "Python prediction process error:",
        error?.message || error
      );
      resolve(new Map());
    });

    child.on("close", (code) => {
      if (code !== 0) {
        console.error(
          `Python prediction process exited with code ${code}`
        );
        console.error("Python stdout:", stdout);
        resolve(new Map());
        return;
      }

      try {
        const predictions = JSON.parse(stdout);
        resolve(new Map(predictions.map((prediction) => [
          prediction.fixture_id,
          prediction,
        ])));
      } catch (err) {
        console.error(
          "Failed to parse prediction output:",
          err.message,
          "stdout:",
          stdout
        );
        resolve(new Map());
      }
    });

    child.stdin.end(JSON.stringify(fixtures));
  });
}

export async function getPredictions() {

  await pool.query(`
    UPDATE fixtures
    SET status = 'STALE'
    WHERE status = ANY($1)
      AND match_date IS NOT NULL
      AND match_date < CURRENT_DATE
  `, [ACTIVE_STATUSES]);

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
      f.player_a_win_probability,
      'READY' AS prediction_status

    FROM fixtures f

    JOIN players pa
      ON pa.player_id = f.player_a_id

    JOIN players pb
      ON pb.player_id = f.player_b_id

    WHERE f.status = 'PREDICTED'
      AND f.match_date IS NOT NULL
      AND f.match_date >= CURRENT_DATE
      AND f.player_a_id IS NOT NULL
      AND f.player_b_id IS NOT NULL
      AND f.tournament IS NOT NULL
      AND f.round IS NOT NULL
      AND f.surface IS NOT NULL
      AND f.winner_predicted IS NOT NULL
      AND f.player_a_win_probability IS NOT NULL

    ORDER BY f.match_date
  `);

  if (result.rows.length > 0) {
    return result.rows;
  }

  const fixtures = await getFixtures();

  const activeFixtures = fixtures
    .filter((fixture) => !["COMPLETED", "CANCELLED", "STALE"].includes(fixture.status))
    .map((fixture) => ({
      fixture_id: fixture.fixture_id,
      tournament: fixture.tournament,
      round: fixture.round,
      surface: fixture.surface,
      match_date: fixture.match_date,
      scheduled_time: fixture.scheduled_time,
      status: fixture.status,
      status_detail: fixture.status_detail,
      court: fixture.court,
      player_a: fixture.player_a,
      player_b: fixture.player_b,
      player_a_image: fixture.player_a_image,
      player_b_image: fixture.player_b_image,
      player_a_flag: fixture.player_a_flag,
      player_b_flag: fixture.player_b_flag,
      player_a_score: fixture.player_a_score,
      player_b_score: fixture.player_b_score,
      winner_predicted: null,
      player_a_win_probability: null,
      prediction_status: "PENDING_MODEL",
    }));

  const predictionByFixtureId = await runPythonBatchPrediction(activeFixtures);

  return activeFixtures.map((fixture) => {
    const prediction = predictionByFixtureId.get(fixture.fixture_id);

    if (!prediction || prediction.prediction_status !== "READY") {
      return fixture;
    }

    return {
      ...fixture,
      winner_predicted: prediction.winner_predicted,
      player_a_win_probability: prediction.player_a_win_probability,
      prediction_status: prediction.prediction_status,
    };
  });
}
