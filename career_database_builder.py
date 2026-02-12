"""
Career History Database Builder
Converts JSON career history into a comprehensive, analysis-ready database
Creates multiple views optimized for different analyses
"""

import pandas as pd
import json
from datetime import datetime
import re

class CareerHistoryDatabase:
    def __init__(self, input_file):
        self.input_file = input_file
        self.players_df = None
        self.career_stints_df = None
        self.team_transitions_df = None
        self.player_stats_df = None
        
    def load_data(self):
        """Load the scraped career history file"""
        print("📂 Loading data...")
        
        if self.input_file.endswith('.xlsx'):
            self.players_df = pd.read_excel(self.input_file)
        else:
            self.players_df = pd.read_csv(self.input_file)
        
        print(f"✅ Loaded {len(self.players_df)} players")
        return self
    
    def build_career_stints_table(self):
        """
        Build detailed career stints table
        One row per team stint with full details
        """
        print("\n🔨 Building career stints table...")
        
        stints = []
        stint_id = 1
        
        for _, player in self.players_df.iterrows():
            if pd.notna(player.get('career_history')) and player['career_history']:
                try:
                    career = json.loads(player['career_history'])
                    
                    for stint_num, entry in enumerate(career, 1):
                        # Extract dates
                        date_start = entry.get('date_start', '')
                        date_end = entry.get('date_end', '')
                        date_range = entry.get('date_range', '')
                        
                        # Calculate stint duration (approximate)
                        duration_days = self._calculate_duration(date_start, date_end)
                        
                        # Determine if currently active
                        is_current = 'present' in date_end.lower() if date_end else False
                        
                        stints.append({
                            'stint_id': stint_id,
                            'player_id': player['player_id'],
                            'real_name': player['real_name'],
                            'country': player['country'],
                            'current_team': player['current_team'],
                            'player_status': player['status'],
                            'stint_number': stint_num,
                            'total_stints': player.get('teams_count', len(career)),
                            'team': entry.get('team', ''),
                            'date_start': date_start,
                            'date_end': date_end,
                            'date_range': date_range,
                            'stint_status': entry.get('status', 'Active'),
                            'is_current_team': is_current,
                            'duration_days': duration_days,
                            'year_start': self._extract_year(date_start),
                            'year_end': self._extract_year(date_end) if date_end and 'present' not in date_end.lower() else datetime.now().year,
                            'roles': player.get('roles', ''),
                            'player_url': player.get('player_url', '')
                        })
                        
                        stint_id += 1
                
                except Exception as e:
                    print(f"  ⚠️  Error processing {player['player_id']}: {e}")
        
        self.career_stints_df = pd.DataFrame(stints)
        print(f"✅ Created {len(self.career_stints_df)} career stints")
        return self
    
    def build_team_transitions_table(self):
        """
        Build team transitions table
        Shows moves FROM team A TO team B
        """
        print("\n🔨 Building team transitions table...")
        
        transitions = []
        transition_id = 1
        
        # Group by player
        for player_id in self.career_stints_df['player_id'].unique():
            player_stints = self.career_stints_df[
                self.career_stints_df['player_id'] == player_id
            ].sort_values('stint_number')
            
            # Create transitions between consecutive teams
            for i in range(len(player_stints) - 1):
                current_stint = player_stints.iloc[i]
                next_stint = player_stints.iloc[i + 1]
                
                transitions.append({
                    'transition_id': transition_id,
                    'player_id': player_id,
                    'real_name': current_stint['real_name'],
                    'country': current_stint['country'],
                    'from_team': current_stint['team'],
                    'to_team': next_stint['team'],
                    'from_stint_status': current_stint['stint_status'],
                    'to_stint_status': next_stint['stint_status'],
                    'transition_date': next_stint['date_start'],
                    'transition_year': next_stint['year_start'],
                    'from_duration_days': current_stint['duration_days'],
                    'stint_number': current_stint['stint_number']
                })
                
                transition_id += 1
        
        self.team_transitions_df = pd.DataFrame(transitions)
        print(f"✅ Created {len(self.team_transitions_df)} team transitions")
        return self
    
    def build_player_stats_table(self):
        """
        Build player career statistics table
        Aggregated stats per player
        """
        print("\n🔨 Building player statistics table...")
        
        stats = []
        
        for player_id in self.career_stints_df['player_id'].unique():
            player_stints = self.career_stints_df[
                self.career_stints_df['player_id'] == player_id
            ]
            
            # Get player info
            player_info = self.players_df[self.players_df['player_id'] == player_id].iloc[0]
            
            # Calculate statistics
            total_teams = len(player_stints)
            unique_teams = player_stints['team'].nunique()
            
            # Career span
            career_start = player_stints['date_start'].min()
            career_end = player_stints['date_end'].max()
            
            # Year range
            year_start = player_stints['year_start'].min()
            year_end = player_stints['year_end'].max()
            career_years = year_end - year_start if year_end > year_start else 0
            
            # Total career days (approximate)
            total_days = player_stints['duration_days'].sum()
            avg_stint_days = player_stints['duration_days'].mean()
            
            # Current status
            is_active = player_info['status'] == 'Active'
            has_team = pd.notna(player_info['current_team']) and player_info['current_team'] != ''
            
            # Stint status breakdown
            inactive_stints = len(player_stints[player_stints['stint_status'] == 'Inactive'])
            loan_stints = len(player_stints[player_stints['stint_status'] == 'Loan'])
            standin_stints = len(player_stints[player_stints['stint_status'] == 'Stand-in'])
            
            stats.append({
                'player_id': player_id,
                'real_name': player_info['real_name'],
                'country': player_info['country'],
                'current_team': player_info['current_team'],
                'player_status': player_info['status'],
                'total_teams': total_teams,
                'unique_teams': unique_teams,
                'teams_played_multiple_times': total_teams - unique_teams,
                'career_start_date': career_start,
                'career_end_date': career_end,
                'career_start_year': year_start,
                'career_end_year': year_end,
                'career_span_years': career_years,
                'total_career_days': total_days,
                'avg_stint_duration_days': avg_stint_days,
                'is_active': is_active,
                'has_current_team': has_team,
                'inactive_stints': inactive_stints,
                'loan_stints': loan_stints,
                'standin_stints': standin_stints,
                'roles': player_info.get('roles', ''),
                'birth_date': player_info.get('birth_date', ''),
                'player_url': player_info.get('player_url', '')
            })
        
        self.player_stats_df = pd.DataFrame(stats)
        print(f"✅ Created statistics for {len(self.player_stats_df)} players")
        return self
    
    def _calculate_duration(self, date_start, date_end):
        """Calculate approximate duration in days"""
        if not date_start or not date_end:
            return 0
        
        try:
            if 'present' in date_end.lower():
                end_date = datetime.now()
            else:
                end_date = datetime.strptime(date_end, '%Y-%m-%d')
            
            start_date = datetime.strptime(date_start, '%Y-%m-%d')
            duration = (end_date - start_date).days
            return max(0, duration)
        except:
            return 0
    
    def _extract_year(self, date_str):
        """Extract year from date string"""
        if not date_str or pd.isna(date_str):
            return None
        
        match = re.search(r'(\d{4})', str(date_str))
        if match:
            return int(match.group(1))
        return None
    
    def export_database(self, output_prefix=None):
        """Export all tables to CSV and Excel"""
        if output_prefix is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_prefix = f"career_database_{timestamp}"
        
        print("\n💾 Exporting database...")
        
        # Export individual tables
        files_created = []
        
        # 1. Career Stints (main table)
        stints_file = f"{output_prefix}_stints.csv"
        self.career_stints_df.to_csv(stints_file, index=False)
        files_created.append(stints_file)
        print(f"✅ {stints_file}")
        
        # 2. Team Transitions
        transitions_file = f"{output_prefix}_transitions.csv"
        self.team_transitions_df.to_csv(transitions_file, index=False)
        files_created.append(transitions_file)
        print(f"✅ {transitions_file}")
        
        # 3. Player Statistics
        stats_file = f"{output_prefix}_player_stats.csv"
        self.player_stats_df.to_csv(stats_file, index=False)
        files_created.append(stats_file)
        print(f"✅ {stats_file}")
        
        # 4. Create Excel workbook with all tables
        excel_file = f"{output_prefix}_complete.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            self.career_stints_df.to_excel(writer, sheet_name='Career Stints', index=False)
            self.team_transitions_df.to_excel(writer, sheet_name='Team Transitions', index=False)
            self.player_stats_df.to_excel(writer, sheet_name='Player Statistics', index=False)
        
        files_created.append(excel_file)
        print(f"✅ {excel_file}")
        
        return files_created
    
    def print_summary(self):
        """Print database summary statistics"""
        print("\n" + "="*70)
        print("📊 CAREER HISTORY DATABASE SUMMARY")
        print("="*70)
        
        print(f"\n📋 Database Tables:")
        print(f"  1. Career Stints:      {len(self.career_stints_df):,} rows")
        print(f"  2. Team Transitions:   {len(self.team_transitions_df):,} rows")
        print(f"  3. Player Statistics:  {len(self.player_stats_df):,} rows")
        
        print(f"\n👥 Players:")
        print(f"  Total Players:     {len(self.player_stats_df)}")
        print(f"  Active Players:    {self.player_stats_df['is_active'].sum()}")
        print(f"  With Teams:        {self.player_stats_df['has_current_team'].sum()}")
        print(f"  Free Agents:       {len(self.player_stats_df[self.player_stats_df['is_active'] & ~self.player_stats_df['has_current_team']])}")
        
        print(f"\n🌍 Top 5 Countries:")
        top_countries = self.player_stats_df['country'].value_counts().head(5)
        for country, count in top_countries.items():
            print(f"  {country}: {count}")
        
        print(f"\n🏆 Career Statistics:")
        print(f"  Total Team Stints:           {len(self.career_stints_df):,}")
        print(f"  Total Team Transitions:      {len(self.team_transitions_df):,}")
        print(f"  Avg Teams per Player:        {self.player_stats_df['total_teams'].mean():.1f}")
        print(f"  Most Teams (one player):     {self.player_stats_df['total_teams'].max()}")
        print(f"  Avg Career Span:             {self.player_stats_df['career_span_years'].mean():.1f} years")
        print(f"  Longest Career:              {self.player_stats_df['career_span_years'].max()} years")
        
        print(f"\n🔄 Stint Types:")
        print(f"  Active Stints:    {len(self.career_stints_df[self.career_stints_df['stint_status'] == 'Active'])}")
        print(f"  Inactive Stints:  {len(self.career_stints_df[self.career_stints_df['stint_status'] == 'Inactive'])}")
        print(f"  Loan Stints:      {len(self.career_stints_df[self.career_stints_df['stint_status'] == 'Loan'])}")
        print(f"  Stand-in Stints:  {len(self.career_stints_df[self.career_stints_df['stint_status'] == 'Stand-in'])}")
        
        print(f"\n🏅 Top 10 Most Common Teams:")
        top_teams = self.career_stints_df['team'].value_counts().head(10)
        for i, (team, count) in enumerate(top_teams.items(), 1):
            print(f"  {i:2}. {team}: {count} players")
        
        print(f"\n📅 Career Timeline:")
        earliest = self.player_stats_df['career_start_year'].min()
        latest = self.player_stats_df['career_end_year'].max()
        print(f"  Earliest Career Start: {earliest}")
        print(f"  Latest Activity:       {latest}")
        print(f"  Time Span:             {latest - earliest} years")


