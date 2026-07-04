# RG Pipeline - Quick Reference Guide

## 🎯 Files Created

### Core Modules
1. **atp_player_fetcher.py** - ATP API + fuzzy player matching
2. **rg_draw_scraper.py** - RG draw scraping with 24hr buffer
3. **match_results_updater.py** - Match results scraping & fixture updates
4. **pipeline_orchestrator.py** - Main CLI orchestrator
5. **pipeline_utils.py** - Helper utilities (buffer, validator, stats)

### Configuration & Documentation
- **scrape_metadata.json** - 24hr buffer cache (per-round timestamps)
- **PIPELINE_README.md** - Comprehensive documentation

---

## ⚡ Quick Start

```bash
# Navigate to scraping folder
cd src/scraping

# Run full pipeline
python pipeline_orchestrator.py

# Run with options
python pipeline_orchestrator.py --mode scrape --force --log-level DEBUG
```

---

## 🔌 CLI Commands

```bash
# Full pipeline (draw scrape + results update)
python pipeline_orchestrator.py --mode full

# Scrape draws only
python pipeline_orchestrator.py --mode scrape

# Update results only
python pipeline_orchestrator.py --mode results

# Target specific round
python pipeline_orchestrator.py --mode scrape --round third

# Force skip 24hr buffer
python pipeline_orchestrator.py --force

# Adjust logging
python pipeline_orchestrator.py --log-level DEBUG
```

---

## 📊 Data Flow

```
RG Website HTML
      ↓
Extract Match Data (regex)
      ↓
For Each Match:
  ├─→ Check Player in DB (fuzzy match 80%)
  ├─→ If not found: Query ATP API + Register
  ├─→ Create/Update Player State (live stats)
  └─→ Create Fixture entry
      ↓
Check 24hr Buffer
      ├─→ Within 24hrs: Skip
      └─→ After 24hrs: Update cache + execute
      ↓
[Fixture Table: UPCOMING]
      ↓
Later: Fetch Results
      ├─→ Parse completed matches
      └─→ Update Fixture → COMPLETED
      ↓
[MatchFeatures: Populated for training]
```

---

## 🗄️ Database Tables Modified

### `Fixture` (INSERT + UPDATE)
```
fixture_id (auto)
player_a_id → Player ID (FK)
player_b_id → Player ID (FK)
tournament = "Roland Garros"
round = "first|second|third|..."
surface = "Clay"
match_date = NULL (initially)
prediction = NULL
winner_predicted = "player_a"|"player_b"|NULL
player_a_win_probability = NULL
status = "UPCOMING" → "COMPLETED"
```

### `Player` (INSERT only)
```
player_id (auto)
player_name (from ATP API if available)
hand (ATP)
country (ATP)
birth_date (ATP)
height_cm (ATP)
```

### `PlayerState` (UPDATE)
```
player_id (FK, PK)
elo (↑ from ATP API)
clay_elo, hard_elo, grass_elo (↑)
recent_form (↑)
clay_winrate, hard_winrate, grass_winrate (↑)
matches_last_7d (↑)
days_since_last_match (↑)
total_matches (↑)
last_match_date (↑)
```

### `MatchFeatures` (INSERT for completed matches)
```
match_id (FK to Fixture.fixture_id)
winner_pre_elo, loser_pre_elo
winner_surface_elo, loser_surface_elo
... (7 model features)
```

---

## 🔧 Configuration Points

### ATP API
- **Endpoint:** `https://www.atptour.com/en/players`
- **Fuzzy Match Threshold:** 80%
- **Graceful Fallback:** Register player without ATP data if API fails

### 24-Hour Buffer
- **Location:** `scrape_metadata.json`
- **Per Round:** Independent timers for each round
- **Override:** `--force` flag

### Logging
- **Console:** Real-time output
- **File:** `rg_pipeline.log` (in scraping folder)
- **Levels:** DEBUG, INFO, WARNING, ERROR

---

