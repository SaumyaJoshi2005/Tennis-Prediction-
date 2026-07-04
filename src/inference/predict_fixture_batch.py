import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.inference.predict_players import predict_players


def predict_fixture(fixture):
    player_a = fixture.get("player_a")
    player_b = fixture.get("player_b")
    surface = fixture.get("surface") or "Hard"

    if not player_a or not player_b:
        return {
            "fixture_id": fixture.get("fixture_id"),
            "prediction_status": "MISSING_PLAYERS",
            "error": "Both player names are required",
        }

    try:
        probability = predict_players(player_a, player_b, surface)

        return {
            "fixture_id": fixture.get("fixture_id"),
            "player_a_win_probability": probability,
            "winner_predicted": player_a if probability >= 0.5 else player_b,
            "prediction_status": "READY",
        }
    except Exception as exc:
        return {
            "fixture_id": fixture.get("fixture_id"),
            "player_a_win_probability": None,
            "winner_predicted": None,
            "prediction_status": "MODEL_UNAVAILABLE",
            "error": str(exc),
        }


def main():
    payload = json.loads(sys.stdin.read() or "[]")
    if isinstance(payload, dict):
        payload = [payload]
    results = [predict_fixture(fixture) for fixture in payload]
    print(json.dumps(results))


if __name__ == "__main__":
    main()
