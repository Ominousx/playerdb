"""
Database Cleaner
Removes tournament tiers, placements, and other non-team entries
"""

import pandas as pd
import re

class DatabaseCleaner:
    def __init__(self):
        # List of patterns to remove (not real teams)
        self.fake_team_patterns = [
            # Tournament tiers
            r'^S-Tier$', r'^A-Tier$', r'^B-Tier$', r'^C-Tier$', r'^D-Tier$',
            
            # Tournament placements
            r'^\d+(?:st|nd|rd|th)$',  # 1st, 2nd, 3rd, 4th
            r'^\d+(?:st|nd|rd|th)\s*-\s*\d+(?:st|nd|rd|th)$',  # 3rd - 4th
            
            # Status entries that shouldn't be teams
            r'^Retired$', r'^Inactive$', r'^Active$',
            r'^Qualifier$', r'^Showmatch$',
            
            # Generic entries
            r'^TBD$', r'^TBA$', r'^Unknown$',
            r'^N/A$', r'^None$', r'^\s*$',
            
            # Single digits or numbers
            r'^\d+$'
        ]
        
        # Additional exact matches to remove
        self.fake_teams_exact = {
            'S-Tier', 'A-Tier', 'B-Tier', 'C-Tier', 'D-Tier',
            'Retired', 'Inactive', 'Active',
            'Qualifier', 'Qualifiers', 'Showmatch',
            '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
            '3rd - 4th', '5th - 6th', '7th - 8th',
            'TBD', 'TBA', 'Unknown', 'N/A', 'None'
        }
    
    def is_fake_team(self, team_name):
        """Check if team name is fake/invalid"""
        if pd.isna(team_name) or not team_name or not str(team_name).strip():
            return True
        
        team = str(team_name).strip()
        
        # Check exact matches
        if team in self.fake_teams_exact:
            return True
        
        # Check patterns
        for pattern in self.fake_team_patterns:
            if re.match(pattern, team, re.IGNORECASE):
                return True
        
        return False
    
    def clean_stints(self, stints_df):
        """Clean career stints table"""
        print("\n🧹 Cleaning stints table...")
        
        original_count = len(stints_df)
        
        # Remove rows with fake teams
        stints_df_clean = stints_df[~stints_df['team'].apply(self.is_fake_team)].copy()
        
        removed = original_count - len(stints_df_clean)
        print(f"  ❌ Removed {removed:,} fake team stints ({removed/original_count*100:.1f}%)")
        print(f"  ✅ Kept {len(stints_df_clean):,} real team stints")
        
        return stints_df_clean
    
    def clean_transitions(self, transitions_df):
        """Clean transitions table"""
        print("\n🧹 Cleaning transitions table...")
        
        original_count = len(transitions_df)
        
        # Remove transitions involving fake teams
        transitions_df_clean = transitions_df[
            ~transitions_df['from_team'].apply(self.is_fake_team) &
            ~transitions_df['to_team'].apply(self.is_fake_team)
        ].copy()
        
        removed = original_count - len(transitions_df_clean)
        print(f"  ❌ Removed {removed:,} transitions ({removed/original_count*100:.1f}%)")
        print(f"  ✅ Kept {len(transitions_df_clean):,} real transitions")
        
        return transitions_df_clean
    
    def recalculate_player_stats(self, stints_df, original_stats_df):
        """Recalculate player stats based on cleaned stints"""
        print("\n🧹 Recalculating player statistics...")
        
        stats = []
        
        for player_id in stints_df['player_id'].unique():
            player_stints = stints_df[stints_df['player_id'] == player_id].sort_values('stint_number')
            
            if len(player_stints) == 0:
                continue
            
            # Get original player info
            original = original_stats_df[original_stats_df['player_id'] == player_id]
            if len(original) == 0:
                continue
            
            original = original.iloc[0]
            
            # Recalculate stats
            total_teams = len(player_stints)
            unique_teams = player_stints['team'].nunique()
            
            # Career span
            year_start = player_stints['year_start'].min()
            year_end = player_stints['year_end'].max()
            career_years = year_end - year_start if year_end > year_start else 0
            
            # Dates
            career_start = player_stints['date_start'].min()
            career_end = player_stints['date_end'].max()
            
            # Days
            total_days = player_stints['duration_days'].sum()
            avg_stint_days = player_stints['duration_days'].mean()
            
            # Stint types
            inactive_stints = len(player_stints[player_stints['stint_status'] == 'Inactive'])
            loan_stints = len(player_stints[player_stints['stint_status'] == 'Loan'])
            standin_stints = len(player_stints[player_stints['stint_status'] == 'Stand-in'])
            
            stats.append({
                'player_id': player_id,
                'real_name': original['real_name'],
                'country': original['country'],
                'current_team': original['current_team'],
                'player_status': original['player_status'],
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
                'is_active': original['is_active'],
                'has_current_team': original['has_current_team'],
                'inactive_stints': inactive_stints,
                'loan_stints': loan_stints,
                'standin_stints': standin_stints,
                'roles': original.get('roles', ''),
                'birth_date': original.get('birth_date', ''),
                'player_url': original.get('player_url', '')
            })
        
        stats_df = pd.DataFrame(stats)
        print(f"  ✅ Recalculated stats for {len(stats_df):,} players")
        
        return stats_df
    
    def clean_database(self, stints_file, transitions_file, stats_file, output_prefix=None):
        """Clean entire database"""
        
        print("\n" + "="*70)
        print("🧹 DATABASE CLEANER")
        print("="*70)
        
        # Load files
        print("\n📂 Loading database files...")
        stints_df = pd.read_csv(stints_file)
        
        try:
            transitions_df = pd.read_csv(transitions_file)
        except:
            transitions_df = None
            print("  ⚠️  No transitions file found")
        
        stats_df = pd.read_csv(stats_file)
        
        print(f"  ✅ Loaded {len(stints_df):,} stints")
        if transitions_df is not None:
            print(f"  ✅ Loaded {len(transitions_df):,} transitions")
        print(f"  ✅ Loaded {len(stats_df):,} player stats")
        
        # Clean
        stints_clean = self.clean_stints(stints_df)
        
        if transitions_df is not None:
            transitions_clean = self.clean_transitions(transitions_df)
        else:
            transitions_clean = None
        
        stats_clean = self.recalculate_player_stats(stints_clean, stats_df)
        
        # Save cleaned files
        if output_prefix is None:
            output_prefix = stints_file.replace('_stints.csv', '_cleaned')
        
        print("\n💾 Saving cleaned database...")
        
        stints_output = f"{output_prefix}_stints.csv"
        stints_clean.to_csv(stints_output, index=False)
        print(f"  ✅ {stints_output}")
        
        if transitions_clean is not None:
            transitions_output = f"{output_prefix}_transitions.csv"
            transitions_clean.to_csv(transitions_output, index=False)
            print(f"  ✅ {transitions_output}")
        
        stats_output = f"{output_prefix}_player_stats.csv"
        stats_clean.to_csv(stats_output, index=False)
        print(f"  ✅ {stats_output}")
        
        # Create Excel
        excel_output = f"{output_prefix}_complete.xlsx"
        with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
            stints_clean.to_excel(writer, sheet_name='Career Stints', index=False)
            if transitions_clean is not None:
                transitions_clean.to_excel(writer, sheet_name='Team Transitions', index=False)
            stats_clean.to_excel(writer, sheet_name='Player Statistics', index=False)
        
        print(f"  ✅ {excel_output}")
        
        # Summary
        print("\n" + "="*70)
        print("📊 CLEANING SUMMARY")
        print("="*70)
        
        print(f"\n✅ Clean Database:")
        print(f"  Stints:      {len(stints_clean):,}")
        if transitions_clean is not None:
            print(f"  Transitions: {len(transitions_clean):,}")
        print(f"  Players:     {len(stats_clean):,}")
        
        print(f"\n🏅 Top 20 Real Teams:")
        top_teams = stints_clean['team'].value_counts().head(20)
        for i, (team, count) in enumerate(top_teams.items(), 1):
            print(f"  {i:2}. {team:30} {count:3} players")
        
        return stints_clean, transitions_clean, stats_clean


def main():
    import sys
    from pathlib import Path
    
    print("\n" + "="*70)
    print("🧹 VALORANT DATABASE CLEANER")
    print("="*70)
    print("\nRemoves tournament tiers, placements, and fake team entries\n")
    
    # Get files
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter database prefix (e.g., career_database_20260216_095352): ").strip()
        
        if not base_path:
            import glob
            files = glob.glob('career_database_*_stints.csv')
            if files:
                base_path = files[0].replace('_stints.csv', '')
                print(f"Using: {base_path}")
            else:
                print("❌ No database files found!")
                return
    
    stints_file = f"{base_path}_stints.csv"
    transitions_file = f"{base_path}_transitions.csv"
    stats_file = f"{base_path}_player_stats.csv"
    
    # Check files exist
    if not Path(stints_file).exists():
        print(f"❌ File not found: {stints_file}")
        return
    
    # Clean
    cleaner = DatabaseCleaner()
    stints, transitions, stats = cleaner.clean_database(
        stints_file,
        transitions_file,
        stats_file
    )
    
    print("\n✅ Database cleaned successfully!")
    print("\n💡 Use the '_cleaned' files for your game!")


if __name__ == "__main__":
    main()
