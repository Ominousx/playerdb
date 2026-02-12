"""
Example Usage: Liquipedia Valorant Scraper for Esports Analysis
Common queries and analysis patterns for a Valorant esports analyst
"""

from advanced_liquipedia_scraper import AdvancedLiquipediaScraper
import pandas as pd
from datetime import datetime

def example_1_active_french_players():
    """Example 1: Scout active French players for potential recruitment"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Active French Players")
    print("="*60)
    
    scraper = AdvancedLiquipediaScraper()
    df = scraper.scrape_with_filters(
        countries=['France'],
        status=['Active'],
        get_details=False
    )
    
    filename = 'active_french_players.csv'
    df.to_csv(filename, index=False)
    
    print(f"\n✅ Scraped {len(df)} active French players")
    print(f"📁 Saved to: {filename}")
    print("\nTop players:")
    print(df[['player_id', 'real_name', 'current_team']].head(10))
    
    return df


def example_2_free_agents():
    """Example 2: Find free agents (players without teams)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Free Agents (Active Players Without Teams)")
    print("="*60)
    
    scraper = AdvancedLiquipediaScraper()
    
    # Get active players from major regions
    df = scraper.scrape_with_filters(
        countries=['France', 'Germany', 'United Kingdom', 'Spain', 'Sweden'],
        status=['Active'],
        get_details=False
    )
    
    # Filter to free agents
    free_agents = df[df['current_team'] == ''].copy()
    
    filename = 'free_agents.csv'
    free_agents.to_csv(filename, index=False)
    
    print(f"\n✅ Found {len(free_agents)} free agents")
    print(f"📁 Saved to: {filename}")
    print("\nFree agents by country:")
    print(free_agents['country'].value_counts())
    
    return free_agents


def example_3_team_rosters():
    """Example 3: Get current team rosters"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Current Team Rosters")
    print("="*60)
    
    scraper = AdvancedLiquipediaScraper()
    
    # Get all active players
    df = scraper.scrape_with_filters(
        status=['Active'],
        get_details=False
    )
    
    # Filter to players with teams
    with_teams = df[df['current_team'] != ''].copy()
    
    # Group by team
    team_rosters = with_teams.groupby('current_team').agg({
        'player_id': list,
        'country': list,
        'real_name': list
    }).reset_index()
    
    team_rosters['roster_size'] = team_rosters['player_id'].apply(len)
    team_rosters = team_rosters.sort_values('roster_size', ascending=False)
    
    filename = 'team_rosters.csv'
    
    # Flatten lists for CSV export
    export_df = with_teams[['current_team', 'player_id', 'real_name', 'country']].copy()
    export_df = export_df.sort_values(['current_team', 'player_id'])
    export_df.to_csv(filename, index=False)
    
    print(f"\n✅ Found {len(team_rosters)} teams with players")
    print(f"📁 Saved to: {filename}")
    print("\nTeams with most players:")
    print(team_rosters[['current_team', 'roster_size']].head(10))
    
    return export_df


def example_4_country_analysis():
    """Example 4: Analyze player distribution by country"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Player Distribution Analysis")
    print("="*60)
    
    scraper = AdvancedLiquipediaScraper()
    
    # Get all players
    df = scraper.scrape_with_filters(get_details=False)
    
    # Create summary statistics
    summary = pd.DataFrame()
    
    for country in df['country'].unique():
        country_df = df[df['country'] == country]
        
        summary = pd.concat([summary, pd.DataFrame({
            'country': [country],
            'total_players': [len(country_df)],
            'active': [len(country_df[country_df['status'] == 'Active'])],
            'inactive': [len(country_df[country_df['status'] == 'Inactive'])],
            'retired': [len(country_df[country_df['status'] == 'Retired'])],
            'with_teams': [len(country_df[country_df['current_team'] != ''])],
            'free_agents': [len(country_df[(country_df['current_team'] == '') & (country_df['status'] == 'Active')])]
        })], ignore_index=True)
    
    summary = summary.sort_values('total_players', ascending=False)
    
    filename = 'country_analysis.csv'
    summary.to_csv(filename, index=False)
    
    print(f"\n✅ Analyzed {len(summary)} countries")
    print(f"📁 Saved to: {filename}")
    print("\nTop 10 countries by player count:")
    print(summary.head(10).to_string(index=False))
    
    return summary