## 🚨 Error Scenarios & Recovery

| Scenario | Handling |
|----------|----------|
| ATP API timeout | Log warning, register player with basic info |
| Player already exists | Fuzzy match finds it, update stats only |
| Network error | Retry logic (configured in error handler) |
| Database duplicate | Caught by IntegrityError, logged as info |
| Malformed HTML | Regex returns empty list, zero fixtures created |
| Missing fixture for result | Result ignored (fixture not yet scraped) |

---

## 📈 Performance Notes

- **Fuzzy Matching:** O(n) database lookup per player (3500+ players = ~milliseconds)
- **Buffer Check:** O(1) JSON file read
- **ATP API:** Rate limited, ~100 req/min typical
- **Database Commits:** Per-fixture for atomicity (or batch if optimized)

---

## 🔄 Typical Execution Timeline

**Day 1 (10:00 AM) - First Round Available**
```
10:00:00 - Pipeline starts
10:00:01 - Scrape buffer: FIRST ROUND = EXECUTE
10:00:45 - 128 matches found, 3 new players registered
10:01:00 - 128 fixtures created in DB
10:01:15 - Cache updated: first_round timestamp + count
Result: 128 fixtures UPCOMING
```

**Day 2 (11:00 AM) - Buffer Active**
```
11:00:00 - Pipeline starts
11:00:01 - Scrape buffer: FIRST ROUND = SKIP (23hr 59min remaining)
Result: 0 fixtures created (expected)
```

**Day 2 (4:00 PM) - Results Available**
```
16:00:00 - Results updater runs (independent)
16:00:30 - 64 winners identified
16:01:00 - Fixtures updated: UPCOMING → COMPLETED
Result: 64 fixtures COMPLETED, ready for training
```

**Day 3 (10:01 AM) - Buffer Expired**
```
10:01:00 - Scrape buffer: FIRST ROUND = EXECUTE (24h expired)
10:01:45 - 0 matches found (round already finalized)
Result: 0 fixtures created (expected)
```

---

## 🎮 Programmatic Usage

```python
from pipeline_orchestrator import RGPipelineOrchestrator

# Setup
orchestrator = RGPipelineOrchestrator(force=False)

# Run pipeline
result = orchestrator.run_complete_pipeline()

if result['success']:
    print(f"Created: {result['stats']['fixtures_created']}")
    print(f"Updated: {result['stats']['results_updated']}")
else:
    print(f"Error: {result['error']}")
```

---

## 📝 Log Example

```
2026-06-09 10:00:01 - ORCHESTRATOR - INFO - Starting Complete RG Pipeline Execution
2026-06-09 10:00:01 - RG_SCRAPER - INFO - Starting scrape for round: first
2026-06-09 10:00:02 - RG_SCRAPER - INFO - Fetched HTML for round: first
2026-06-09 10:00:03 - RG_SCRAPER - INFO - Extracted 128 matches from HTML
2026-06-09 10:00:03 - ATP_FETCHER - INFO - Player found in database: Novak Djokovic
2026-06-09 10:00:04 - ATP_FETCHER - INFO - New player registered: Jannik Sinner
2026-06-09 10:00:05 - RG_SCRAPER - INFO - Created fixture 12345: 45 vs 67
...
2026-06-09 10:00:45 - ORCHESTRATOR - INFO - PIPELINE EXECUTION SUMMARY
2026-06-09 10:00:45 - ORCHESTRATOR - INFO - Fixtures Created: 128
2026-06-09 10:00:45 - ORCHESTRATOR - INFO - New Players: 3
```

---

## ⚙️ Future Enhancements

- [ ] Webhook support for real-time updates
- [ ] Batch database inserts for performance
- [ ] Caching layer for ATP API responses
- [ ] Email alerts for pipeline failures
- [ ] Dashboard for pipeline status
- [ ] Retry with exponential backoff

---

**Status:** ✅ Production Ready  
**Last Updated:** June 9, 2026  
**Author:** AUM
