"""
Global Valorant Player Scraper
Scrapes ALL regions from Liquipedia: Europe, CIS, Americas, Asia, Oceania, Africa & Middle East
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict, Optional
import re
import json
from datetime import datetime
from pathlib import Path

class GlobalValorantScraper:
    def __init__(self):
        self.base_url = "https://liquipedia.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # All Liquipedia portal pages
        self.regions = {
            'Europe': '/valorant/Portal:Players/Europe',
            'CIS': '/valorant/Portal:Players/CIS',
            'Americas': '/valorant/Portal:Players/Americas',
            'Asia': '/valorant/Portal:Players/Asia',
            'Oceania': '/valorant/Portal:Players/Oceania',
            'Africa & Middle East': '/valorant/Portal:Players/Africa_%26_Middle_East'
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
    
    def scrape_region_portal(self, region_name: str, portal_path: str) -> List[Dict]:
        """Scrape a single region's player portal"""
        print(f"\n{'='*70}")
        print(f"🌍 Scraping {region_name}")
        print(f"{'='*70}")
        
        url = f"{self.base_url}{portal_path}"
        soup = self.get_page_content(url)
        
        if not soup:
            print(f"❌ Failed to load {region_name} portal")
            return []
        
        players = []
        current_country = "Unknown"
        
        for element in soup.find_all(['h3', 'h4', 'table']):
            if element.name in ['h3', 'h4']:
                country_text = element.get_text(strip=True)
                current_country = re.sub(r'^\W+', '', country_text).strip()
            
            elif element.name == 'table':
                headers = element.find_all('th')
                header_texts = [h.get_text(strip=True) for h in headers]
                
                if 'ID' in header_texts and 'Real Name' in header_texts:
                    rows = element.find_all('tr')[1:]
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) < 3:
                            continue
                        
                        player_id = cells[0].get_text(strip=True)
                        player_link = cells[0].find('a')
                        player_url = None
                        
                        if player_link and player_link.get('href'):
                            player_url = self.base_url + player_link.get('href')
                        
                        real_name = cells[1].get_text(strip=True)
                        current_team = cells[2].get_text(strip=True)
                        
                        status = "Active"
                        row_style = row.get('style', '').lower()
                        if 'gray' in row_style:
                            status = "Retired"
                        elif 'blue' in row_style:
                            status = "Inactive"
                        
                        players.append({
                            'player_id': player_id,
                            'real_name': real_name,
                            'country': current_country,
                            'region': region_name,
                            'current_team': current_team,
                            'status': status,
                            'player_url': player_url
                        })
        
        print(f"✅ Found {len(players)} players in {region_name}")
        return players
    
    def extract_career_history(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract career history from player page"""
        career = []
        
        # Find History section
        history_header = None
        for tag in soup.find_all(['h2', 'h3', 'div', 'span']):
            text = tag.get_text(strip=True)
            if text.lower() == 'history':
                history_header = tag
                break
        
        if not history_header:
            return []
        
        # Try to find table
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
        """Extract start date"""
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_range)
        return match.group(1) if match else ''
    
    def _extract_end_date(self, date_range: str) -> str:
        """Extract end date"""
        if 'Present' in date_range or 'present' in date_range:
            return 'Present'
        matches = re.findall(r'(\d{4}-\d{2}-\d{2})', date_range)
        return matches[-1] if len(matches) > 1 else ''
    
    def _clean_team_name(self, team_text: str) -> str:
        """Clean team name"""
        team = re.sub(r'\s*\([^)]+\)\s*$', '', team_text)
        return team.strip()
    
    def _extract_status(self, team_text: str) -> str:
        """Extract status from team text"""
        match = re.search(r'\(([^)]+)\)', team_text)
        if match:
            status = match.group(1).strip().lower()
            if 'inactive' in status:
                return 'Inactive'
            elif 'loan' in status:
                return 'Loan'
            elif 'stand-in' in status or 'standin' in status:
                return 'Stand-in'
            elif 'trial' in status:
                return 'Trial'
            else:
                return status.title()
        return 'Active'
    
    def get_player_details(self, player_url: str, player_id: str) -> Dict:
        """Get detailed player info including career"""
        soup = self.get_page_content(player_url)
        if not soup:
            return {'career_history': None, 'teams_count': 0}
        
        career = self.extract_career_history(soup)
        
        details = {
            'career_history': json.dumps(career) if career else None,
            'teams_count': len(career),
            'roles': [],
            'birth_date': None
        }
        
        # Extract from infobox
        infobox = soup.find('div', class_='infobox-wrapper')
        if infobox:
            for row in infobox.find_all('div', class_='infobox-cell-2'):
                label_div = row.find('div', class_='infobox-header')
                value_div = row.find('div', class_='infobox-description')
                
                if label_div and value_div:
                    label = label_div.get_text(strip=True).lower()
                    value = value_div.get_text(strip=True)
                    
                    if 'role' in label:
                        details['roles'] = value
                    elif 'birth' in label or 'born' in label:
                        details['birth_date'] = value
        
        return details
    
    def scrape_all_regions(
        self,
        regions_to_scrape: Optional[List[str]] = None,
        get_details: bool = False,
        max_players_per_region: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Scrape all regions
        
        Args:
            regions_to_scrape: List of region names to scrape (None = all)
            get_details: Whether to fetch detailed career history
            max_players_per_region: Limit players per region (for testing)
        """
        
        if regions_to_scrape is None:
            regions_to_scrape = list(self.regions.keys())
        
        print("\n" + "="*70)
        print("🌍 GLOBAL VALORANT PLAYER SCRAPER")
        print("="*70)
        print(f"\nRegions to scrape: {', '.join(regions_to_scrape)}")
        print(f"Get detailed history: {get_details}")
        if max_players_per_region:
            print(f"Max per region: {max_players_per_region}")
        
        all_players = []
        
        # Scrape each region
        for region_name in regions_to_scrape:
            if region_name not in self.regions:
                print(f"⚠️  Unknown region: {region_name}")
                continue
            
            portal_path = self.regions[region_name]
            region_players = self.scrape_region_portal(region_name, portal_path)
            
            if max_players_per_region:
                region_players = region_players[:max_players_per_region]
                print(f"⏱️  Limited to {len(region_players)} players")
            
            all_players.extend(region_players)
        
        print(f"\n{'='*70}")
        print(f"📊 TOTAL PLAYERS SCRAPED: {len(all_players)}")
        print(f"{'='*70}")
        
        # Get detailed info if requested
        if get_details:
            print(f"\n🔍 Fetching detailed career history...")
            print(f"⏱️  Estimated time: ~{len(all_players) * 2 / 60:.0f} minutes\n")
            
            for i, player in enumerate(all_players):
                if (i + 1) % 50 == 0:
                    print(f"\n✅ Progress: {i+1}/{len(all_players)} ({(i+1)/len(all_players)*100:.1f}%)\n")
                
                if player['player_url']:
                    print(f"[{i+1}/{len(all_players)}] {player['player_id']} ({player['region']})")
                    details = self.get_player_details(player['player_url'], player['player_id'])
                    player.update(details)
                    
                    if details.get('teams_count', 0) > 0:
                        print(f"  ✅ Found {details['teams_count']} career entries")
                    else:
                        print(f"  ⚠️  No career history")
        
        df = pd.DataFrame(all_players)
        return df
    
    def save_database(self, df: pd.DataFrame, output_prefix=None):
        """Save the scraped database"""
        if output_prefix is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_prefix = f"global_valorant_players_{timestamp}"
        
        # CSV
        csv_file = f"{output_prefix}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"\n✅ CSV saved: {csv_file}")
        
        # Excel
        try:
            excel_file = f"{output_prefix}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"✅ Excel saved: {excel_file}")
        except:
            print("⚠️  Excel export failed")
        
        return csv_file


def main():
    scraper = GlobalValorantScraper()
    
    print("\n" + "="*70)
    print("🌍 GLOBAL VALORANT PLAYER DATABASE BUILDER")
    print("="*70)
    
    # Ask what to scrape
    print("\n📋 Available regions:")
    for i, region in enumerate(scraper.regions.keys(), 1):
        print(f"  {i}. {region}")
    
    print("\nOptions:")
    print("  • Press Enter = ALL regions")
    print("  • Type numbers (e.g., '1,2,3') = Specific regions")
    
    choice = input("\nYour choice: ").strip()
    
    if choice:
        indices = [int(x.strip()) - 1 for x in choice.split(',')]
        regions_list = list(scraper.regions.keys())
        regions_to_scrape = [regions_list[i] for i in indices if 0 <= i < len(regions_list)]
    else:
        regions_to_scrape = None  # All regions
    
    # Get detailed history?
    get_details = input("\n💡 Fetch detailed career history? (yes/no) [yes]: ").strip().lower()
    get_details = get_details != 'no'
    
    # Test mode?
    test_mode = input("\n🧪 Test mode? (limits to 10 players per region) (yes/no) [no]: ").strip().lower()
    max_per_region = 10 if test_mode == 'yes' else None
    
    # Confirm
    print("\n" + "="*70)
    print("🚀 STARTING SCRAPE")
    print("="*70)
    
    if test_mode == 'yes':
        print("⚠️  TEST MODE: 10 players per region")
    else:
        estimated_players = 5000 if not regions_to_scrape else len(regions_to_scrape or []) * 800
        estimated_hours = estimated_players * 2 / 3600 if get_details else 0.1
        print(f"📊 Estimated: ~{estimated_players:,} players")
        if get_details:
            print(f"⏱️  Estimated time: ~{estimated_hours:.1f} hours")
            confirm = input("\n⚠️  This will take a long time. Continue? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Cancelled.")
                return
    
    # Scrape
    df = scraper.scrape_all_regions(
        regions_to_scrape=regions_to_scrape,
        get_details=get_details,
        max_players_per_region=max_per_region
    )
    
    # Save
    output_file = scraper.save_database(df)
    
    # Statistics
    print("\n" + "="*70)
    print("📊 DATABASE SUMMARY")
    print("="*70)
    print(f"\nTotal Players: {len(df)}")
    print(f"\n🌍 By Region:")
    print(df['region'].value_counts().to_string())
    print(f"\n📊 By Status:")
    print(df['status'].value_counts().to_string())
    
    if 'teams_count' in df.columns:
        with_history = df[df['teams_count'] > 0]
        print(f"\n🏆 Career History:")
        print(f"  Players with history: {len(with_history)} ({len(with_history)/len(df)*100:.1f}%)")
        if len(with_history) > 0:
            print(f"  Avg teams per player: {with_history['teams_count'].mean():.1f}")
            print(f"  Most teams: {with_history['teams_count'].max()}")
    
    print("\n✅ SCRAPING COMPLETE!")
    print(f"\n💾 Saved to: {output_file}")
    print("\n🎯 Next steps:")
    print("  1. Run: python3 career_database_builder.py")
    print("  2. Then: python3 valorant_grid_generator.py")


if __name__ == "__main__":
    main()
