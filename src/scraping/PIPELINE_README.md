# Roland Garros Scraping Pipeline

Complete automated pipeline for scraping Roland Garros draws and match results, managing player data, and injecting fixtures into the prediction model database.

---

## 📋 Overview

The pipeline consists of 4 modular components orchestrated by a main controller:

```
┌─────────────────────────────────────────────────────────────┐
│          Pipeline Orchestrator (CLI Interface)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────────┐  ┌────────────┐  ┌──────────────┐
    │ Draw       │  │ Player ATP │  │ Results      │
    │ Scraper    │  │ Fetcher    │  │ Updater      │
    │ (24hr buf) │  │ (Fuzzy+DB) │  │ (Auto-close) │
    └────────────┘  └────────────┘  └──────────────┘
        │              │                  │
        └──────────────┴──────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
    ┌─────────────────┐         ┌──────────────┐
    │ Fixture Table   │         │ PlayerState  │
    │ (new matches)   │         │ (live stats) │
    └─────────────────┘         └──────────────┘
```

---

## 🔧 Components

### 1. **atp_player_fetcher.py**
Manages player registration and live stat updates from ATP API.

**Features:**
- Fuzzy name matching (80% threshold) to prevent duplicates
- ATP API integration for player data enrichment
- Automatic PlayerState initialization for new players
- Live stat updates (Elo, recent form, surface stats, activity metrics)

**Key Functions:**
- `process_player()` - Register/update player in database
- `find_player_in_db()` - Fuzzy search existing players
- `fetch_player_from_atp()` - Query ATP API
- `update_player_state()` - Update live statistics

### 2. **rg_draw_scraper.py**
Scrapes Roland Garros draws with intelligent 24-hour buffering.

**Features:**
- 24-hour buffer per round (prevents redundant scraping)
- Local JSON cache for buffer metadata
- Automatic player registration via ATP fetcher
- Multi-round support (First through Final)

**Key Functions:**
- `scrape_round()` - Scrape specific round with buffer check
- `scrape_all_rounds()` - Scrape all rounds
- `should_scrape()` - Check 24hr buffer status
- `create_fixture()` - Insert match into database

**Cache File:** `scrape_metadata.json`
```json
{
  "first": {
    "last_scraped": "2026-06-09T14:30:00",
    "fixture_count": 128
  }
}
```

### 3. **match_results_updater.py**
Fetches completed match results and updates fixtures.

**Features:**
- Result scraping from RG website
- Automatic fixture status updates (UPCOMING → COMPLETED)
- MatchFeatures population for completed matches
- Per-round result tracking

**Key Functions:**
- `update_round_results()` - Update results for specific round
- `update_all_rounds()` - Update all round results
- `find_fixture_by_players()` - Match result to fixture
- `update_fixture_with_result()` - Mark winner and close fixture

### 4. **pipeline_orchestrator.py**
Master orchestrator with CLI interface.

**Features:**
- Three execution modes (full, scrape-only, results-only)
- Force-mode override for buffer windows
- Comprehensive logging to file and console
- Statistics tracking and reporting

**Execution Modes:**
```bash
# Full pipeline (draws + results)
python pipeline_orchestrator.py --mode full

# Scrape draws only
python pipeline_orchestrator.py --mode scrape

# Update results only
python pipeline_orchestrator.py --mode results

# Target specific round
python pipeline_orchestrator.py --mode scrape --round third

# Force execution (skip 24hr buffer)
python pipeline_orchestrator.py --force
```

---

## 🚀 Usage

### Quick Start

```bash
# Complete pipeline execution
cd src/scraping
python pipeline_orchestrator.py

# With options
python pipeline_orchestrator.py --mode full --force --log-level INFO
```

### Programmatic Usage

```python
from pipeline_orchestrator import RGPipelineOrchestrator

# Create orchestrator
orchestrator = RGPipelineOrchestrator(force=False)

# Run complete pipeline
result = orchestrator.run_complete_pipeline()

# Or individual steps
draw_result = orchestrator.run_scrape_only()
result_update = orchestrator.run_results_only()
```

### Scheduled Execution (e.g., Daily)

```bash
# Add to crontab for daily 10am execution
0 10 * * * cd /path/to/prediction_model/src/scraping && python pipeline_orchestrator.py >> /var/log/rg_pipeline.log 2>&1
```

---

## 📊 Database Integration

### Fixture Table Updates
```
Status Flow: (none) → UPCOMING → IN_PROGRESS → COMPLETED
```

