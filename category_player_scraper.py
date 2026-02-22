"""
Liquipedia Category Scraper
Scrapes players from country-specific category pages (e.g., Brazilian_Players)
Use this to fill gaps from the regional portal scraper
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict, Optional
import re
import json
from datetime import datetime

class CategoryPlayerScraper:
    def __init__(self):
        self.base_url = "https://liquipedia.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Country categories to scrape
        # Format: 'Country Name': 'Category_Page_Name'
        self.country_categories = {
            'Brazil': 'Brazilian_Players',
            'South Korea': 'South_Korean_Players',
            'Japan': 'Japanese_Players',
            'Indonesia': 'Indonesian_Players',
            'Vietnam': 'Vietnamese_Players',
            'Malaysia': 'Malaysian_Players',
            'Singapore': 'Singaporean_Players',
            'Taiwan': 'Taiwanese_Players',
            'Hong Kong': 'Hong_Kong_Players',
            'Philippines': 'Filipino_Players',
            'Thailand': 'Thai_Players',
            'India': 'Indian_Players',
            'Pakistan': 'Pakistani_Players',
            'China': 'Chinese_Players',
            # Add more as needed
        }
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse webpage content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(2)  # Rate limiting
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            return None
    
    def scrape_category_page(self, country: str, category_name: str) -> List[Dict]:
        """Scrape players from a category page"""
        url = f"{self.base_url}/valorant/Category:{category_name}"
        
        print(f"\n{'='*70}")
        print(f"🌍 Scraping {country} ({category_name})")
        print(f"{'='*70}")
        print(f"URL: {url}")
        
        soup = self.get_page_content(url)
        if not soup:
            print(f"❌ Failed to load category page")
            return []
        
        players = []
        
        # Method 1: Look for player links in category page
        # Category pages usually have links to player pages
        content_div = soup.find('div', {'id': 'mw-pages'})
        
        if content_div:
            # Find all player links
            player_links = content_div.find_all('a')
            
            print(f"  Found {len(player_links)} potential player links")
            
            for link in player_links:
                player_id = link.get_text(strip=True)
                player_href = link.get('href', '')
                
                if not player_href or '/Category:' in player_href:
                    continue
                
                player_url = self.base_url + player_href if not player_href.startswith('http') else player_href
                
                players.append({
                    'player_id': player_id,
                    'country': country,
                    'player_url': player_url,
                    'real_name': '',  # Will be filled by detail scraper
                    'current_team': '',
                    'status': 'Active',  # Assume active, will be updated
                    'region': self._get_region_from_country(country)
                })
        
        # Method 2: Look for structured player list
        player_divs = soup.find_all('div', class_='mw-category-group')
        
        for group in player_divs:
            links = group.find_all('a')
            for link in links:
                player_id = link.get_text(strip=True)
                player_href = link.get('href', '')
                
                if not player_href or '/Category:' in player_href:
                    continue
                
                # Avoid duplicates
                if any(p['player_id'] == player_id for p in players):
                    continue
                
                player_url = self.base_url + player_href if not player_href.startswith('http') else player_href
                
                players.append({
                    'player_id': player_id,
                    'country': country,
                    'player_url': player_url,
                    'real_name': '',
                    'current_team': '',
                    'status': 'Active',
                    'region': self._get_region_from_country(country)
                })
        
        print(f"✅ Found {len(players)} players from {country}")
        return players
    
    def _get_region_from_country(self, country: str) -> str:
        """Map country to region"""
        americas = {'Brazil', 'Argentina', 'Chile', 'Mexico', 'Colombia', 'Peru', 
                   'Uruguay', 'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay'}
        asia = {'South Korea', 'Japan', 'China', 'Taiwan', 'Hong Kong', 'Philippines',
               'Thailand', 'Vietnam', 'Indonesia', 'Malaysia', 'Singapore', 'India',
               'Pakistan', 'Mongolia'}
        
        if country in americas:
            return 'Americas'
        elif country in asia:
            return 'Asia'
        else:
            return 'Unknown'
    
    def extract_career_history(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract career history from player page"""
        career = []
        
        history_header = None
        for tag in soup.find_all(['h2', 'h3', 'div', 'span']):
            text = tag.get_text(strip=True)
            if text.lower() == 'history':
                history_header = tag
                break
        
        if not history_header:
            return []
        
        table = history_header.find_next('table')
        if table:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    date_text = cells[0].get_text(strip=True)
                    team_text = cells[1].get_text(strip=True)
                    
                    if re.search(r'\d{4}', date_text):
                        career.append({
                            'date_start': self._extract_start_date(date_text),
                            'date_end': self._extract_end_date(date_text),
                            'date_range': date_text,
                            'team': self._clean_team_name(team_text),
                            'status': self._extract_status(team_text)
                        })
        
        return career
    
    def _extract_start_date(self, date_range: str) -> str:
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_range)
        return match.group(1) if match else ''
    
    def _extract_end_date(self, date_range: str) -> str:
        if 'Present' in date_range or 'present' in date_range:
            return 'Present'
        matches = re.findall(r'(\d{4}-\d{2}-\d{2})', date_range)
        return matches[-1] if len(matches) > 1 else ''
    
    def _clean_team_name(self, team_text: str) -> str:
        team = re.sub(r'\s*\([^)]+\)\s*$', '', team_text)
        return team.strip()
    
    def _extract_status(self, team_text: str) -> str:
        match = re.search(r'\(([^)]+)\)', team_text)
        if match:
            status = match.group(1).strip().lower()
            if 'inactive' in status:
                return 'Inactive'
            elif 'loan' in status:
                return 'Loan'
            elif 'stand-in' in status or 'standin' in status:
                return 'Stand-in'
            else:
                return status.title()
        return 'Active'
    
    def get_player_details(self, player_url: str, player_id: str) -> Dict:
        """Get detailed player info"""
        soup = self.get_page_content(player_url)
        if not soup:
            return {'career_history': None, 'teams_count': 0}
        
        career = self.extract_career_history(soup)
        
        details = {
            'career_history': json.dumps(career) if career else None,
            'teams_count': len(career)
        }
        
        # Get real name and current team from infobox
        infobox = soup.find('div', class_='infobox-wrapper')
        if infobox:
            # Real name
            name_div = infobox.find('div', class_='infobox-header', string=re.compile(r'Name', re.IGNORECASE))
            if name_div:
                value_div = name_div.find_next_sibling('div', class_='infobox-description')
                if value_div:
                    details['real_name'] = value_div.get_text(strip=True)
            
            # Current team
            team_div = infobox.find('div', class_='infobox-header', string=re.compile(r'Team', re.IGNORECASE))
            if team_div:
                value_div = team_div.find_next_sibling('div', class_='infobox-description')
                if value_div:
                    details['current_team'] = value_div.get_text(strip=True)
        
        return details
    
    def scrape_countries(
        self,
        countries: Optional[List[str]] = None,
        get_details: bool = True
    ) -> pd.DataFrame:
        """Scrape players from specified countries"""
        
        if countries is None:
            countries = list(self.country_categories.keys())
        
        print("\n" + "="*70)
        print("🌍 CATEGORY-BASED PLAYER SCRAPER")
        print("="*70)
        print(f"\nCountries to scrape: {', '.join(countries)}")
        print(f"Get detailed history: {get_details}")
        
        all_players = []
        
        for country in countries:
            if country not in self.country_categories:
                print(f"\n⚠️  Unknown country: {country}")
                continue
            
            category_name = self.country_categories[country]
            country_players = self.scrape_category_page(country, category_name)
            all_players.extend(country_players)
        
        print(f"\n{'='*70}")
        print(f"📊 TOTAL PLAYERS SCRAPED: {len(all_players)}")
        print(f"{'='*70}")
        
        # Get detailed info if requested
        if get_details and len(all_players) > 0:
            print(f"\n🔍 Fetching detailed career history...")
            print(f"⏱️  Estimated time: ~{len(all_players) * 2 / 60:.0f} minutes\n")
            
            for i, player in enumerate(all_players):
                if (i + 1) % 50 == 0:
                    print(f"\n✅ Progress: {i+1}/{len(all_players)} ({(i+1)/len(all_players)*100:.1f}%)\n")
                
                print(f"[{i+1}/{len(all_players)}] {player['player_id']} ({player['country']})")
                details = self.get_player_details(player['player_url'], player['player_id'])
                player.update(details)
                
                if details.get('teams_count', 0) > 0:
                    print(f"  ✅ Found {details['teams_count']} career entries")
                else:
                    print(f"  ⚠️  No career history")
        
        df = pd.DataFrame(all_players)
        return df