def main():
    import sys
    
    print("\n" + "="*70)
    print("🗄️  CAREER HISTORY DATABASE BUILDER")
    print("="*70)
    print("\nConverts JSON career history into comprehensive database tables")
    print("Creates multiple views optimized for different analyses\n")
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("📁 Enter career history file: ").strip()
        
        if not input_file:
            # Find most recent
            import glob
            files = glob.glob('career_history_*.xlsx')
            if files:
                input_file = max(files)
                print(f"Using: {input_file}")
            else:
                print("❌ No career history files found!")
                return
    
    # Build database
    print("\n" + "="*70)
    db = CareerHistoryDatabase(input_file)
    
    db.load_data()
    db.build_career_stints_table()
    db.build_team_transitions_table()
    db.build_player_stats_table()
    
    # Export
    files = db.export_database()
    
    # Summary
    db.print_summary()
    
    print("\n" + "="*70)
    print("✅ DATABASE CREATION COMPLETE!")
    print("="*70)
    print(f"\n📦 Created {len(files)} files:")
    for f in files:
        print(f"  • {f}")
    
    print("\n💡 Use these files for:")
    print("  • SQL imports")
    print("  • Power BI / Tableau dashboards")
    print("  • Advanced analytics in Python/R")
    print("  • Excel pivot tables and analysis")
    print("  • Team scouting and recruitment")


if __name__ == "__main__":
    main()
