import FixtureStatusBadge from "./FixtureStatusBadge";
import "./FixtureCard.css";
import { formatDate } from "../../utils/helpers";
import PlayerAvatar from "../player/PlayerAvatar";

function FixtureCard({ fixture }) {
    const playerA = fixture.player_a || (fixture.player_a_id ? `Player #${fixture.player_a_id}` : "Player A");
    const playerB = fixture.player_b || (fixture.player_b_id ? `Player #${fixture.player_b_id}` : "Player B");
    const isCompleted = String(fixture.status || "").toUpperCase() === "COMPLETED";
    const playerAScore = Array.isArray(fixture.player_a_score) ? fixture.player_a_score : [];
    const playerBScore = Array.isArray(fixture.player_b_score) ? fixture.player_b_score : [];
    const hasScore = playerAScore.length > 0 || playerBScore.length > 0;

    return (
        <article className="fixture-card">
            <div className="fixture-card-header">
                <div>
                    <h3>{fixture.tournament || "Tournament TBD"}</h3>
                    <p>{fixture.round || "Round TBD"}</p>
                </div>

                <FixtureStatusBadge status={fixture.status} />
            </div>

            <div className="fixture-matchup">
                <div>
                    <PlayerAvatar
                        player={{ name: playerA, image_url: fixture.player_a_image }}
                        size="md"
                    />
                    <strong>
                        {fixture.player_a_flag && <img src={fixture.player_a_flag} alt="" className="fixture-flag" />}
                        {playerA}
                    </strong>
                </div>
                <span>vs</span>
                <div>
                    <PlayerAvatar
                        player={{ name: playerB, image_url: fixture.player_b_image }}
                        size="md"
                    />
                    <strong>
                        {fixture.player_b_flag && <img src={fixture.player_b_flag} alt="" className="fixture-flag" />}
                        {playerB}
                    </strong>
                </div>
            </div>

            {hasScore && (
                <div className="fixture-scoreboard">
                    <div>
                        <span>{playerA}</span>
                        <strong>{playerAScore.join(" ")}</strong>
                    </div>
                    <div>
                        <span>{playerB}</span>
                        <strong>{playerBScore.join(" ")}</strong>
                    </div>
                </div>
            )}

            <dl className="fixture-meta">
                <div>
                    <dt>Surface</dt>
                    <dd>{fixture.surface || "TBD"}</dd>
                </div>
                <div>
                    <dt>Scheduled</dt>
                    <dd>{formatDate(fixture.match_date || fixture.scheduled_time)}</dd>
                </div>
                <div>
                    <dt>Court</dt>
                    <dd>{fixture.court || "TBD"}</dd>
                </div>
                <div>
                    <dt>Status</dt>
                    <dd>{fixture.status_detail || fixture.status || "TBD"}</dd>
                </div>
            </dl>

            {isCompleted && (
                <div className="fixture-result">
                    <span>Result</span>
                    <strong>{fixture.result_winner || fixture.winner_predicted || "Winner TBD"}</strong>
                    <small>{fixture.result_summary || "Completed"}</small>
                </div>
            )}
        </article>
    );
}

export default FixtureCard;
