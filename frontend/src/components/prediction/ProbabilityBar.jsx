import "./ProbabilityBar.css";
import { formatProbability, normalizeProbability } from "../../utils/helpers";

function ProbabilityBar({

    player,

    probability,

    color = "#2ecc71"

}) {

    const normalizedProbability = normalizeProbability(probability);

    return (

        <div className="probability-row">

            <div className="probability-header">

                <span>{player || "Player"}</span>

                <span>

                    {formatProbability(normalizedProbability)}

                </span>

            </div>

            <div className="probability-track">

                <div

                    className="probability-fill"

                    style={{
                        width: `${normalizedProbability * 100}%`,
                        backgroundColor: color
                    }}

                />

            </div>

        </div>

    );

}

export default ProbabilityBar;
