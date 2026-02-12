"""
Liquipedia Valorant European Player Database Scraper
Scrapes player information from Liquipedia including:
- Player ID/IGN
- Real Name
- Current Team
- Country
- Career History
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict
import re

class LiquipediaValorantScraper:
    def __init__(self):
        self.base_url = "https://liquipedia.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch and parse webpage content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(1)  # Be respectful to the server
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def scrape_europe_portal(self) -> List[Dict]:
        """Scrape the main European player portal"""
        url = f"{self.base_url}/valorant/Portal:Players/Europe"
        soup = self.get_page_content(url)
        
        if not soup:
            return []
        
        players = []
        
        # Find all player tables on the page
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this is a player table (has specific headers)
            headers = table.find_all('th')
            header_texts = [h.get_text(strip=True) for h in headers]
            
            # Look for player tables (ID, Real Name, Team, Links)
            if 'ID' in header_texts and 'Real Name' in header_texts:
                # Get the country from the table caption or preceding heading
                country = self._get_country_from_table(table)
                
                # Parse all rows in the table
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    player_data = self._parse_player_row(row, country)
                    if player_data:
                        players.append(player_data)
        
        return players
    
    def _get_country_from_table(self, table) -> str:
        """Extract country name from the table context"""
        # Look for the country heading before this table
        prev_element = table.find_previous(['h3', 'h4'])
        if prev_element:
            # Remove flag icons and get clean country name
            country_text = prev_element.get_text(strip=True)
            # Remove any leading/trailing whitespace and special chars
            country_text = re.sub(r'^\W+', '', country_text)
            return country_text
        return "Unknown"
    
    def _parse_player_row(self, row, country: str) -> Dict:
        """Parse a single player row from the table"""
        try:
            cells = row.find_all('td')
            if len(cells) < 3:
                return None
            
            # Extract player ID/IGN
            player_id_cell = cells[0]
            player_id = player_id_cell.get_text(strip=True)
            
            # Try to get the player page link
            player_link_tag = player_id_cell.find('a')
            player_page_url = None
            if player_link_tag and player_link_tag.get('href'):
                player_page_url = self.base_url + player_link_tag.get('href')
            
            # Extract real name
            real_name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            
            # Extract current team
            team_cell = cells[2] if len(cells) > 2 else None
            current_team = ""
            team_link = None
            
            if team_cell:
                current_team = team_cell.get_text(strip=True)
                team_link_tag = team_cell.find('a')
                if team_link_tag and team_link_tag.get('href'):
                    team_link = self.base_url + team_link_tag.get('href')
            
            # Check if player is retired/inactive based on row styling
            status = "Active"
            row_style = row.get('style', '')
            row_class = ' '.join(row.get('class', []))
            
            if 'gray' in row_style or 'gray' in row_class:
                status = "Retired"
            elif 'blue' in row_style or 'blue' in row_class:
                status = "Inactive"
            
            player_data = {
                'player_id': player_id,
                'real_name': real_name,
                'country': country,
                'current_team': current_team,
                'status': status,
                'player_page_url': player_page_url,
                'team_link': team_link
            }
            
            return player_data
            
        except Exception as e:
            print(f"Error parsing row: {e}")
            return None
    
    def get_player_details(self, player_url: str) -> Dict:
        """Scrape detailed information from a player's individual page"""
        soup = self.get_page_content(player_url)
        
        if not soup:
            return {}
        
        details = {}
        
        # Look for the infobox with player information
        infobox = soup.find('div', class_='infobox-wrapper')
        
        if infobox:
            # Extract various details from the infobox
            # Birth date, nationality, role, etc.
            for row in infobox.find_all('div', class_='infobox-cell-2'):
                label_div = row.find('div', class_='infobox-header')
                value_div = row.find('div', class_='infobox-description')
                
                if label_div and value_div:
                    label = label_div.get_text(strip=True).rstrip(':')
                    value = value_div.get_text(strip=True)
                    details[label.lower().replace(' ', '_')] = value
        
        # Get career history from team history tables
        career_history = self._get_career_history(soup)
        if career_history:
            details['career_history'] = career_history
        
        return details
    
    def _get_career_history(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract career history from the team history section"""
        career = []
        
        # Find team history table
        team_history_header = soup.find(['h2', 'h3'], string=re.compile(r'Team History', re.IGNORECASE))
        
        if team_history_header:
            # Find the table following this header
            table = team_history_header.find_next('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        date_range = cells[0].get_text(strip=True)
                        team_name = cells[1].get_text(strip=True)
                        
                        career.append({
                            'date_range': date_range,
                            'team': team_name
                        })
        
        return career
    
    def scrape_all_players_with_details(self, max_players: int = None) -> pd.DataFrame:
        """Scrape all players from the portal and get detailed info for each"""
        print("Scraping European player portal...")
        players = self.scrape_europe_portal()
        
        print(f"Found {len(players)} players")
        
        if max_players:
            players = players[:max_players]
            print(f"Limiting to first {max_players} players")
        
        # Enrich with detailed information
        print("Fetching detailed player information...")
        for i, player in enumerate(players):
            if player['player_page_url']:
                print(f"Processing {i+1}/{len(players)}: {player['player_id']}")
                details = self.get_player_details(player['player_page_url'])
                player.update(details)
                
                # Rate limiting - be respectful
                time.sleep(2)
        
        df = pd.DataFrame(players)
        return df
    
    def scrape_basic_info_only(self) -> pd.DataFrame:
        """Quick scrape of just the portal data without detailed pages"""
        print("Scraping European player portal (basic info only)...")
        players = self.scrape_europe_portal()
        print(f"Found {len(players)} players")
        
        df = pd.DataFrame(players)
        return df


def main():
    scraper = LiquipediaValorantScraper()
    
    print("=" * 60)
    print("Liquipedia Valorant European Player Database Scraper")
    print("=" * 60)
    print()
    print("Choose scraping mode:")
    print("1. Quick scrape (basic info only - fast)")
    print("2. Detailed scrape (includes player pages - slow)")
    print("3. Sample detailed scrape (first 10 players)")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        # Quick scrape
        df = scraper.scrape_basic_info_only()
        output_file = 'european_players_basic.csv'
        
    elif choice == '2':
        # Full detailed scrape
        confirm = input("⚠️  This will take a long time. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
        df = scraper.scrape_all_players_with_details()
        output_file = 'european_players_detailed.csv'
        
    elif choice == '3':
        # Sample scrape
        df = scraper.scrape_all_players_with_details(max_players=10)
        output_file = 'european_players_sample.csv'
        
    else:
        print("Invalid choice")
        return
    
    # Save to CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✅ Data saved to {output_file}")
    print(f"Total players scraped: {len(df)}")
    print("\nFirst few rows:")
    print(df.head())
    
    # Display some statistics
    print("\n" + "=" * 60)
    print("Statistics:")
    print(f"Total Players: {len(df)}")
    print(f"\nPlayers by Country:")
    print(df['country'].value_counts().head(10))
    print(f"\nPlayers by Status:")
    print(df['status'].value_counts())


if __name__ == "__main__":
    main()
