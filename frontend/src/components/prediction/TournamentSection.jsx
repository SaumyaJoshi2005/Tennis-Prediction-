import PredictionCard from "./PredictionCard";
import "./TournamentSection.css";
import { getTournamentTier } from "../../utils/helpers";

function TournamentSection({ tournament, matches }) {
    const tier = getTournamentTier(tournament);

    return (
        <section className="tournament-section">
            <div className="tournament-section-header">
                <div>
                    <p className="section-eyebrow">{tier.label}</p>
                    <h2>{tournament}</h2>
                </div>

                <span>{matches.length} matches</span>
            </div>

            <div className="prediction-grid">
                {matches.map((match) => (
                    <PredictionCard
                        key={match.fixture_id || `${match.player_a}-${match.player_b}`}
                        match={match}
                    />
                ))}
            </div>
        </section>
    );
}

export default TournamentSection;