### PlayerState Updates
Live statistics synchronized with ATP API:
- `elo` - Current ATP ranking Elo
- `clay_elo`, `hard_elo`, `grass_elo` - Surface-specific ratings
- `recent_form` - Last 5 matches win rate
- `clay_winrate`, `hard_winrate`, `grass_winrate` - Surface win rates
- `matches_last_7d` - Activity indicator
- `days_since_last_match` - Rest/fatigue indicator
- `total_matches` - Career match count
- `last_match_date` - Most recent match date

### Buffer Logic
24-hour buffer tracked per round in `scrape_metadata.json`:
- First scrape: executes immediately
- Next 23:59 hours: skipped (unless `--force`)
- After 24 hours: executes and resets timer

---

## ⚠️ Important Notes

1. **Duplicate Prevention:**
   - Fuzzy matching prevents duplicate player entries
   - Threshold: 80% name similarity
   - Exact match in database prioritized

2. **ATP API:**
   - Free API with rate limiting
   - Graceful fallback if temporarily unavailable
   - Players still registered with basic info

3. **Error Handling:**
   - Network errors logged but non-blocking
   - Database integrity constraints respected
   - Partial success scenarios handled gracefully

4. **Logging:**
   - File log: `rg_pipeline.log`
   - Console output in real-time
   - Adjustable verbosity: DEBUG, INFO, WARNING, ERROR

---

## 🔄 Pipeline Flow Example

**Day 1 - First Round Available:**
```
1. Scraper checks cache → No prior scrape → EXECUTE
2. Fetches RG HTML → 128 matches found
3. For each match:
   - Extract player names
   - Check/register players (ATP API for new)
   - Create Fixture entry
4. Update cache: first round → 2026-06-09T10:00:00
5. Results: 128 fixtures created

Output: "First Round: Created 128, Failed 0"
```

**Day 2 - Buffer Active (< 24hrs):**
```
1. Scraper checks cache → 14:30:00 elapsed → SKIP
2. Log: "24hr buffer active for first, skipping scrape"
3. No changes to database

Output: "First Round: Created 0, Failed 0"
```

**Day 2 - After Results Available:**
```
1. Results updater runs (independent of buffer)
2. Fetches completed match data
3. Updates 64 Fixture entries (first round winners)
4. Updates MatchFeatures for model training

Output: "First Round: Updated 64, Failed 0"
```

---

## 📝 Configuration

All configuration is embedded in module constants:

- **ATP API:** `ATP_API_BASE`, `FUZZY_MATCH_THRESHOLD`
- **RG URLs:** `RG_ROUND_URLS` dictionary
- **Buffer:** `scrape_metadata.json`, 24-hour timer
- **Database:** Uses app.db connections

To modify settings, edit the module constants directly.

---

## 🐛 Troubleshooting

### Players not registering
- Check ATP API connectivity
- Verify name format (FirstName LastName)
- Check database player_id auto-increment

### Fixtures not found
- Verify player names match exactly between RG and database
- Check Round names against RG_ROUND_URLS
- Review logs for fuzzy match scores

### 24hr buffer not working
- Check `scrape_metadata.json` permissions
- Verify `last_scraped` timestamp format (ISO 8601)
- Clear cache if corrupted

### ATP API errors
- Expected occasionally (rate limiting)
- Gracefully falls back to basic player info
- Check network connectivity

---

## 📊 Logging Output Example

```
2026-06-09 10:00:01 - ORCHESTRATOR - INFO - Starting Complete RG Pipeline Execution
2026-06-09 10:00:01 - RG_SCRAPER - INFO - Starting scrape for round: first
2026-06-09 10:00:03 - ATP_FETCHER - INFO - Player found in database: Novak Djokovic
2026-06-09 10:00:03 - ATP_FETCHER - INFO - New player registered: Jannik Sinner
2026-06-09 10:00:05 - RG_SCRAPER - INFO - Created fixture 12345: 45 vs 67
2026-06-09 10:00:45 - ORCHESTRATOR - INFO - PIPELINE EXECUTION SUMMARY
2026-06-09 10:00:45 - ORCHESTRATOR - INFO - Fixtures Created: 128
2026-06-09 10:00:45 - ORCHESTRATOR - INFO - New Players: 12
```

---

## 🔐 Security Notes

- No sensitive credentials stored in code
- Uses environment variables for database connections (via app.db.session)
- ATP API calls use standard User-Agent headers
- No player data is cached locally beyond database

---

## 📌 Future Enhancements

- [ ] Webhook support for real-time updates
- [ ] Email notifications for pipeline failures
- [ ] Dashboard for pipeline status
- [ ] Retry logic with exponential backoff
- [ ] Database transaction batching for performance
- [ ] Caching layer for ATP API responses

---

**Created:** June 9, 2026  
**Author:** AUM  
**Status:** Production Ready
