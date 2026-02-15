"""
Team Logo Scraper for Liquipedia
Extracts team logos from your career database and downloads them
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
from urllib.parse import urljoin
import re

class TeamLogoScraper:
    def __init__(self, career_database_file):
        self.career_db_file = career_database_file
        self.base_url = "https://liquipedia.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Create logos directory
        self.logos_dir = Path("team_logos")
        self.logos_dir.mkdir(exist_ok=True)
        
        self.teams = set()
        self.logo_mapping = {}
    
    def load_teams_from_database(self):
        """Extract unique team names from career database"""
        print("📂 Loading teams from database...")
        
        # Try to load stints CSV first
        stints_file = self.career_db_file.replace('_complete.xlsx', '_stints.csv')
        
        try:
            df = pd.read_csv(stints_file)
        except:
            # Try Excel
            if self.career_db_file.endswith('.xlsx'):
                df = pd.read_excel(self.career_db_file, sheet_name='Career Stints')
            else:
                df = pd.read_csv(self.career_db_file)
        
        # Get unique teams
        if 'team' in df.columns:
            self.teams = set(df['team'].dropna().unique())
        elif 'current_team' in df.columns:
            self.teams = set(df['current_team'].dropna().unique())
        
        # Remove empty strings
        self.teams = {t for t in self.teams if t and t.strip()}
        
        print(f"✅ Found {len(self.teams)} unique teams")
        return self
    
    def get_team_page_url(self, team_name):
        """Convert team name to Liquipedia URL"""
        # Clean team name for URL
        clean_name = team_name.strip()
        # Replace spaces with underscores
        url_name = clean_name.replace(' ', '_')
        # Remove special characters that might cause issues
        url_name = re.sub(r'[^\w\s-]', '', url_name)
        
        return f"{self.base_url}/valorant/{url_name}"
    
    def get_team_logo(self, team_name):
        """Scrape team logo from Liquipedia team page"""
        url = self.get_team_page_url(team_name)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(1)  # Rate limiting
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Method 1: Look for infobox logo
            infobox = soup.find('div', class_='infobox-wrapper')
            if infobox:
                # Find logo image in infobox
                logo_img = infobox.find('img')
                if logo_img and logo_img.get('src'):
                    logo_url = logo_img['src']
                    if not logo_url.startswith('http'):
                        logo_url = urljoin(self.base_url, logo_url)
                    return logo_url
            
            # Method 2: Look for any team logo class
            logo_elements = soup.find_all('img', class_=re.compile(r'logo|team-logo'))
            for logo in logo_elements:
                if logo.get('src'):
                    logo_url = logo['src']
                    if not logo_url.startswith('http'):
                        logo_url = urljoin(self.base_url, logo_url)
                    return logo_url
            
            # Method 3: First image in infobox-image div
            infobox_img = soup.find('div', class_='infobox-image')
            if infobox_img:
                img = infobox_img.find('img')
                if img and img.get('src'):
                    logo_url = img['src']
                    if not logo_url.startswith('http'):
                        logo_url = urljoin(self.base_url, logo_url)
                    return logo_url
            
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)[:100]}")
        
        return None
    
    def download_logo(self, logo_url, team_name):
        """Download logo image"""
        try:
            response = self.session.get(logo_url, timeout=10)
            response.raise_for_status()
            
            # Get file extension
            ext = logo_url.split('.')[-1].split('?')[0]
            if ext not in ['png', 'jpg', 'jpeg', 'svg', 'webp']:
                ext = 'png'
            
            # Clean filename
            safe_name = re.sub(r'[^\w\s-]', '', team_name)
            safe_name = safe_name.replace(' ', '_')
            filename = f"{safe_name}.{ext}"
            
            filepath = self.logos_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return str(filepath)
            
        except Exception as e:
            print(f"  ⚠️  Download error: {str(e)[:100]}")
            return None
    
    def scrape_all_logos(self, max_teams=None):
        """Scrape logos for all teams"""
        print(f"\n🎨 Starting logo scraping for {len(self.teams)} teams...")
        
        if max_teams:
            teams_to_scrape = list(self.teams)[:max_teams]
        else:
            teams_to_scrape = self.teams
        
        success_count = 0
        failed_teams = []
        
        for i, team in enumerate(teams_to_scrape, 1):
            print(f"\n[{i}/{len(teams_to_scrape)}] {team}")
            
            # Get logo URL
            logo_url = self.get_team_logo(team)
            
            if logo_url:
                print(f"  ✅ Found logo: {logo_url[:60]}...")
                
                # Download logo
                filepath = self.download_logo(logo_url, team)
                
                if filepath:
                    print(f"  💾 Saved to: {filepath}")
                    self.logo_mapping[team] = {
                        'url': logo_url,
                        'filepath': filepath,
                        'status': 'success'
                    }
                    success_count += 1
                else:
                    print(f"  ❌ Failed to download")
                    failed_teams.append(team)
                    self.logo_mapping[team] = {
                        'url': logo_url,
                        'filepath': None,
                        'status': 'download_failed'
                    }
            else:
                print(f"  ❌ No logo found")
                failed_teams.append(team)
                self.logo_mapping[team] = {
                    'url': None,
                    'filepath': None,
                    'status': 'not_found'
                }
            
            # Progress update
            if i % 20 == 0:
                print(f"\n✅ Progress: {i}/{len(teams_to_scrape)} ({success_count} successful)")
        
        return success_count, failed_teams
    
    def save_mapping(self):
        """Save logo mapping to CSV"""
        mapping_df = pd.DataFrame([
            {
                'team_name': team,
                'logo_url': info['url'],
                'local_path': info['filepath'],
                'status': info['status']
            }
            for team, info in self.logo_mapping.items()
        ])
        
        csv_file = 'team_logo_mapping.csv'
        mapping_df.to_csv(csv_file, index=False)
        print(f"\n💾 Mapping saved to: {csv_file}")
        
        return csv_file
    
    def generate_fallback_logos(self, failed_teams):
        """Generate simple placeholder logos for teams without images"""
        print(f"\n🎨 Generating {len(failed_teams)} placeholder logos...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            for team in failed_teams[:10]:  # Limit to 10 for demo
                # Create simple colored square with team initials
                img = Image.new('RGB', (200, 200), color=(73, 109, 137))
                draw = ImageDraw.Draw(img)
                
                # Get team initials (first letter of each word)
                initials = ''.join([word[0] for word in team.split()[:3]]).upper()
                
                # Draw text
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
                except:
                    font = ImageFont.load_default()
                
                # Calculate text position (center)
                bbox = draw.textbbox((0, 0), initials, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((200 - text_width) / 2, (200 - text_height) / 2)
                
                draw.text(position, initials, fill=(255, 255, 255), font=font)
                
                # Save
                safe_name = re.sub(r'[^\w\s-]', '', team).replace(' ', '_')
                filepath = self.logos_dir / f"{safe_name}_placeholder.png"
                img.save(filepath)
                
                print(f"  ✅ Created placeholder for {team}")
            
            print(f"✅ Created {min(len(failed_teams), 10)} placeholders")
            print("💡 Install Pillow for more: pip install Pillow")
            
        except ImportError:
            print("⚠️  Pillow not installed. Run: pip install Pillow")
            print("💡 Or use default placeholder image for missing logos")


def main():
    import sys
    
    print("\n" + "="*70)
    print("🎨 TEAM LOGO SCRAPER")
    print("="*70)
    
    # Get database file
    if len(sys.argv) > 1:
        db_file = sys.argv[1]
    else:
        db_file = input("\n📁 Enter career database file: ").strip()
        
        if not db_file:
            import glob
            db_files = glob.glob('career_database_*_complete.xlsx')
            if not db_files:
                db_files = glob.glob('career_database_*_stints.csv')
            
            if db_files:
                db_file = max(db_files)
                print(f"Using: {db_file}")
            else:
                print("❌ No database files found!")
                return
    
    # Initialize scraper
    scraper = TeamLogoScraper(db_file)
    scraper.load_teams_from_database()
    
    # Ask for limit
    print(f"\n📊 Found {len(scraper.teams)} teams")
    limit = input("Enter max teams to scrape (or press Enter for all): ").strip()
    max_teams = int(limit) if limit else None
    
    # Scrape logos
    success_count, failed_teams = scraper.scrape_all_logos(max_teams=max_teams)
    
    # Save mapping
    scraper.save_mapping()
    
    # Summary
    print("\n" + "="*70)
    print("📊 SCRAPING SUMMARY")
    print("="*70)
    print(f"\nTotal teams: {len(scraper.teams)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {len(failed_teams)}")
    
    if failed_teams:
        print(f"\n⚠️  Teams without logos ({len(failed_teams)}):")
        for team in failed_teams[:10]:
            print(f"  • {team}")
        if len(failed_teams) > 10:
            print(f"  ... and {len(failed_teams) - 10} more")
        
        # Offer to create placeholders
        create_placeholders = input("\n🎨 Create placeholder logos? (y/n): ").strip().lower()
        if create_placeholders == 'y':
            scraper.generate_fallback_logos(failed_teams)
    
    print(f"\n✅ Logos saved to: team_logos/")
    print(f"📋 Mapping saved to: team_logo_mapping.csv")


if __name__ == "__main__":
    main()
