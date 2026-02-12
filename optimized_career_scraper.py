"""
Optimized Liquipedia Career History Scraper
Specifically designed for Liquipedia's History section format
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

class OptimizedCareerScraper:
    def __init__(self):
        self.base_url = "https://liquipedia.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
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
    
    def extract_career_history(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract career history from the History section"""
        career = []
        
        # Look for the History section (as shown in your screenshot)
        history_header = None
        
        # Try different ways to find the History section
        for tag in soup.find_all(['h2', 'h3', 'div', 'span']):
            text = tag.get_text(strip=True)
            if text.lower() == 'history':
                history_header = tag
                print(f"  ✅ Found 'History' section")
                break
        
        if not history_header:
            print(f"  ⚠️  No 'History' section found")
            return []
        
        # Method 1: Look for a table after the History header
        table = history_header.find_next('table')
        if table:
            career = self._parse_history_table(table)
            if career:
                return career
        
        # Method 2: Look for a div/list structure
        container = history_header.find_next(['div', 'ul'])
        if container:
            career = self._parse_history_container(container)
            if career:
                return career
        
        # Method 3: Parse text content directly
        next_section = history_header.find_next(['h2', 'h3'])
        if next_section:
            # Get all content between History header and next header
            current = history_header.find_next_sibling()
            while current and current != next_section:
                career.extend(self._parse_history_element(current))
                current = current.find_next_sibling()
        
        return career
    
    def _parse_history_table(self, table) -> List[Dict]:
        """Parse career history from a table"""
        career = []
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                date_text = cells[0].get_text(strip=True)
                team_text = cells[1].get_text(strip=True)
                
                # Look for patterns like "2020-04-13 — 2020-07-02"
                if re.search(r'\d{4}', date_text):
                    career.append({
                        'date_start': self._extract_start_date(date_text),
                        'date_end': self._extract_end_date(date_text),
                        'date_range': date_text,
                        'team': self._clean_team_name(team_text),
                        'status': self._extract_status(team_text)
                    })
        
        return career
    
    def _parse_history_container(self, container) -> List[Dict]:
        """Parse career history from a div or list container"""
        career = []
        
        # Look for all text containing date patterns
        for element in container.find_all(['div', 'li', 'p', 'span']):
            text = element.get_text(strip=True)
            
            # Pattern: "YYYY-MM-DD — YYYY-MM-DD Team Name"
            match = re.search(r'(\d{4}-\d{2}-\d{2}\s*[—–-]\s*(?:\d{4}-\d{2}-\d{2}|Present))\s+(.+)', text)
            if match:
                date_range = match.group(1).strip()
                team_name = match.group(2).strip()
                
                career.append({
                    'date_start': self._extract_start_date(date_range),
                    'date_end': self._extract_end_date(date_range),
                    'date_range': date_range,
                    'team': self._clean_team_name(team_name),
                    'status': self._extract_status(team_name)
                })
        
        return career
    
    def _parse_history_element(self, element) -> List[Dict]:
        """Parse career entries from any element"""
        career = []
        text = element.get_text(strip=True)
        
        # Look for date patterns in text
        matches = re.finditer(r'(\d{4}-\d{2}-\d{2}\s*[—–-]\s*(?:\d{4}-\d{2}-\d{2}|Present))\s+([^\n]+)', text)
        for match in matches:
            date_range = match.group(1).strip()
            team_name = match.group(2).strip()
            
            career.append({
                'date_start': self._extract_start_date(date_range),
                'date_end': self._extract_end_date(date_range),
                'date_range': date_range,
                'team': self._clean_team_name(team_name),
                'status': self._extract_status(team_name)
            })
        
        return career
    
    def _extract_start_date(self, date_range: str) -> str:
        """Extract start date from date range"""
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_range)
        return match.group(1) if match else ''
    
    def _extract_end_date(self, date_range: str) -> str:
        """Extract end date from date range"""
        if 'Present' in date_range or 'present' in date_range:
            return 'Present'
        matches = re.findall(r'(\d{4}-\d{2}-\d{2})', date_range)
        return matches[-1] if len(matches) > 1 else ''
    
    def _clean_team_name(self, team_text: str) -> str:
        """Clean team name by removing status markers"""
        # Remove (Inactive), (Loan), etc.
        team = re.sub(r'\s*\([^)]+\)\s*$', '', team_text)
        return team.strip()
    
    def _extract_status(self, team_text: str) -> str:
        """Extract status from team text like (Inactive), (Loan)"""
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
        """Get detailed player information including career history"""
        print(f"  🔍 Fetching: {player_id}")
        
        soup = self.get_page_content(player_url)
        if not soup:
            return {'career_history': None, 'teams_count': 0}
        
        # Extract career history
        career = self.extract_career_history(soup)
        
        details = {
            'career_history': json.dumps(career) if career else None,
            'teams_count': len(career),
            'roles': [],
            'birth_date': None,
            'nationality': None
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
                    elif 'nationality' in label:
                        details['nationality'] = value
        
        if career:
            print(f"  ✅ Found {len(career)} career entries")
        else:
            print(f"  ⚠️  No career history found")
        
        return details
    
    def scrape_players_with_history(
        self,
        countries: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        max_players: Optional[int] = None
    ) -> pd.DataFrame:
        """Main scraping function"""
        
        # Get player list from portal
        print("\n🔍 Step 1: Scraping player portal...")
        url = f"{self.base_url}/valorant/Portal:Players/Europe"
        soup = self.get_page_content(url)
        
        if not soup:
            print("❌ Failed to load portal page")
            return pd.DataFrame()
        
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
                        
                        status_val = "Active"
                        row_style = row.get('style', '').lower()
                        if 'gray' in row_style:
                            status_val = "Retired"
                        elif 'blue' in row_style:
                            status_val = "Inactive"
                        
                        players.append({
                            'player_id': player_id,
                            'real_name': real_name,
                            'country': current_country,
                            'current_team': current_team,
                            'status': status_val,
                            'player_url': player_url
                        })
        
        print(f"✅ Found {len(players)} total players")
        
        # Apply filters
        if countries:
            players = [p for p in players if p['country'] in countries]
            print(f"📍 Filtered to {len(players)} from: {', '.join(countries)}")
        
        if status:
            players = [p for p in players if p['status'] in status]
            print(f"🎯 Filtered to {len(players)} with status: {', '.join(status)}")
        
        if max_players:
            players = players[:max_players]
            print(f"⏱️  Limited to {max_players} players")
        
        # Get career history
        print(f"\n🔍 Step 2: Fetching career history ({len(players)} players)...")
        print("⏱️  Estimated time: ~{} minutes\n".format(len(players) * 2 / 60))
        
        for i, player in enumerate(players):
            print(f"[{i+1}/{len(players)}] {player['player_id']} ({player['country']})")
            
            if player['player_url']:
                details = self.get_player_details(player['player_url'], player['player_id'])
                player.update(details)
            
            if (i + 1) % 10 == 0:
                print(f"\n✅ Progress: {i+1}/{len(players)} complete\n")
        
        df = pd.DataFrame(players)
        return df


def main():
    scraper = OptimizedCareerScraper()
    
    print("\n" + "="*70)
    print("🎮 Optimized Liquipedia Career History Scraper")
    print("="*70)
    print("\nThis scraper is optimized for Liquipedia's History section")
    print("It will extract detailed career timelines for each player\n")
    
    # Get filters
    countries_input = input("🌍 Countries (e.g., 'France,Spain') or [Enter] for all: ").strip()
    countries = [c.strip() for c in countries_input.split(',')] if countries_input else None
    
    status_input = input("📊 Status (Active/Inactive/Retired) or [Enter] for all: ").strip()
    status_filter = [s.strip() for s in status_input.split(',')] if status_input else None
    
    max_input = input("🔢 Max players (for testing, e.g., 10) or [Enter] for all: ").strip()
    max_players = int(max_input) if max_input else None
    
    # Scrape
    print("\n" + "="*70)
    df = scraper.scrape_players_with_history(
        countries=countries,
        status=status_filter,
        max_players=max_players
    )
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"career_history_{timestamp}.csv"
    excel_file = f"career_history_{timestamp}.xlsx"
    
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"\n✅ CSV saved: {csv_file}")
    
    try:
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"✅ Excel saved: {excel_file}")
    except:
        print("⚠️  Excel export failed (openpyxl may not be installed)")
    
    # Statistics
    print("\n" + "="*70)
    print("📊 RESULTS SUMMARY")
    print("="*70)
    print(f"\nTotal Players: {len(df)}")
    
    if 'teams_count' in df.columns:
        with_history = df[df['teams_count'] > 0]
        print(f"Players with Career History: {len(with_history)} ({len(with_history)/len(df)*100:.1f}%)")
        
        if len(with_history) > 0:
            print(f"\n📈 Career Stats:")
            print(f"  Avg teams per player: {with_history['teams_count'].mean():.1f}")
            print(f"  Max teams: {with_history['teams_count'].max()}")
            print(f"  Min teams: {with_history['teams_count'].min()}")
            
            print(f"\n🏆 Top 10 by Career Length:")
            top = with_history.nlargest(10, 'teams_count')[['player_id', 'real_name', 'teams_count', 'current_team']]
            print(top.to_string(index=False))
    
    print("\n✅ Done! Check the CSV file for full career history data")


if __name__ == "__main__":
    main()
