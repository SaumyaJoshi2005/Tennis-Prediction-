// src/App.js
// Tennis prediction dashboard wired to the FastAPI backend.

import React, { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

// In local dev, call FastAPI directly. Set REACT_APP_API_URL only when the API
// is hosted somewhere else.
const API_BASE = (process.env.REACT_APP_API_URL || "http://localhost:8000").replace(/\/$/, "");
const DEFAULT_MODEL = "XGBoost";

const THEME_OPTIONS = [
  { value: "rg-clay", label: "RG Clay" },
  { value: "wimbledon", label: "Wimbledon Green" },
  { value: "hard-blue", label: "Hard Court Blue" },
  { value: "night-neon", label: "Night Neon" },
];

function apiUrl(path) {
  return `${API_BASE}${path}`;
}

function todayKey() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

function normalizePlayers(payload) {
  const players = Array.isArray(payload) ? payload : payload?.players || [];

  return players
    .filter(player => player?.name)
    .map(player => ({
      ...player,
      rank: Number(player.rank ?? 9999),
    }))
    .sort((a, b) => a.rank - b.rank || a.name.localeCompare(b.name));
}

function getWinnerFirstName(winner, player1Name, player2Name) {
  const normalizedWinner = String(winner || "").trim();

  if (/^player\s*1$/i.test(normalizedWinner) || /^p1$/i.test(normalizedWinner)) {
    return player1Name?.split(" ")[0] || player1Name || "Player 1";
  }

  if (/^player\s*2$/i.test(normalizedWinner) || /^p2$/i.test(normalizedWinner)) {
    return player2Name?.split(" ")[0] || player2Name || "Player 2";
  }

  return normalizedWinner.split(" ")[0] || normalizedWinner;
}

function PlayerPicker({ label, players, selectedName, search, onSearch, onSelect, loading }) {
  const visiblePlayers = useMemo(() => {
    const query = search.trim().toLowerCase();
    const filtered = query
      ? players.filter(player => player.name.toLowerCase().includes(query))
      : players;

    return filtered.slice(0, 12);
  }, [players, search]);

  const selectedPlayer = players.find(player => player.name === selectedName);

  return (
    <div className="player-picker">
      <label className="block mb-2 text-zinc-300 text-sm">{label}</label>
      <input
        type="text"
        placeholder={loading ? "Loading players..." : "Search player..."}
        value={search}
        onChange={event => onSearch(event.target.value)}
        className="w-full rounded-xl bg-zinc-800 border border-zinc-700 p-3 mb-2"
        disabled={loading}
      />

      {selectedPlayer && (
        <div className="selected-player">
          <span>Selected</span>
          <strong>#{selectedPlayer.rank} {selectedPlayer.name}</strong>
        </div>
      )}

      <div className="player-results" role="listbox" aria-label={`${label} results`}>
        {visiblePlayers.map(player => {
          const active = player.name === selectedName;

          return (
            <button
              key={player.name}
              type="button"
              className={`player-result ${active ? "is-active" : ""}`}
              onClick={() => {
                onSelect(player.name);
                onSearch("");
              }}
            >
              <span>#{player.rank}</span>
              <strong>{player.name}</strong>
            </button>
          );
        })}

        {!loading && visiblePlayers.length === 0 && (
          <div className="player-empty">No players found</div>
        )}
      </div>
    </div>
  );
}

export default function TennisPredictionApp() {
  const [allPlayers, setAllPlayers] = useState([]);
  const [player1Name, setPlayer1Name] = useState("");
  const [player2Name, setPlayer2Name] = useState("");
  const [player1Search, setPlayer1Search] = useState("");
  const [player2Search, setPlayer2Search] = useState("");
  const [surface, setSurface] = useState("Clay");
  const [tourneyLevel, setTourneyLevel] = useState("G");
  const [bestOf, setBestOf] = useState(5);
  const [selectedTheme, setSelectedTheme] = useState("rg-clay");

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingPlayers, setLoadingPlayers] = useState(true);
  const [fixtures, setFixtures] = useState([]);
  const [fixturePredictions, setFixturePredictions] = useState([]);
  const [loadingFixtures, setLoadingFixtures] = useState(false);
  const [predictingFixtures, setPredictingFixtures] = useState(false);
  const [error, setError] = useState(null);

  // Load players directly from the real endpoint. The old hidden /health gate
  // could block the picker even when /players/ itself was working correctly.
  useEffect(() => {
    let cancelled = false;

    async function loadPlayers() {
      setLoadingPlayers(true);
      setError(null);

      try {
        let response = await fetch(apiUrl("/players/"));

        // Accept both FastAPI styles: /players/ and /players.
        if (!response.ok && response.status === 404) {
          response = await fetch(apiUrl("/players"));
        }

        if (!response.ok) {
          throw new Error(`Failed to load players: API returned ${response.status}`);
        }

        const players = normalizePlayers(await response.json());

        if (cancelled) return;

        setAllPlayers(players);
        setPlayer1Name(players[0]?.name || "");
        setPlayer2Name(players[1]?.name || "");
      } catch (event) {
        if (!cancelled) {
          setError(event.message);
          setAllPlayers([]);
        }
      } finally {
        if (!cancelled) {
          setLoadingPlayers(false);
        }
      }
    }

    loadPlayers();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadFixtures() {
      setLoadingFixtures(true);

      try {
        const response = await fetch(apiUrl(`/fixtures/today?match_date=${todayKey()}`));
        if (!response.ok) {
          throw new Error(`Failed to load fixtures: API returned ${response.status}`);
        }

        const data = await response.json();
        if (!cancelled) {
          setFixtures(data);
        }
      } catch (event) {
        if (!cancelled) {
          setError(event.message);
        }
      } finally {
        if (!cancelled) {
          setLoadingFixtures(false);
        }
      }
    }

    loadFixtures();

    return () => {
      cancelled = true;
    };
  }, []);

  const p1Details = allPlayers.find(player => player.name === player1Name);
  const p2Details = allPlayers.find(player => player.name === player2Name);

  const predict = useCallback(async () => {
    if (!player1Name || !player2Name) return;

    if (player1Name === player2Name) {
      setError("Player 1 and Player 2 must be different.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(apiUrl("/predict/"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player1: player1Name,
          player2: player2Name,
          surface,
          tourney_level: tourneyLevel,
          best_of: bestOf,
          model_name: DEFAULT_MODEL,
        }),
      });

      if (!response.ok) {
        const apiError = await response.json().catch(() => ({}));
        throw new Error(apiError.detail || `API error ${response.status}`);
      }

      setResult(await response.json());
    } catch (event) {
      setError(event.message);
    } finally {
      setLoading(false);
    }
  }, [player1Name, player2Name, surface, tourneyLevel, bestOf]);

  const predictTodaysFixtures = useCallback(async () => {
    setPredictingFixtures(true);
    setError(null);

    try {
      const response = await fetch(apiUrl(`/fixtures/today/predictions?match_date=${todayKey()}&model_name=${DEFAULT_MODEL}`));
      if (!response.ok) {
        const apiError = await response.json().catch(() => ({}));
        throw new Error(apiError.detail || `API error ${response.status}`);
      }

      setFixturePredictions(await response.json());
    } catch (event) {
      setError(event.message);
    } finally {
      setPredictingFixtures(false);
    }
  }, []);

  return (
    <div className={`min-h-screen bg-zinc-950 text-white p-6 theme-${selectedTheme}`}>
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="rounded-3xl border border-zinc-800 bg-zinc-900 p-8 shadow-2xl">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-4xl font-bold mb-2">Tennis Prediction Engine</h1>
            </div>

            <label className="theme-picker">
              <span>Theme</span>
              <select value={selectedTheme} onChange={event => setSelectedTheme(event.target.value)}>
                {THEME_OPTIONS.map(theme => (
                  <option key={theme.value} value={theme.value}>
                    {theme.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="rounded-3xl border border-zinc-800 bg-zinc-900 p-6">
          <div className="fixture-header">
            <div>
              <h2 className="text-2xl font-semibold">Today at Roland Garros</h2>
              <p>{loadingFixtures ? "Loading fixtures..." : `${fixtures.length} men's fixtures stored for today`}</p>
            </div>
            <button
              type="button"
              onClick={predictTodaysFixtures}
              disabled={predictingFixtures || loadingFixtures || fixtures.length === 0}
              className="rounded-2xl bg-white text-black font-semibold py-3 px-5 hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {predictingFixtures ? "Predicting..." : "Predict Today's Matches"}
            </button>
          </div>

          <div className="fixture-grid">
            {(fixturePredictions.length > 0 ? fixturePredictions : fixtures).slice(0, 12).map(fixture => (
              <button
                key={fixture.fixture_id}
                type="button"
                className="fixture-card"
                onClick={() => {
                  setPlayer1Name(fixture.player1_name);
                  setPlayer2Name(fixture.player2_name);
                  setSurface("Clay");
                  setTourneyLevel("G");
                  setBestOf(5);
                  setResult(null);
                }}
              >
                <span>R128</span>
                <strong>{fixture.player1_name}</strong>
                <em>vs</em>
                <strong>{fixture.player2_name}</strong>
                {fixture.prediction_available && (
                  <div className="fixture-pick">
                    <div className="text-xs uppercase tracking-wide text-zinc-400">Winner</div>
                    <div className="text-green-400 font-semibold mt-1">
                      {getWinnerFirstName(fixture.predicted_winner, fixture.player1_name, fixture.player2_name)}
                    </div>
                  </div>
                )}
                {fixture.error && <div className="fixture-error">{fixture.error}</div>}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="rounded-3xl border border-zinc-800 bg-zinc-900 p-6 space-y-5">
            <h2 className="text-2xl font-semibold">Match Configuration</h2>

            <PlayerPicker
              label="Player 1"
              players={allPlayers}
              selectedName={player1Name}
              search={player1Search}
              onSearch={setPlayer1Search}
              onSelect={setPlayer1Name}
              loading={loadingPlayers}
            />

            <PlayerPicker
              label="Player 2"
              players={allPlayers}
              selectedName={player2Name}
              search={player2Search}
              onSearch={setPlayer2Search}
              onSelect={setPlayer2Name}
              loading={loadingPlayers}
            />

            <div>
              <label className="block mb-2 text-zinc-300 text-sm">Surface</label>
              <select
                value={surface}
                onChange={event => setSurface(event.target.value)}
                className="w-full rounded-xl bg-zinc-800 border border-zinc-700 p-3"
              >
                <option value="Clay">Clay</option>
                <option value="Hard">Hard</option>
                <option value="Grass">Grass</option>
                <option value="Carpet">Carpet</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block mb-2 text-zinc-300 text-sm">Tournament Level</label>
                <select
                  value={tourneyLevel}
                  onChange={event => setTourneyLevel(event.target.value)}
                  className="w-full rounded-xl bg-zinc-800 border border-zinc-700 p-3"
                >
                  <option value="G">Grand Slam</option>
                  <option value="M">Masters</option>
                  <option value="A">ATP 250/500</option>
                  <option value="D">Davis Cup</option>
                </select>
              </div>

              <div>
                <label className="block mb-2 text-zinc-300 text-sm">Best Of</label>
                <select
                  value={bestOf}
                  onChange={event => setBestOf(Number(event.target.value))}
                  className="w-full rounded-xl bg-zinc-800 border border-zinc-700 p-3"
                >
                  <option value={3}>Best of 3</option>
                  <option value={5}>Best of 5</option>
                </select>
              </div>
            </div>

            <button
              onClick={predict}
              disabled={loading || loadingPlayers || !player1Name || !player2Name}
              className="w-full rounded-2xl bg-white text-black font-semibold py-3 hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? "Predicting..." : "Predict Match"}
            </button>

            {error && (
              <div className="rounded-xl bg-red-950 border border-red-700 p-3 text-red-300 text-sm">
                {error}
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-zinc-800 bg-zinc-900 p-6">
            <h2 className="text-2xl font-semibold mb-5">Match Prediction</h2>

            {!result && !loading && (
              <div className="text-zinc-500 text-center mt-20">
                {loadingPlayers ? "Loading player list..." : "Select two players and click Predict Match"}
              </div>
            )}

            {loading && (
              <div className="text-zinc-400 text-center mt-20 animate-pulse">
                Reading the matchup...
              </div>
            )}

            {result && (
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2 text-lg">
                    <span>{result.player1_name}</span>
                    <span className="font-bold">
                      {Math.round(result.player1_probability * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-zinc-800 rounded-full h-5 overflow-hidden">
                    <div
                      className="bg-white h-5 rounded-full transition-all duration-700"
                      style={{ width: `${result.player1_probability * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2 text-lg">
                    <span>{result.player2_name}</span>
                    <span className="font-bold">
                      {Math.round(result.player2_probability * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-zinc-800 rounded-full h-5 overflow-hidden">
                    <div
                      className="bg-zinc-500 h-5 rounded-full transition-all duration-700"
                      style={{ width: `${result.player2_probability * 100}%` }}
                    />
                  </div>
                </div>

                <div className="rounded-2xl bg-zinc-800 p-4 border border-zinc-700">
                  <div>
                    <div className="text-zinc-400 text-sm">Predicted Winner</div>
                    <div className="text-2xl font-bold mt-2 text-green-400">
                      {getWinnerFirstName(result.predicted_winner, result.player1_name, result.player2_name)}
                    </div>
                  </div>
                </div>

                {(p1Details || p2Details) && (
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { name: result.player1_name, details: p1Details },
                      { name: result.player2_name, details: p2Details },
                    ].map(({ name, details }) => details && (
                      <div key={name} className="rounded-2xl bg-zinc-800 p-4 space-y-1">
                        <div className="font-semibold text-sm mb-2 truncate">{name}</div>
                        <div className="text-xs text-zinc-400">Rank: <span className="text-white">{details.rank}</span></div>
                        <div className="text-xs text-zinc-400">ELO: <span className="text-white">{details.elo?.toFixed(0)}</span></div>
                        <div className="text-xs text-zinc-400">Form: <span className="text-white">{(details.recent_form * 100).toFixed(0)}%</span></div>
                        <div className="text-xs text-zinc-400">Surface W%: <span className="text-white">{(details.surface_winrate * 100).toFixed(0)}%</span></div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
