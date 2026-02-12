"""
Advanced Liquipedia Valorant Player Scraper
Features:
- Filter by country
- Filter by status (Active/Retired/Inactive)
- Export to CSV/Excel
- Resume capability for interrupted scrapes
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict, Optional
import re
import json
from pathlib import Path
from datetime import datetime

class AdvancedLiquipediaScraper:
    def __init__(self, checkpoint_file: str = 'scraper_checkpoint.json'):
        self.base_url = "https://liquipedia.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.checkpoint_file = checkpoint_file
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse webpage content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(1)  # Respectful rate limiting
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def scrape_europe_portal(self) -> List[Dict]:
        """Scrape the main European player portal"""
        url = f"{self.base_url}/valorant/Portal:Players/Europe"
        soup = self.get_page_content(url)
        
        if not soup:
            return []
        
        players = []
        current_country = "Unknown"
        
        # Find all tables and headers
        for element in soup.find_all(['h3', 'h4', 'table']):
            if element.name in ['h3', 'h4']:
                # This is a country heading
                country_text = element.get_text(strip=True)
                # Clean country name (remove flag icons, etc.)
                current_country = re.sub(r'^\W+', '', country_text).strip()
                
            elif element.name == 'table':
                # Check if it's a player table
                headers = element.find_all('th')
                header_texts = [h.get_text(strip=True) for h in headers]
                
                if 'ID' in header_texts and 'Real Name' in header_texts:
                    # This is a player table
                    rows = element.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        player_data = self._parse_player_row(row, current_country)
                        if player_data:
                            players.append(player_data)
        
        return players
    
    def _parse_player_row(self, row, country: str) -> Optional[Dict]:
        """Parse a single player row"""
        try:
            cells = row.find_all('td')
            if len(cells) < 3:
                return None
            
            # Player ID
            player_id_cell = cells[0]
            player_id = player_id_cell.get_text(strip=True)
            
            # Player page link
            player_link_tag = player_id_cell.find('a')
            player_page_url = None
            if player_link_tag and player_link_tag.get('href'):
                player_page_url = self.base_url + player_link_tag.get('href')
            
            # Real name
            real_name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            
            # Current team
            team_cell = cells[2] if len(cells) > 2 else None
            current_team = ""
            team_link = None
            
            if team_cell:
                current_team = team_cell.get_text(strip=True)
                team_link_tag = team_cell.find('a')
                if team_link_tag and team_link_tag.get('href'):
                    team_link = self.base_url + team_link_tag.get('href')
            
            # Determine player status from row styling
            status = "Active"
            row_style = row.get('style', '').lower()
            
            if 'background' in row_style:
                if 'gray' in row_style or '#d3d3d3' in row_style:
                    status = "Retired"
                elif 'blue' in row_style or '#add8e6' in row_style:
                    status = "Inactive"
            
            return {
                'player_id': player_id,
                'real_name': real_name,
                'country': country,
                'current_team': current_team,
                'status': status,
                'player_page_url': player_page_url,
                'team_link': team_link,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️  Error parsing row: {e}")
            return None
    
    def get_player_details(self, player_url: str) -> Dict:
        """Scrape detailed information from player page"""
        soup = self.get_page_content(player_url)
        
        if not soup:
            return {}
        
        details = {
            'roles': [],
            'birth_date': None,
            'age': None,
            'social_media': {}
        }
        
        # Parse infobox
        infobox = soup.find('div', class_='infobox-wrapper')
        if infobox:
            for row in infobox.find_all('div', class_='infobox-cell-2'):
                label_div = row.find('div', class_='infobox-header')
                value_div = row.find('div', class_='infobox-description')
                
                if label_div and value_div:
                    label = label_div.get_text(strip=True).rstrip(':').lower()
                    value = value_div.get_text(strip=True)
                    
                    if 'role' in label:
                        details['roles'] = [r.strip() for r in value.split(',')]
                    elif 'birth' in label:
                        details['birth_date'] = value
                    elif 'age' in label:
                        details['age'] = value
                    else:
                        details[label.replace(' ', '_')] = value
        
        # Get career history
        career = self._get_career_history(soup)
        if career:
            details['career_history'] = json.dumps(career)  # Store as JSON string for CSV compatibility
            details['teams_count'] = len(career)
        
        return details
    
    def _get_career_history(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract career/team history"""
        career = []
        
        # Look for team history section
        for header in soup.find_all(['h2', 'h3', 'span'], string=re.compile(r'Team History|Career', re.IGNORECASE)):
            table = header.find_next('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        date_range = cells[0].get_text(strip=True)
                        team_name = cells[1].get_text(strip=True)
                        
                        career.append({
                            'date': date_range,
                            'team': team_name
                        })
                break
        
        return career
    
    def save_checkpoint(self, data: Dict):
        """Save progress checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_checkpoint(self) -> Optional[Dict]:
        """Load previous checkpoint"""
        if Path(self.checkpoint_file).exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return None
    
    def scrape_with_filters(
        self,
        countries: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        get_details: bool = False,
        max_players: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Scrape players with filtering options
        
        Args:
            countries: List of countries to include (e.g., ['France', 'Germany'])
            status: List of statuses to include (e.g., ['Active', 'Inactive'])
            get_details: Whether to fetch detailed player info
            max_players: Maximum number of players to scrape
        """
        print("🔍 Scraping European player portal...")
        players = self.scrape_europe_portal()
        print(f"✅ Found {len(players)} total players")
        
        # Apply filters
        if countries:
            players = [p for p in players if p['country'] in countries]
            print(f"📍 Filtered to {len(players)} players from: {', '.join(countries)}")
        
        if status:
            players = [p for p in players if p['status'] in status]
            print(f"🎯 Filtered to {len(players)} players with status: {', '.join(status)}")
        
        if max_players:
            players = players[:max_players]
            print(f"⏱️  Limited to first {max_players} players")
        
        # Get detailed info if requested
        if get_details:
            print(f"\n📊 Fetching detailed information for {len(players)} players...")
            
            # Check for checkpoint
            checkpoint = self.load_checkpoint()
            start_idx = 0
            
            if checkpoint and checkpoint.get('players'):
                print(f"♻️  Resuming from checkpoint (processed {len(checkpoint['players'])} players)")
                processed_players = checkpoint['players']
                start_idx = len(processed_players)
            else:
                processed_players = []
            
            for i in range(start_idx, len(players)):
                player = players[i]
                print(f"[{i+1}/{len(players)}] Processing: {player['player_id']} ({player['country']})")
                
                if player['player_page_url']:
                    details = self.get_player_details(player['player_page_url'])
                    player.update(details)
                
                processed_players.append(player)
                
                # Save checkpoint every 10 players
                if (i + 1) % 10 == 0:
                    self.save_checkpoint({'players': processed_players, 'last_index': i})
                
                time.sleep(2)  # Rate limiting
            
            players = processed_players
            
            # Clear checkpoint when done
            if Path(self.checkpoint_file).exists():
                Path(self.checkpoint_file).unlink()
        
        df = pd.DataFrame(players)
        return df


def interactive_mode():
    """Interactive CLI for scraping"""
    scraper = AdvancedLiquipediaScraper()
    
    print("\n" + "=" * 70)
    print("🎮 Liquipedia Valorant European Player Database Scraper")
    print("=" * 70)
    
    # Get user preferences
    print("\n📋 Select scraping options:")
    
    # Details or not
    get_details = input("\n💡 Fetch detailed player info? (yes/no) [no]: ").strip().lower() == 'yes'
    
    # Country filter
    print("\n🌍 Filter by country? (leave blank for all)")
    print("Examples: France, Germany, United Kingdom, Spain")
    countries_input = input("Countries (comma-separated): ").strip()
    countries = [c.strip() for c in countries_input.split(',')] if countries_input else None
    
    # Status filter
    print("\n📊 Filter by status? (leave blank for all)")
    print("Options: Active, Inactive, Retired")
    status_input = input("Status (comma-separated): ").strip()
    status_filter = [s.strip() for s in status_input.split(',')] if status_input else None
    
    # Max players
    max_input = input("\n🔢 Maximum number of players (leave blank for all): ").strip()
    max_players = int(max_input) if max_input else None
    
    # Output format
    print("\n💾 Export format:")
    print("1. CSV")
    print("2. Excel")
    print("3. Both")
    format_choice = input("Choice (1-3) [1]: ").strip() or "1"
    
    # Execute scrape
    print("\n" + "=" * 70)
    print("🚀 Starting scrape...")
    print("=" * 70)
    
    try:
        df = scraper.scrape_with_filters(
            countries=countries,
            status=status_filter,
            get_details=get_details,
            max_players=max_players
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"valorant_players_{timestamp}"
        
        # Save files
        if format_choice in ['1', '3']:
            csv_file = f"{base_filename}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"\n✅ CSV saved: {csv_file}")
        
        if format_choice in ['2', '3']:
            excel_file = f"{base_filename}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"✅ Excel saved: {excel_file}")
        
        # Display summary
        print("\n" + "=" * 70)
        print("📈 SCRAPING SUMMARY")
        print("=" * 70)
        print(f"Total Players Scraped: {len(df)}")
        print(f"\n🌍 Players by Country:")
        print(df['country'].value_counts().to_string())
        print(f"\n📊 Players by Status:")
        print(df['status'].value_counts().to_string())
        
        if 'current_team' in df.columns:
            teams_with_players = df[df['current_team'] != ''].shape[0]
            print(f"\n👥 Players with Teams: {teams_with_players}")
        
        print("\n📋 Sample Data:")
        print(df.head(10).to_string())
        
        print("\n✅ Scraping completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    interactive_mode()
