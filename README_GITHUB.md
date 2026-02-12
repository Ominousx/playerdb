# Valorant Player Database & Tic-Tac-Toe Game 🎮

A comprehensive scraper and database builder for Valorant esports players, designed to power a Valorant Tic-Tac-Toe game (similar to Immaculate Grid for football).

## 🌍 Features

- **Global Player Scraper**: Scrapes all 6 regions from Liquipedia (4,700+ players)
- **Career History Database**: Full career timelines with team stints and transitions
- **Tier 1 Filter**: Identifies players with top-tier team experience
- **Grid Generator**: Creates valid Tic-Tac-Toe game grids with multiple criteria types
- **Analytics Tools**: Career analysis, player statistics, and more

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install requests beautifulsoup4 lxml pandas openpyxl
```

### 2. Scrape Player Data

```bash
python3 global_valorant_scraper.py
```

Choose regions and whether to fetch detailed career history.

**Test mode**: Scrapes 10 players per region (~3 min)  
**Full mode**: Scrapes all players (~6-8 hours)

### 3. Build Database

```bash
python3 career_database_builder.py
```

Converts JSON career data into structured database tables.

### 4. Generate Game Grids

```bash
python3 valorant_grid_generator.py
```

Creates valid 3x3 Tic-Tac-Toe grids for gameplay.

## 📊 Database Structure

### Career Stints Table
One row per team stint with dates, duration, status

### Team Transitions Table
Player movements from team to team

### Player Statistics Table
Aggregated career stats per player

## 🎮 Tic-Tac-Toe Game Criteria

Grids use 4 types of criteria:
- **Teams**: Fnatic, Team Liquid, Sentinels, etc.
- **Countries**: France, Spain, Turkey, etc.
- **Tier 1 Experience**: Played for VCT franchised teams
- **Career Length**: 5+ teams in career

### Example Grid

```
              Fnatic    │  🌍 France    │  🏆 Tier 1 XP
    ──────────────────────┼───────────────┼────────────────
Team Liquid │  8 answers│  12 answers  │  15 answers   │
    ──────────────────────┼───────────────┼────────────────
📊 5+ Teams │ 15 answers│  20 answers  │  25 answers   │
    ──────────────────────┼───────────────┼────────────────
🌍 Spain    │  6 answers│  18 answers  │  10 answers   │
```

## 🛠️ Tools Included

### Core Scripts

- `global_valorant_scraper.py` - Scrapes all regions from Liquipedia
- `career_database_builder.py` - Builds structured database from JSON
- `tier1_filter.py` - Filters players with Tier 1 experience
- `valorant_grid_generator.py` - Generates game grids

### Analysis Tools

- `career_analyzer.py` - Analyze career patterns and statistics

## 📁 Data Sources

All data scraped from [Liquipedia Valorant](https://liquipedia.net/valorant/)

### Regions Covered
- Europe (~1,600 players)
- CIS (~400 players)
- Americas (~1,200 players)
- Asia (~1,000 players)
- Oceania (~300 players)
- Africa & Middle East (~200 players)

**Total**: 4,700+ professional players

## 🎯 Use Cases

- **Esports Analytics**: Track player careers and team transitions
- **Scouting**: Identify free agents with Tier 1 experience
- **Game Development**: Power Valorant trivia games
- **Data Visualization**: Create dashboards and visualizations
- **Research**: Study esports career patterns

## ⚙️ Configuration

### Tier 1 Teams

Tier 1 classification includes:
- VCT International League teams (Americas, EMEA, Pacific, China)
- Historic top-tier organizations
- 70+ teams total

Edit `tier1_filter.py` to customize the Tier 1 team list.

### Rate Limiting

Scraper uses 2-second delays between requests to respect Liquipedia's servers. Do not modify without considering server load.

## 📊 Output Files

### From Scraper
- `global_valorant_players_YYYYMMDD_HHMMSS.xlsx` - Raw scraped data

### From Database Builder
- `career_database_*_stints.csv` - All team stints
- `career_database_*_transitions.csv` - Team-to-team moves
- `career_database_*_player_stats.csv` - Player statistics
- `career_database_*_complete.xlsx` - All tables in one file

### From Grid Generator
- `valorant_grid_YYYYMMDD_HHMMSS.json` - Game grid data

## 🔄 Updating Data

Re-run the scraper periodically to get latest roster moves:
- **Weekly**: For current season tracking
- **Monthly**: For general updates
- **Quarterly**: Minimal maintenance

## 📝 License

This project is for educational and personal use. All player data belongs to Liquipedia and its contributors.

## 🙏 Credits

- Data source: [Liquipedia Valorant](https://liquipedia.net/valorant/)
- Built for Valorant esports analytics and game development

## 🐺 Author

Built by Sushant for the Wolves esports organization and Valorant community.

---

## 🚨 Important Notes

1. **Respect Rate Limits**: 2-second delay between requests
2. **Data Size**: Full global scrape creates ~5MB of data
3. **Time**: Full scrape takes 6-8 hours (run overnight)
4. **Updates**: Re-scrape when you need fresh data

## 💡 Future Enhancements

- [ ] Web interface for Tic-Tac-Toe game
- [ ] Daily challenge system
- [ ] Leaderboards and scoring
- [ ] More grid criteria (roles, regions, awards)
- [ ] API for game integration
- [ ] Real-time data updates

---

**Star ⭐ this repo if you find it useful!**
