"""
Database Merger
Merges supplemental player data (e.g., Brazilian players) with main database
"""

import pandas as pd
from datetime import datetime

def merge_databases(main_file, supplemental_file, output_file=None):
    """
    Merge main database with supplemental data
    
    Args:
        main_file: Original global_valorant_players file
        supplemental_file: Supplemental players file (e.g., Brazil)
        output_file: Output filename (optional)
    """
    
    print("\n" + "="*70)
    print("🔀 DATABASE MERGER")
    print("="*70)
    
    # Load both databases
    print("\n📂 Loading databases...")
    main_df = pd.read_excel(main_file)
    supp_df = pd.read_excel(supplemental_file)
    
    print(f"  ✅ Main database:         {len(main_df):,} players")
    print(f"  ✅ Supplemental database: {len(supp_df):,} players")
    
    # Show what we're adding
    print(f"\n🌍 Supplemental data breakdown:")
    if 'country' in supp_df.columns:
        print(supp_df['country'].value_counts().to_string())
    
    # Combine
    print(f"\n🔀 Merging databases...")
    combined_df = pd.concat([main_df, supp_df], ignore_index=True)
    
    print(f"  Combined total: {len(combined_df):,} players")
    
    # Remove duplicates (by player_id)
    print(f"\n🧹 Removing duplicates...")
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['player_id'], keep='first')
    duplicates_removed = before_dedup - len(combined_df)
    
    if duplicates_removed > 0:
        print(f"  ⚠️  Removed {duplicates_removed} duplicate players")
    else:
        print(f"  ✅ No duplicates found")
    
    print(f"\n📊 Final database: {len(combined_df):,} players")
    
    # Save
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"global_valorant_players_complete_{timestamp}.xlsx"
    
    combined_df.to_excel(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    
    # Show summary
    print("\n" + "="*70)
    print("📊 MERGED DATABASE SUMMARY")
    print("="*70)
    
    print(f"\n🌍 Players by Region:")
    if 'region' in combined_df.columns:
        print(combined_df['region'].value_counts().to_string())
    
    print(f"\n🌎 Top 15 Countries:")
    if 'country' in combined_df.columns:
        print(combined_df['country'].value_counts().head(15).to_string())
    
    print(f"\n📊 Player Status:")
    if 'status' in combined_df.columns:
        print(combined_df['status'].value_counts().to_string())
    
    return output_file, combined_df


def main():
    import sys
    import glob
    
    print("\n" + "="*70)
    print("🔀 VALORANT DATABASE MERGER")
    print("="*70)
    print("\nMerge supplemental player data (e.g., Brazil) with main database\n")
    
    # Get main database file
    if len(sys.argv) > 1:
        main_file = sys.argv[1]
    else:
        main_file = input("📁 Main database file: ").strip()
        
        if not main_file:
            # Find most recent global file
            files = glob.glob('global_valorant_players_*.xlsx')
            if files:
                # Exclude 'complete' versions
                files = [f for f in files if 'complete' not in f]
                if files:
                    main_file = max(files)
                    print(f"Using: {main_file}")
    
    if not main_file:
        print("❌ Main database file not found!")
        return
    
    # Get supplemental file
    if len(sys.argv) > 2:
        supp_file = sys.argv[2]
    else:
        supp_file = input("📁 Supplemental database file: ").strip()
        
        if not supp_file:
            # Find most recent supplemental file
            files = glob.glob('supplemental_players_*.xlsx')
            if files:
                supp_file = max(files)
                print(f"Using: {supp_file}")
    
    if not supp_file:
        print("❌ Supplemental database file not found!")
        return
    
    # Merge
    output_file, merged_df = merge_databases(main_file, supp_file)
    
    print("\n✅ Merge complete!")
    print("\n" + "="*70)
    print("🎯 NEXT STEPS")
    print("="*70)
    print("\n1. Rebuild career database:")
    print(f"   python3 career_database_builder.py {output_file}")
    print("\n2. Clean the database:")
    print(f"   python3 database_cleaner.py career_database_XXXXX")
    print("\n3. Your database will now include Brazilian players! 🇧🇷")


if __name__ == "__main__":
    main()
