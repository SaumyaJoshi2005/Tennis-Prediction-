import "./PlayerCard.css";
import { formatDate, formatNumber, getPlayerName } from "../../utils/helpers";
import PlayerAvatar from "./PlayerAvatar";

function PlayerCard({ player }) {
    const surfaceElo = [
        { label: "Hard", value: player.hard_elo },
        { label: "Clay", value: player.clay_elo },
        { label: "Grass", value: player.grass_elo },
    ];

    return (
        <article className="player-card">
            <div className="player-card-header">
                <div className="player-card-identity">
                    <PlayerAvatar player={player} size="md" />
                    <div>
                        <h3>{getPlayerName(player)}</h3>
                        <p>{player.country || "Country N/A"}</p>
                    </div>
                </div>

                <span>{player.hand || "Hand N/A"}</span>
            </div>

            <div className="player-stat-grid">
                <div>
                    <span>Overall Elo</span>
                    <strong>{formatNumber(player.elo, 1)}</strong>
                </div>
                <div>
                    <span>Current Form</span>
                    <strong>{formatNumber(player.recent_form, 2)}</strong>
                </div>
                <div>
                    <span>Recent Matches</span>
                    <strong>{formatNumber(player.matches_last_7d)}</strong>
                </div>
                <div>
                    <span>Birth Date</span>
                    <strong>{formatDate(player.birth_date)}</strong>
                </div>
            </div>

            <div className="surface-elo-list">
                {surfaceElo.map((surface) => (
                    <div key={surface.label}>
                        <span>{surface.label}</span>
                        <strong>{formatNumber(surface.value, 1)}</strong>
                    </div>
                ))}
            </div>
        </article>
    );
}

export default PlayerCard;
