"""
Career History Analyzer
Parse and analyze the JSON career history data from the scraper
"""

import pandas as pd
import json
from datetime import datetime
import re

def parse_career_history_file(excel_file):
    """Load and parse career history from Excel file"""
    
    # Load the data
    df = pd.read_excel(excel_file)
    
    print(f"📊 Loaded {len(df)} players from {excel_file}\n")
    
    # Expand career history into separate rows
    expanded_rows = []
    
    for _, player in df.iterrows():
        if pd.notna(player['career_history']) and player['career_history']:
            try:
                career = json.loads(player['career_history'])
                
                for entry in career:
                    expanded_rows.append({
                        'player_id': player['player_id'],
                        'real_name': player['real_name'],
                        'country': player['country'],
                        'current_team': player['current_team'],
                        'player_status': player['status'],
                        'total_teams': player['teams_count'],
                        'date_start': entry.get('date_start', ''),
                        'date_end': entry.get('date_end', ''),
                        'date_range': entry.get('date_range', ''),
                        'team': entry.get('team', ''),
                        'team_status': entry.get('status', 'Active')
                    })
            except:
                pass
    
    # Create expanded dataframe
    expanded_df = pd.DataFrame(expanded_rows)
    
    return df, expanded_df


def analyze_careers(df, expanded_df):
    """Analyze career patterns"""
    
    print("=" * 70)
    print("📈 CAREER ANALYSIS")
    print("=" * 70)
    
    # Players with career data
    with_history = df[df['teams_count'] > 0]
    
    print(f"\n👥 Players Analyzed: {len(with_history)}")
    print(f"📊 Total Career Moves: {len(expanded_df)}")
    
    # Average teams per player
    print(f"\n🔄 Career Mobility:")
    print(f"  Average teams per player: {with_history['teams_count'].mean():.1f}")
    print(f"  Most teams: {with_history['teams_count'].max()}")
    print(f"  Fewest teams: {with_history['teams_count'].min()}")
    
    # Most common teams
    print(f"\n🏆 Most Common Teams:")
    team_counts = expanded_df['team'].value_counts().head(10)
    for i, (team, count) in enumerate(team_counts.items(), 1):
        print(f"  {i}. {team}: {count} players")
    
    # Team status breakdown
    print(f"\n📊 Team Status Breakdown:")
    status_counts = expanded_df['team_status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count} ({count/len(expanded_df)*100:.1f}%)")
    
    # Players by total teams
    print(f"\n🎖️  Top Players by Career Length:")
    top_players = with_history.nlargest(10, 'teams_count')[['player_id', 'real_name', 'teams_count', 'current_team']]
    print(top_players.to_string(index=False))


def export_expanded_career(expanded_df, output_file):
    """Export expanded career history"""
    expanded_df.to_csv(output_file, index=False)
    print(f"\n✅ Expanded career data saved to: {output_file}")
    print(f"   This file has one row per team stint\n")


def show_player_timeline(df, player_id):
    """Show detailed timeline for a specific player"""
    player = df[df['player_id'] == player_id].iloc[0]
    
    print("\n" + "=" * 70)
    print(f"🎮 CAREER TIMELINE: {player['player_id']}")
    print("=" * 70)
    print(f"Name: {player['real_name']}")
    print(f"Country: {player['country']}")
    print(f"Current Team: {player['current_team']}")
    print(f"Status: {player['status']}")
    print(f"Total Teams: {player['teams_count']}")
    
    if pd.notna(player['career_history']):
        career = json.loads(player['career_history'])
        print(f"\n📅 Career History:\n")
        
        for i, entry in enumerate(career, 1):
            status_marker = ""
            if entry.get('status') == 'Inactive':
                status_marker = " 🔵 (Inactive)"
            elif entry.get('status') == 'Loan':
                status_marker = " 🔄 (Loan)"
            elif entry.get('status') == 'Stand-in':
                status_marker = " 🆘 (Stand-in)"
            
            print(f"{i:2}. {entry['date_range']:30} → {entry['team']}{status_marker}")


def main():
    import sys
    
    print("\n" + "=" * 70)
    print("📊 Career History Analyzer")
    print("=" * 70)
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("\n📁 Enter Excel file name (or press Enter for latest): ").strip()
        
        if not input_file:
            # Find the most recent career_history file
            import glob
            files = glob.glob('career_history_*.xlsx')
            if files:
                input_file = max(files)
                print(f"Using: {input_file}")
            else:
                print("❌ No career history files found!")
                return
    
    # Load and parse
    df, expanded_df = parse_career_history_file(input_file)
    
    # Analyze
    analyze_careers(df, expanded_df)
    
    # Export expanded data
    output_file = input_file.replace('.xlsx', '_expanded.csv')
    export_expanded_career(expanded_df, output_file)
    
    # Interactive mode
    while True:
        print("\n" + "=" * 70)
        choice = input("\n👀 View specific player timeline? (enter player ID or 'quit'): ").strip()
        
        if choice.lower() in ['quit', 'q', 'exit', '']:
            break
        
        if choice in df['player_id'].values:
            show_player_timeline(df, choice)
        else:
            print(f"❌ Player '{choice}' not found")
            print(f"\nAvailable players:")
            print(df['player_id'].tolist())


if __name__ == "__main__":
    main()