def main():
    print("\n" + "="*70)
    print("🌍 SUPPLEMENTAL CATEGORY SCRAPER")
    print("="*70)
    print("\nUse this to scrape missing countries from category pages")
    print("(e.g., Brazilian players that were missed in regional portals)\n")
    
    scraper = CategoryPlayerScraper()
    
    # Show available countries
    print("📋 Available countries:")
    for i, country in enumerate(scraper.country_categories.keys(), 1):
        print(f"  {i:2}. {country}")
    
    # Get user input
    print("\nOptions:")
    print("  • Type country names (e.g., 'Brazil,South Korea')")
    print("  • Press Enter = ALL countries")
    
    choice = input("\nYour choice: ").strip()
    
    if choice:
        countries = [c.strip() for c in choice.split(',')]
    else:
        countries = None  # All countries
    
    # Get details?
    get_details = input("\n💡 Fetch detailed career history? (yes/no) [yes]: ").strip().lower()
    get_details = get_details != 'no'
    
    # Scrape
    print("\n" + "="*70)
    df = scraper.scrape_countries(countries=countries, get_details=get_details)
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"supplemental_players_{timestamp}.xlsx"
    
    df.to_excel(output_file, index=False)
    print(f"\n✅ Saved to: {output_file}")
    
    # Statistics
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"\nTotal Players: {len(df)}")
    print(f"\n🌍 By Country:")
    print(df['country'].value_counts().to_string())
    
    if 'teams_count' in df.columns:
        with_history = df[df['teams_count'] > 0]
        print(f"\n🏆 Career History:")
        print(f"  Players with history: {len(with_history)} ({len(with_history)/len(df)*100:.1f}%)")
    
    print("\n💡 Next step: Merge this with your main database!")


if __name__ == "__main__":
    main()
