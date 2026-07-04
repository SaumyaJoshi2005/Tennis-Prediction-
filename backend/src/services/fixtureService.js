import pool from "../config/db.js";

const SCOREBOARD_URL =
  "https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard";

const ACTIVE_STATUSES = [
  "PENDING",
  "SCHEDULED",
  "UPCOMING",
  "IN_PROGRESS",
  "LIVE",
  "PREDICTED",
];

const VISIBLE_STATUSES = [
  ...ACTIVE_STATUSES,
  "COMPLETED",
];

function parseDate(value) {
  const parsedDate = value ? new Date(value) : null;

  return parsedDate && !Number.isNaN(parsedDate.getTime()) ? parsedDate : null;
}

function toDateOnly(value) {
  const parsedDate = parseDate(value);

  return parsedDate ? parsedDate.toISOString().slice(0, 10) : null;
}

function mapEspnStatus(competition) {
  const statusType = competition?.status?.type || {};
  const state = statusType.state;

  if (state === "in") {
    return "LIVE";
  }

  if (state === "post" || statusType.completed) {
    return "COMPLETED";
  }

  return "SCHEDULED";
}

function getPlayerName(competitor) {
  return (
    competitor?.athlete?.fullName ||
    competitor?.athlete?.displayName ||
    competitor?.displayName ||
    null
  );
}

function getPlayerImage(competitor) {
  return (
    competitor?.athlete?.headshot?.href ||
    competitor?.athlete?.photoUrl ||
    null
  );
}

function getFlag(competitor) {
  return competitor?.athlete?.flag?.href || null;
}

function getLinescore(competitor) {
  return (competitor?.linescores || []).map((line) => line.value);
}

function getResultWinner(competitors) {
  const winner = competitors.find((competitor) => competitor.winner);

  return winner ? getPlayerName(winner) : null;
}

function shouldShowEspnCompetition(competition, now = new Date()) {
  const status = mapEspnStatus(competition);
  const matchDate = parseDate(competition?.date || competition?.startDate);

  if (!matchDate) {
    return status === "LIVE";
  }

  if (status === "LIVE") {
    return true;
  }

  if (status === "COMPLETED") {
    const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    return matchDate >= twentyFourHoursAgo;
  }

  return matchDate >= new Date(now.toISOString().slice(0, 10));
}

function mapEspnCompetition(event, grouping, competition) {
  const competitors = [...(competition.competitors || [])]
    .filter((competitor) => competitor.athlete)
    .sort((a, b) => (a.order || 0) - (b.order || 0));

  if (competitors.length !== 2) {
    return null;
  }

  const [playerA, playerB] = competitors;
  const status = mapEspnStatus(competition);
  const resultWinner = status === "COMPLETED" ? getResultWinner(competitors) : null;

  return {
    fixture_id: `espn-${competition.id}`,
    source: "ESPN",
    source_id: String(competition.id),
    tournament: event.name || event.shortName || "Tournament",
    round:
      competition.round?.displayName ||
      competition.type?.text ||
      grouping.grouping?.displayName ||
      "Round TBD",
    surface: event.name?.toLowerCase().includes("wimbledon") ? "Grass" : null,
    match_date: toDateOnly(competition.date || competition.startDate),
    scheduled_time: competition.date || competition.startDate,
    status,
    status_detail:
      competition.status?.type?.shortDetail ||
      competition.status?.type?.detail ||
      competition.status?.type?.description ||
      status,
    court: competition.venue?.court || competition.venue?.fullName || null,
    player_a: getPlayerName(playerA),
    player_b: getPlayerName(playerB),
    player_a_id: playerA.id ? `espn-${playerA.id}` : null,
    player_b_id: playerB.id ? `espn-${playerB.id}` : null,
    player_a_image: getPlayerImage(playerA),
    player_b_image: getPlayerImage(playerB),
    player_a_flag: getFlag(playerA),
    player_b_flag: getFlag(playerB),
    player_a_score: getLinescore(playerA),
    player_b_score: getLinescore(playerB),
    result_winner: resultWinner,
    result_summary:
      status === "COMPLETED"
        ? competition.notes?.[0]?.text || "Completed"
        : null,
    winner_predicted: null,
    player_a_win_probability: null,
  };
}

