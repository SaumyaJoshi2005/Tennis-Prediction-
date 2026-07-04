import ProbabilityBar from "./ProbabilityBar";
import "./PredictionCard.css";
import PlayerAvatar from "../player/PlayerAvatar";
import { formatDate, formatProbability, getTournamentTier, normalizeProbability } from "../../utils/helpers";

function hasUsableProbability(value) {
    return (
        value !== null
        && value !== undefined
        && value !== ""
        && Number.isFinite(Number(value))
    );
}

function PredictionCard({ match }) {
    const hasModelPrediction = hasUsableProbability(match.player_a_win_probability);
    const playerAProbability = normalizeProbability(match.player_a_win_probability);
    const playerBProbability = 1 - playerAProbability;
    const confidence = Math.max(playerAProbability, playerBProbability);
    const tier = getTournamentTier(match.tournament);
    const playerAScore = Array.isArray(match.player_a_score) ? match.player_a_score : [];
    const playerBScore = Array.isArray(match.player_b_score) ? match.player_b_score : [];
    const hasScore = playerAScore.length > 0 || playerBScore.length > 0;
    const matchMeta = [
        match.status_detail || match.status || "Scheduled",
        match.court,
        formatDate(match.match_date),
    ].filter(Boolean).join(" - ");

    return (
        <div className="prediction-card">
            <div className="prediction-header">
                <div>
                    <h3>{match.tournament || "Tournament TBD"}</h3>
                    <span>{match.round || "Round TBD"}</span>
                </div>

                <span className="surface-chip">{match.surface || "Surface TBD"}</span>
            </div>

            <span className="tier-chip">{tier.label}</span>

            <div className="prediction-date">
                {matchMeta}
            </div>

            <div className="matchup">
                <div className="matchup-player">
                    <PlayerAvatar
                        player={{ name: match.player_a || "Player A", image_url: match.player_a_image }}
                        size="lg"
                    />
                    <h2>{match.player_a || "Player A"}</h2>
                </div>

                <p>vs</p>

                <div className="matchup-player">
                    <PlayerAvatar
                        player={{ name: match.player_b || "Player B", image_url: match.player_b_image }}
                        size="lg"
                    />
                    <h2>{match.player_b || "Player B"}</h2>
                </div>
            </div>

            {hasScore && (
                <div className="prediction-scoreboard">
                    <div>
                        <span>{match.player_a || "Player A"}</span>
                        <strong>{playerAScore.join(" ")}</strong>
                    </div>
                    <div>
                        <span>{match.player_b || "Player B"}</span>
                        <strong>{playerBScore.join(" ")}</strong>
                    </div>
                </div>
            )}

            {hasModelPrediction ? (
                <>
                    <ProbabilityBar
                        player={match.player_a || "Player A"}
                        probability={playerAProbability}
                    />

                    <ProbabilityBar
                        player={match.player_b || "Player B"}
                        probability={playerBProbability}
                        color="#1565c0"
                    />
                </>
            ) : (
                <div className="prediction-pending">
                    {match.prediction_status === "PENDING_MODEL"
                        ? "Prediction model is running for this fixture."
                        : match.prediction_status === "MODEL_UNAVAILABLE"
                        ? "Model unavailable for this fixture."
                        : match.prediction_status === "MISSING_PLAYERS"
                        ? "Missing player data for model prediction."
                        : "Model prediction pending for this fixture."}
                </div>
            )}

            <div className="winner-box">
                <span>{hasModelPrediction ? "Prediction" : "Prediction status"}</span>

                <strong>
                    {hasModelPrediction
                        ? match.winner_predicted
                        : match.prediction_status
                        ? match.prediction_status.replace(/_/g, " ")
                        : "Pending model run"}
                </strong>

                <small>
                    {hasModelPrediction
                        ? `${formatProbability(confidence)} confidence`
                        : match.prediction_status === "PENDING_MODEL"
                        ? "Visible from ESPN; model probability not generated yet"
                        : "Model result unavailable for this fixture"}
                </small>
            </div>
        </div>
    );
}

export default PredictionCard;
