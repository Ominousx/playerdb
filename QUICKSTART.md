# Quick Start Guide - Liquipedia Valorant Scraper

## 🚀 Get Started in 60 Seconds

### Step 1: Install Dependencies
```bash
pip install requests beautifulsoup4 lxml pandas openpyxl --break-system-packages
```

### Step 2: Choose Your Use Case

#### A) Quick scrape of ALL European players (basic info - FAST ~1 minute)
```bash
python liquipedia_scraper.py
# Choose option 1
```

#### B) Interactive scraper with filters (RECOMMENDED)
```bash
python advanced_liquipedia_scraper.py
```
Then follow the prompts to filter by country, status, etc.

#### C) Run example queries
```bash
python examples.py
```

---

## 🎯 Common Use Cases for Esports Analysts

### 1. Scout Active French Players
```bash
python examples.py
# Choose option 2
```
**Output**: `active_french_players.csv` with all active French players

### 2. Find Free Agents
```bash
python examples.py
# Choose option 3
```
**Output**: `free_agents.csv` with players not on teams

### 3. Get Team Rosters
```bash
python examples.py
# Choose option 4
```
**Output**: `team_rosters.csv` with current team compositions

---

## 📊 What Data Do You Get?

### Basic Scrape (Fast)
- Player IGN/ID
- Real Name
- Country
- Current Team
- Status (Active/Inactive/Retired)
- Links

### Detailed Scrape (Slow but Rich)
All of the above PLUS:
- Career history (all previous teams)
- Roles played
- Birth date / Age
- Number of teams played for
- Social media

---

## ⚡ Performance Guide

| Task | Time | Command |
|------|------|---------|
| All players (basic) | 1-2 min | `liquipedia_scraper.py` → option 1 |
| French players (basic) | 30 sec | `examples.py` → option 2 |
| 50 players (detailed) | 2-3 min | `advanced_liquipedia_scraper.py` + max_players=50 |
| All players (detailed) | 4-6 hours | `advanced_liquipedia_scraper.py` + get_details=yes |

---

## 🔧 Programmatic Usage

```python
from advanced_liquipedia_scraper import AdvancedLiquipediaScraper

scraper = AdvancedLiquipediaScraper()

# Get active French and Spanish players
df = scraper.scrape_with_filters(
    countries=['France', 'Spain'],
    status=['Active'],
    get_details=False
)

# Save
df.to_csv('french_spanish_active.csv', index=False)
```

---

## 🎮 For Your Wolves Team Analysis

### Scouting Pipeline
1. **Identify regions**: Run with countries filter
2. **Find free agents**: Filter by empty team + active status
3. **Deep dive**: Get detailed career history for shortlist
4. **Track changes**: Re-run weekly to monitor roster moves

### Example Workflow
```python
# 1. Get all active EMEA players
df = scraper.scrape_with_filters(
    countries=['France', 'Germany', 'UK', 'Spain', 'Poland'],
    status=['Active']
)

# 2. Filter to free agents
free_agents = df[df['current_team'] == '']

# 3. Save for review
free_agents.to_csv('potential_recruits.csv', index=False)

# 4. Get detailed history for top candidates
# (manually identify player_ids from CSV, then run detailed scrape on those)
```

---

## ⚠️ Important Notes

1. **Rate Limiting**: Scraper waits 1-2 seconds between requests
2. **Checkpoints**: Detailed scrapes save progress every 10 players
3. **Resume**: If interrupted, run again - it will resume from checkpoint
4. **Respect**: Don't run multiple scrapers at once

---

## 🆘 Troubleshooting

**"Connection Error"**: Check internet, wait a few minutes, try again

**"Empty DataFrame"**: Your filters were too restrictive, try broader search

**Takes too long**: Use filters to narrow scope, or use basic scrape first

---

## 📁 Output Files

All files are saved with timestamp: `valorant_players_YYYYMMDD_HHMMSS.csv`

Example outputs:
- `active_french_players.csv`
- `free_agents.csv`
- `team_rosters.csv`
- `country_analysis.csv`
- `valorant_players_20250203_123456.csv`

---

## 🔥 Pro Tips

1. **Start with basic scrape** to see all data, then do targeted detailed scrapes
2. **Use country filters** to focus on your recruitment regions
3. **Run weekly** to track roster changes and new free agents
4. **Export to Excel** for easier filtering and analysis in your workflow
5. **Check player_page_url** in CSV to manually verify promising players

---

## Next Steps

1. Run `examples.py` to see the scraper in action
2. Modify `examples.py` for your specific needs
3. Integrate into your weekly scouting workflow
4. Share CSV outputs with your Wolves coaching staff

Happy scouting! 🐺