def example_5_targeted_scout():
    """Example 5: Detailed scouting of specific players"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Detailed Player Scouting (First 20 French Active Players)")
    print("="*60)
    
    scraper = AdvancedLiquipediaScraper()
    
    # Get detailed info for French active players
    df = scraper.scrape_with_filters(
        countries=['France'],
        status=['Active'],
        get_details=True,  # This will fetch career history
        max_players=20     # Limit for demo purposes
    )
    
    filename = 'french_players_detailed.csv'
    df.to_csv(filename, index=False)
    
    print(f"\n✅ Scraped detailed info for {len(df)} players")
    print(f"📁 Saved to: {filename}")
    
    # Show players with career history
    if 'teams_count' in df.columns:
        print("\nPlayers by number of previous teams:")
        print(df[['player_id', 'real_name', 'teams_count', 'current_team']].sort_values('teams_count', ascending=False))
    
    return df


def example_6_quick_stats():
    """Example 6: Quick statistics without full scrape"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Quick Statistics (Basic Scrape)")
    print("="*60)
    
    scraper = AdvancedLiquipediaScraper()
    df = scraper.scrape_with_filters(get_details=False)
    
    print("\n📊 QUICK STATISTICS")
    print("-" * 60)
    print(f"Total Players: {len(df)}")
    print(f"Active: {len(df[df['status'] == 'Active'])}")
    print(f"Inactive: {len(df[df['status'] == 'Inactive'])}")
    print(f"Retired: {len(df[df['status'] == 'Retired'])}")
    print(f"\nPlayers with Teams: {len(df[df['current_team'] != ''])}")
    print(f"Free Agents: {len(df[(df['current_team'] == '') & (df['status'] == 'Active')])}")
    
    print("\nTop 5 Countries:")
    print(df['country'].value_counts().head(5))
    
    return df


def run_all_examples():
    """Run all examples sequentially"""
    print("\n" + "="*60)
    print("🎮 LIQUIPEDIA VALORANT SCRAPER - EXAMPLE USAGE")
    print("="*60)
    print("\nThis will demonstrate common use cases for esports analysis")
    print("Each example will create a CSV file with the results")
    
    input("\nPress Enter to start...")
    
    # Run examples
    try:
        # Example 1: French players (fast)
        example_1_active_french_players()
        input("\nPress Enter for next example...")
        
        # Example 2: Free agents (fast)
        example_2_free_agents()
        input("\nPress Enter for next example...")
        
        # Example 3: Team rosters (fast)
        example_3_team_rosters()
        input("\nPress Enter for next example...")
        
        # Example 4: Country analysis (medium)
        example_4_country_analysis()
        input("\nPress Enter for next example...")
        
        # Example 5: Detailed scouting (slow - only 20 players)
        print("\n⚠️  Note: This example fetches detailed info and will take ~1 minute")
        proceed = input("Continue? (yes/no): ").lower()
        if proceed == 'yes':
            example_5_targeted_scout()
        
        # Example 6: Quick stats
        input("\nPress Enter for final example...")
        example_6_quick_stats()
        
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED!")
        print("="*60)
        print("\nGenerated files:")
        print("- active_french_players.csv")
        print("- free_agents.csv")
        print("- team_rosters.csv")
        print("- country_analysis.csv")
        print("- french_players_detailed.csv (if you ran example 5)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎮 Valorant Esports Data Scraper - Examples")
    print("="*60)
    print("\nChoose an option:")
    print("1. Run all examples sequentially")
    print("2. Example 1: Active French players")
    print("3. Example 2: Find free agents")
    print("4. Example 3: Current team rosters")
    print("5. Example 4: Country analysis")
    print("6. Example 5: Detailed scouting (slow)")
    print("7. Example 6: Quick statistics")
    print()
    
    choice = input("Enter choice (1-7): ").strip()
    
    examples = {
        '1': run_all_examples,
        '2': example_1_active_french_players,
        '3': example_2_free_agents,
        '4': example_3_team_rosters,
        '5': example_4_country_analysis,
        '6': example_5_targeted_scout,
        '7': example_6_quick_stats
    }
    
    if choice in examples:
        examples[choice]()
    else:
        print("Invalid choice")
