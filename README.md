# Liquipedia Valorant Player Database Scraper

A comprehensive Python scraper for extracting player data from Liquipedia's Valorant European player database.

## Features

- ✅ Scrape all European Valorant players
- 🌍 Filter by country
- 📊 Filter by player status (Active/Inactive/Retired)
- 🔍 Get basic info (fast) or detailed info (includes career history)
- 💾 Export to CSV or Excel
- ♻️ Resume capability for interrupted scrapes
- ⏱️ Respectful rate limiting

## Data Collected

### Basic Information (from portal page)
- Player ID/IGN
- Real Name
- Country
- Current Team
- Player Status (Active/Inactive/Retired)
- Player Page URL
- Team Link

### Detailed Information (from individual player pages)
- Role(s)
- Birth Date & Age
- Career History (all previous teams with date ranges)
- Number of teams played for
- Social media links
- Additional biographical info

## Installation

### Required Libraries

```bash
pip install requests beautifulsoup4 lxml pandas openpyxl --break-system-packages
```

## Usage

### Option 1: Basic Scraper (Simple, Good for Quick Data)

```bash
python liquipedia_scraper.py
```

**Modes:**
1. Quick scrape (basic info only - fast) ~1 minute
2. Detailed scrape (includes player pages - slow) ~several hours
3. Sample detailed scrape (first 10 players) ~1 minute

### Option 2: Advanced Scraper (Full Control)

```bash
python advanced_liquipedia_scraper.py
```

Interactive prompts will guide you through:
- Whether to fetch detailed info
- Country filter (e.g., "France, Germany, Spain")
- Status filter (e.g., "Active, Inactive")
- Maximum number of players
- Export format (CSV/Excel/Both)

### Option 3: Programmatic Usage

```python
from advanced_liquipedia_scraper import AdvancedLiquipediaScraper

# Initialize scraper
scraper = AdvancedLiquipediaScraper()

# Example 1: Get all active French players (basic info)
df = scraper.scrape_with_filters(
    countries=['France'],
    status=['Active'],
    get_details=False
)
df.to_csv('active_french_players.csv', index=False)

# Example 2: Get detailed info for first 50 players
df = scraper.scrape_with_filters(
    max_players=50,
    get_details=True
)
df.to_excel('top_50_players_detailed.xlsx', index=False)

# Example 3: Get all German and UK players with teams
df = scraper.scrape_with_filters(
    countries=['Germany', 'United Kingdom'],
    status=['Active'],
    get_details=False
)
# Filter to only players with teams
df_with_teams = df[df['current_team'] != '']
df_with_teams.to_csv('german_uk_players_with_teams.csv', index=False)
```

## Example Queries for Your Team

As a Valorant esports analyst, here are some useful queries:

### 1. Scout Active Players by Country
```python
# Get all active French players
scraper = AdvancedLiquipediaScraper()
df = scraper.scrape_with_filters(
    countries=['France'],
    status=['Active'],
    get_details=False
)
```

### 2. Analyze Free Agents
```python
# Get active players without teams
df = scraper.scrape_with_filters(status=['Active'])
free_agents = df[df['current_team'] == '']
```

### 3. Career History Analysis
```python
# Get detailed career info for specific players
df = scraper.scrape_with_filters(
    countries=['France', 'Spain', 'Germany'],
    get_details=True
)
# Career history is in 'career_history' column as JSON
```

### 4. Team Composition Analysis
```python
# Get all active players and group by team
df = scraper.scrape_with_filters(status=['Active'])
team_counts = df[df['current_team'] != ''].groupby('current_team').size()
```

## Performance Notes

- **Basic scrape (all players)**: ~1-2 minutes
- **Detailed scrape (all players)**: ~4-6 hours (2000+ players × 2 sec delay)
- **Detailed scrape (50 players)**: ~2-3 minutes

The scraper includes:
- Automatic rate limiting (1-2 sec between requests)
- Checkpoint system (saves progress every 10 players)
- Resume capability if interrupted

## File Structure

```
.
├── liquipedia_scraper.py           # Basic scraper with 3 modes
├── advanced_liquipedia_scraper.py   # Advanced scraper with filters
├── README.md                        # This file
└── scraper_checkpoint.json          # Auto-created during detailed scrapes
```

## Important Notes

### Liquipedia Terms of Use
- Be respectful of Liquipedia's servers
- This scraper includes rate limiting (2 seconds between requests)
- For heavy usage, consider contacting Liquipedia
- Do not run multiple scrapers simultaneously

### Data Freshness
- Data is scraped in real-time from Liquipedia
- Player status and teams may change frequently
- Re-run scraper periodically for updates

### Data Quality
- Some players may have incomplete information
- Status detection (Active/Inactive/Retired) is based on table styling
- Career history parsing depends on page structure

## Troubleshooting

### "Connection Error"
- Check your internet connection
- Liquipedia may be temporarily down
- You may have been rate-limited (wait a few minutes)

### "Missing Career History"
- Some player pages don't have team history sections
- This is expected and not an error

### "Checkpoint File Exists"
- From a previous interrupted scrape
- Delete `scraper_checkpoint.json` to start fresh
- Or the scraper will automatically resume

## Data Analysis Examples

After scraping, you can analyze the data:

```python
import pandas as pd

# Load your scraped data
df = pd.read_csv('valorant_players_20250203_123456.csv')

# Analysis 1: Top countries by player count
print(df['country'].value_counts().head(10))

# Analysis 2: Active players per country
active = df[df['status'] == 'Active']
print(active.groupby('country').size().sort_values(ascending=False))

# Analysis 3: Teams with most players
team_sizes = df[df['current_team'] != ''].groupby('current_team').size()
print(team_sizes.sort_values(ascending=False).head(20))

# Analysis 4: Retired players
retired = df[df['status'] == 'Retired']
print(f"Retired players: {len(retired)}")
```

## Contributing to Your Team's Analysis

This data can feed into:
- Scouting reports (player identification by country/status)
- Team composition analysis
- Player career trajectory studies
- Free agent availability tracking
- Regional strength analysis

## License

This scraper is for educational and analytical purposes. All data belongs to Liquipedia and its contributors.

## Contact

For issues or questions about this scraper, please check:
- Liquipedia's terms of use
- Your organization's data usage policies
