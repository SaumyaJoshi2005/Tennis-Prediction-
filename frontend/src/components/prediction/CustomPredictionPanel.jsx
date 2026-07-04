import { useMemo, useState } from "react";
import Button from "../common/Button";
import PlayerAvatar from "../player/PlayerAvatar";
import { getPlayerName } from "../../utils/helpers";
import "./CustomPredictionPanel.css";

const surfaces = ["Hard", "Clay", "Grass"];

const featureControls = [
    { id: "eloDiff", label: "Overall Elo edge", min: -300, max: 300, step: 10, weight: 0.009 },
    { id: "surfaceEloDiff", label: "Surface Elo edge", min: -260, max: 260, step: 10, weight: 0.007 },
    { id: "recentFormDiff", label: "Recent form edge", min: -1, max: 1, step: 0.05, weight: 1.2 },
    { id: "surfaceWinrateDiff", label: "Surface winrate edge", min: -1, max: 1, step: 0.05, weight: 1.05 },
    { id: "matchesLast7dDiff", label: "Workload last 7d", min: -5, max: 5, step: 1, weight: -0.16 },
    { id: "daysSinceLastMatchDiff", label: "Rest-day edge", min: -10, max: 10, step: 1, weight: 0.06 },
    { id: "h2hDiff", label: "Head-to-head edge", min: -5, max: 5, step: 1, weight: 0.24 },
];

const initialFeatures = featureControls.reduce((acc, control) => ({ ...acc, [control.id]: 0 }), {});

function sigmoid(value) {
    return 1 / (1 + Math.exp(-value));
}

function CustomPredictionPanel({ players = [] }) {
    const [playerAId, setPlayerAId] = useState("");
    const [playerBId, setPlayerBId] = useState("");
    const [surface, setSurface] = useState("Hard");
    const [features, setFeatures] = useState(initialFeatures);

    const playerA = players.find((player) => String(player.player_id) === playerAId);
    const playerB = players.find((player) => String(player.player_id) === playerBId);

    const scenarioProbability = useMemo(() => {
        const score = featureControls.reduce((total, control) => (
            total + Number(features[control.id]) * control.weight
        ), 0);

        return Math.round(sigmoid(score) * 100);
    }, [features]);

    const handleFeatureChange = (featureId, value) => {
        setFeatures((currentFeatures) => ({
            ...currentFeatures,
            [featureId]: Number(value),
        }));
    };

    return (
        <section className="custom-prediction-panel">
            <div className="panel-copy">
                <p className="section-eyebrow">Custom lab</p>
                <h2>Build a scenario before the model endpoint exists.</h2>
                <p>
                    These controls mirror the backend feature builder: Elo, surface Elo,
                    recent form, surface winrate, workload, rest, and h2h. The output is a
                    local scenario score, not a saved backend prediction.
                </p>
            </div>

            <div className="custom-lab-grid">
                <div className="selector-card">
                    <label>
                        Player A
                        <select value={playerAId} onChange={(event) => setPlayerAId(event.target.value)}>
                            <option value="">Choose player</option>
                            {players.map((player) => (
                                <option key={player.player_id} value={player.player_id}>
                                    {getPlayerName(player)}
                                </option>
                            ))}
                        </select>
                    </label>

                    <label>
                        Player B
                        <select value={playerBId} onChange={(event) => setPlayerBId(event.target.value)}>
                            <option value="">Choose player</option>
                            {players.map((player) => (
                                <option key={player.player_id} value={player.player_id}>
                                    {getPlayerName(player)}
                                </option>
                            ))}
                        </select>
                    </label>

                    <label>
                        Surface
                        <select value={surface} onChange={(event) => setSurface(event.target.value)}>
                            {surfaces.map((surfaceOption) => (
                                <option key={surfaceOption} value={surfaceOption}>
                                    {surfaceOption}
                                </option>
                            ))}
                        </select>
                    </label>
                </div>

                <div className="scenario-card">
                    <div className="scenario-players">
                        <div>
                            <PlayerAvatar player={playerA || getPlayerName(playerA, "Player A")} size="lg" />
                            <strong>{getPlayerName(playerA, "Player A")}</strong>
                        </div>
                        <span>{surface}</span>
                        <div>
                            <PlayerAvatar player={playerB || getPlayerName(playerB, "Player B")} size="lg" />
                            <strong>{getPlayerName(playerB, "Player B")}</strong>
                        </div>
                    </div>

                    <div className="scenario-score">
                        <span>Scenario probability</span>
                        <strong>{scenarioProbability}%</strong>
                        <p>Player A edge after your feature adjustments.</p>
                    </div>
                </div>
            </div>

            <div className="feature-controls">
                {featureControls.map((control) => (
                    <label key={control.id}>
                        <span>
                            {control.label}
                            <strong>{features[control.id]}</strong>
                        </span>
                        <input
                            type="range"
                            min={control.min}
                            max={control.max}
                            step={control.step}
                            value={features[control.id]}
                            onChange={(event) => handleFeatureChange(control.id, event.target.value)}
                        />
                    </label>
                ))}
            </div>

            <Button variant="secondary" onClick={() => setFeatures(initialFeatures)}>
                Reset feature adjustments
            </Button>
        </section>
    );
}

export default CustomPredictionPanel;