async function getEspnFixtures() {
  const response = await fetch(SCOREBOARD_URL);

  if (!response.ok) {
    throw new Error(`ESPN scoreboard failed with ${response.status}`);
  }

  const data = await response.json();
  const fixtures = [];

  for (const event of data.events || []) {
    for (const grouping of event.groupings || []) {
      for (const competition of grouping.competitions || []) {
        if (!shouldShowEspnCompetition(competition)) {
          continue;
        }

        const fixture = mapEspnCompetition(event, grouping, competition);

        if (fixture?.player_a && fixture?.player_b) {
          fixtures.push(fixture);
        }
      }
    }
  }

  return fixtures.sort((a, b) => {
    const statusRank = {
      LIVE: 0,
      IN_PROGRESS: 0,
      COMPLETED: 1,
      PREDICTED: 2,
      SCHEDULED: 3,
    };

    const rankA = statusRank[a.status] ?? 9;
    const rankB = statusRank[b.status] ?? 9;

    if (rankA !== rankB) {
      return rankA - rankB;
    }

    return String(a.scheduled_time || "").localeCompare(String(b.scheduled_time || ""));
  });
}

async function getDbFixtures() {
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
      'DB' AS source,
      NULL AS source_id,
      f.tournament,
      f.round,
      f.surface,
      f.match_date,
      f.match_date AS scheduled_time,
      f.status,
      f.player_a_id,
      f.player_b_id,
      pa.player_name AS player_a,
      pb.player_name AS player_b,
      NULL AS player_a_image,
      NULL AS player_b_image,
      NULL AS player_a_flag,
      NULL AS player_b_flag,
      NULL AS player_a_score,
      NULL AS player_b_score,
      f.winner_predicted,
      f.player_a_win_probability,
      CASE
        WHEN f.status = 'COMPLETED'
          AND f.winner_predicted = 'player_a'
          THEN pa.player_name
        WHEN f.status = 'COMPLETED'
          AND f.winner_predicted = 'player_b'
          THEN pb.player_name
        WHEN f.status = 'COMPLETED'
          THEN f.winner_predicted
        ELSE NULL
      END AS result_winner,
      CASE
        WHEN f.status = 'COMPLETED'
          THEN 'Completed'
        ELSE NULL
      END AS result_summary
    FROM fixtures f
    JOIN players pa
      ON pa.player_id = f.player_a_id
    JOIN players pb
      ON pb.player_id = f.player_b_id
    WHERE f.status = ANY($1)
      AND f.match_date IS NOT NULL
      AND (
        (
          f.status = ANY($2)
          AND f.match_date >= CURRENT_DATE
        )
        OR (
          f.status = 'COMPLETED'
          AND f.match_date >= CURRENT_DATE - INTERVAL '1 day'
        )
      )
      AND f.player_a_id IS NOT NULL
      AND f.player_b_id IS NOT NULL
      AND f.tournament IS NOT NULL
      AND f.round IS NOT NULL
      AND f.surface IS NOT NULL
    ORDER BY
      f.match_date ASC,
      CASE
        WHEN f.status IN ('LIVE', 'IN_PROGRESS') THEN 0
        WHEN f.status = 'COMPLETED' THEN 1
        WHEN f.status IN ('PREDICTED') THEN 2
        ELSE 3
      END,
      f.tournament ASC,
      f.round ASC
  `, [VISIBLE_STATUSES, ACTIVE_STATUSES]);

  return result.rows;
}

export async function getFixtures() {
  const [dbFixtures, espnFixtures] = await Promise.allSettled([
    getDbFixtures(),
    getEspnFixtures(),
  ]);

  const liveFixtures =
    espnFixtures.status === "fulfilled"
      ? espnFixtures.value
      : [];

  if (liveFixtures.length > 0) {
    return liveFixtures;
  }

  if (dbFixtures.status === "fulfilled") {
    return dbFixtures.value;
  }

  throw espnFixtures.reason || dbFixtures.reason || new Error("Unable to load fixtures");
}
