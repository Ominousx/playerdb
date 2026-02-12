"""
Tier 1 Team Filter
Filter players who have played for Tier 1 teams in their career
"""

import pandas as pd
import json
import sys

# Define Tier 1 teams (VCT International League teams + top tier orgs)
TIER_1_TEAMS = {
    # VCT Americas
    'Sentinels', 'Cloud9', '100 Thieves', 'Evil Geniuses', 'NRG', 'FURIA', 
    'LOUD', 'Leviatán', 'KRÜ Esports', 'MIBR', 'G2 Esports', 'Envy', 'Team Envy',
    
    # VCT EMEA
    'Fnatic', 'Team Liquid', 'NAVI', 'Team Vitality', 'Giants Gaming', 'GIANTX',
    'Karmine Corp', 'KOI', 'BBL Esports', 'FUT Esports', 'Gentle Mates',
    'PCIFIC Esports', 'Team Heretics', 'Heretics',
    
    # VCT Pacific
    'Paper Rex', 'DRX', 'T1', 'Gen.G', 'Global Esports', 'Team Secret',
    'Talon Esports', 'Rex Regum Qeon', 'ZETA DIVISION', 'DetonatioN FocusMe',
    'BOOM Esports', 'Nongshim RedForce', 'Nongshim', 'NS RedForce',
    
    # VCT China
    'EDward Gaming', 'FunPlus Phoenix', 'Attacking Soul Esports', 'Bilibili Gaming',
    'JD Gaming', 'Trace Esports', 'Dragon Ranger Gaming', 'Nova Esports',
    
    # Historic/Former Tier 1
    'OpTic Gaming', 'The Guard', 'XSET', 'FPX', 'M3 Champions', 'Acend',
    'Gambit Esports', 'Guild Esports',
    
    # Add variations and common abbreviations
    'FPX', 'NAVI', 'NRG Esports', 'Sentinels', 'FNC', 'TL', 'VIT',
    'PRX', 'EDG', 'BLG', 'TE', 'TEC', 'KC', 'GIA', 'GIA Gaming',
    'G2', 'TH', 'BOOM', 'NS', 'ENVY', 'NV'
}

# Add case-insensitive lookup
TIER_1_TEAMS_LOWER = {team.lower() for team in TIER_1_TEAMS}


def is_tier_1_team(team_name):
    """Check if a team is Tier 1"""
    if not team_name or pd.isna(team_name):
        return False
    
    team_lower = team_name.lower().strip()
    
    # Direct match
    if team_lower in TIER_1_TEAMS_LOWER:
        return True
    
    # Check if Tier 1 team name is contained in the team name
    for tier1_team in TIER_1_TEAMS_LOWER:
        if tier1_team in team_lower or team_lower in tier1_team:
            return True
    
    return False


def filter_tier_1_players(input_file, output_file=None):
    """Filter players who have played for Tier 1 teams"""
    
    print("\n" + "="*70)
    print("🏆 TIER 1 PLAYER FILTER")
    print("="*70)
    
    # Load data
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    else:
        df = pd.read_csv(input_file)
    
    print(f"\n📊 Loaded {len(df)} players")
    
    # Track Tier 1 players
    tier_1_players = []
    
    for _, player in df.iterrows():
        player_tier_1_teams = []
        
        # Check current team
        if is_tier_1_team(player.get('current_team')):
            player_tier_1_teams.append(player['current_team'])
        
        # Check career history
        if pd.notna(player.get('career_history')) and player['career_history']:
            try:
                career = json.loads(player['career_history'])
                
                for entry in career:
                    team = entry.get('team', '')
                    if is_tier_1_team(team):
                        player_tier_1_teams.append(team)
                
            except:
                pass
        
        # If player has any Tier 1 experience, add them
        if player_tier_1_teams:
            player_data = player.to_dict()
            player_data['tier_1_teams'] = list(set(player_tier_1_teams))  # Remove duplicates
            player_data['tier_1_teams_count'] = len(set(player_tier_1_teams))
            tier_1_players.append(player_data)
    
    # Create filtered dataframe
    tier_1_df = pd.DataFrame(tier_1_players)
    
    print(f"✅ Found {len(tier_1_df)} players with Tier 1 experience")
    print(f"   ({len(tier_1_df)/len(df)*100:.1f}% of total)")
    
    # Save to file
    if output_file is None:
        output_file = input_file.replace('.xlsx', '_tier1.xlsx').replace('.csv', '_tier1.csv')
    
    if output_file.endswith('.xlsx'):
        # Convert list to string for Excel
        tier_1_df_export = tier_1_df.copy()
        if 'tier_1_teams' in tier_1_df_export.columns:
            tier_1_df_export['tier_1_teams'] = tier_1_df_export['tier_1_teams'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x
            )
        tier_1_df_export.to_excel(output_file, index=False)
    else:
        tier_1_df_export = tier_1_df.copy()
        if 'tier_1_teams' in tier_1_df_export.columns:
            tier_1_df_export['tier_1_teams'] = tier_1_df_export['tier_1_teams'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x
            )
        tier_1_df_export.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved to: {output_file}")
    
    return tier_1_df


