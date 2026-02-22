# Valorant Player Database Scraper 🎮

A comprehensive scraper and database builder for Valorant esports players from Liquipedia. Build a complete global database of professional Valorant players with full career histories, team transitions, and statistics.

## 🌍 Features

- **Global Player Scraper**: Scrapes all 6 regions from Liquipedia (4,700+ players)
- **Career History Database**: Full career timelines with team stints and transitions
- **Tier 1 Filter**: Identifies players with top-tier team experience
- **Analytics Tools**: Career analysis, player statistics, and team transition tracking
- **Structured Data**: Export to CSV, Excel, and JSON formats

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

### 3. Filter Tier 1 Players (Optional)

```bash
python3 tier1_filter.py
```

Filters database to only players with Tier 1 team experience.

### 4. Analyze Career Data (Optional)

```bash
python3 career_analyzer.py
```

Explore player statistics, career patterns, and team transitions.

## 📊 Database Structure

### Career Stints Table
One row per team stint with dates, duration, status

### Team Transitions Table
Player movements from team to team

### Player Statistics Table
Aggregated career stats per player

## 🎯 Use Cases

- **Esports Analytics**: Track player careers and team transitions
- **Scouting**: Identify free agents with Tier 1 experience  
- **Data Visualization**: Create dashboards and visualizations
- **Research**: Study esports career patterns and player mobility
- **Team Management**: Analyze roster histories and player backgrounds
- **Database Projects**: Build applications using structured Valorant data

All data scraped from [Liquipedia Valorant](https://liquipedia.net/valorant/)

### Regions Covered
- Europe (~1,600 players)
- CIS (~400 players)
- Americas (~1,200 players)
- Asia (~1,000 players)
- Oceania (~300 players)
- Africa & Middle East (~200 players)

**Total**: 4,700+ professional players

## 🛠️ Tools Included

### Core Scripts

- `global_valorant_scraper.py` - Scrapes all regions from Liquipedia
- `career_database_builder.py` - Builds structured database from JSON
- `tier1_filter.py` - Filters players with Tier 1 experience
- `career_analyzer.py` - Analyze career patterns and statistics

## 📁 Data Sources

## ⚙️ Configuration

Edit `tier1_filter.py` to customize the Tier 1 team list.

### Rate Limiting

Scraper uses 2-second delays between requests to respect Liquipedia's servers. Do not modify without considering server load.

## 📊 Output Files

### From Scraper
- `global_valorant_players_YYYYMMDD_HHMMSS.xlsx` - Raw scraped data with career JSON

### From Database Builder
- `career_database_*_stints.csv` - All team stints (one row per stint)
- `career_database_*_transitions.csv` - Team-to-team moves
- `career_database_*_player_stats.csv` - Aggregated player statistics
- `career_database_*_complete.xlsx` - All tables in one Excel file

### From Tier 1 Filter
- `career_history_*_tier1.xlsx` - Only players with Tier 1 experience
- `career_history_*_tier1_expanded.csv` - Expanded Tier 1 career data

## 🔄 Updating Data

Re-run the scraper periodically to get latest roster moves:
- **Weekly**: For current season tracking
- **Monthly**: For general updates
- **Quarterly**: Minimal maintenance

## 📝 License

This project is for educational and personal use. All player data belongs to Liquipedia and its contributors.

## 🙏 Credits

- Data source: [Liquipedia Valorant](https://liquipedia.net/valorant/)

## 🐺 Author

Built by Ominous for the Wolves esports organization and Valorant community.

---

## 🚨 Important Notes

1. **Respect Rate Limits**: 2-second delay between requests
2. **Data Size**: Full global scrape creates ~5MB of data
3. **Time**: Full scrape takes 6-8 hours (run overnight)
4. **Updates**: Re-scrape when you need fresh data

## 💡 Future Enhancements

- [ ] Support for more regions as Liquipedia expands
- [ ] Automated periodic scraping and updates
- [ ] Player performance statistics integration
- [ ] Team roster timeline visualization
- [ ] Export to SQL databases
- [ ] REST API for data access
- [ ] Integration with VLR.gg for match statistics

---

**Star ⭐ this repo if you find it useful for your Valorant esports projects!**