def show_tier_1_stats(tier_1_df):
    """Display statistics about Tier 1 players"""
    
    print("\n" + "="*70)
    print("📊 TIER 1 STATISTICS")
    print("="*70)
    
    # By country
    print("\n🌍 Tier 1 Players by Country:")
    country_counts = tier_1_df['country'].value_counts().head(10)
    for country, count in country_counts.items():
        print(f"  {country}: {count}")
    
    # Most Tier 1 teams per player
    print("\n🏆 Players with Most Tier 1 Teams:")
    top_tier1 = tier_1_df.nlargest(10, 'tier_1_teams_count')[
        ['player_id', 'real_name', 'tier_1_teams_count', 'current_team']
    ]
    print(top_tier1.to_string(index=False))
    
    # Most common Tier 1 teams
    print("\n🎯 Most Common Tier 1 Teams:")
    all_tier1_teams = []
    for teams in tier_1_df['tier_1_teams']:
        if isinstance(teams, list):
            all_tier1_teams.extend(teams)
    
    if all_tier1_teams:
        team_counts = pd.Series(all_tier1_teams).value_counts().head(15)
        for i, (team, count) in enumerate(team_counts.items(), 1):
            print(f"  {i:2}. {team}: {count} players")
    
    # Currently on Tier 1 teams
    currently_tier1 = tier_1_df[tier_1_df['current_team'].apply(is_tier_1_team)]
    print(f"\n✨ Currently on Tier 1 Teams: {len(currently_tier1)}")
    
    # Free agents with Tier 1 experience
    free_agents = tier_1_df[
        (tier_1_df['current_team'].isna()) | 
        (tier_1_df['current_team'] == '') |
        (tier_1_df['current_team'] == 'nan')
    ]
    print(f"🆓 Free Agents with Tier 1 Experience: {len(free_agents)}")
    
    if len(free_agents) > 0:
        print("\n📋 Sample Free Agents with Tier 1 Experience:")
        sample_fa = free_agents.head(10)[['player_id', 'real_name', 'country', 'tier_1_teams_count']]
        print(sample_fa.to_string(index=False))


def main():
    print("\n" + "="*70)
    print("🏆 Tier 1 Team Filter for Valorant Career Data")
    print("="*70)
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("\n📁 Enter career history file name: ").strip()
        
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
    
    # Filter
    tier_1_df = filter_tier_1_players(input_file)
    
    # Show stats
    show_tier_1_stats(tier_1_df)
    
    # Export expanded version too
    print("\n" + "="*70)
    create_expanded = input("\n💡 Create expanded CSV (one row per team)? (y/n): ").strip().lower()
    
    if create_expanded == 'y':
        expanded_rows = []
        
        for _, player in tier_1_df.iterrows():
            if pd.notna(player.get('career_history')) and player['career_history']:
                try:
                    career = json.loads(player['career_history'])
                    
                    for i, entry in enumerate(career, 1):
                        is_t1 = is_tier_1_team(entry.get('team', ''))
                        
                        expanded_rows.append({
                            'player_id': player['player_id'],
                            'real_name': player['real_name'],
                            'country': player['country'],
                            'current_team': player['current_team'],
                            'stint_number': i,
                            'date_start': entry.get('date_start', ''),
                            'date_end': entry.get('date_end', ''),
                            'date_range': entry.get('date_range', ''),
                            'team': entry.get('team', ''),
                            'is_tier_1': is_t1,
                            'stint_status': entry.get('status', 'Active'),
                            'tier_1_teams_count': player['tier_1_teams_count']
                        })
                except:
                    pass
        
        expanded_df = pd.DataFrame(expanded_rows)
        expanded_file = input_file.replace('.xlsx', '_tier1_expanded.csv')
        expanded_df.to_csv(expanded_file, index=False)
        
        print(f"✅ Expanded file saved: {expanded_file}")
        print(f"   Total stints: {len(expanded_df)}")
        print(f"   Tier 1 stints: {expanded_df['is_tier_1'].sum()}")
    
    print("\n✅ Done!\n")


if __name__ == "__main__":
    main()
