"""
Phase 5: Final CSV Generation - Merge all data from previous phases
Creates the comprehensive final viral database CSV
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import os
import config

def merge_all_data():
    """Merge data from all phases into final CSV."""
    print("=" * 60)
    print("PHASE 5: Final CSV Generation")
    print("=" * 60)
    
    # Load initial data
    print(f"\n📂 Loading initial CSV...")
    if not os.path.exists(config.OUTPUT_CSV):
        print(f"❌ Error: {config.OUTPUT_CSV} not found")
        return
    
    df = pd.read_csv(config.OUTPUT_CSV)
    print(f"   Base records: {len(df)}")
    
    # Load transcriptions
    transcripts_path = config.PROJECT_ROOT / 'output' / 'transcriptions.csv'
    if os.path.exists(transcripts_path):
        print(f"\n📂 Loading transcriptions...")
        transcripts_df = pd.read_csv(transcripts_path)
        
        # Merge transcripts
        df = df.merge(
            transcripts_df[['video_id', 'transcript_text', 'detected_language', 'audio_duration']],
            left_on=df['source_url'].apply(lambda x: pd.util.hash_pandas_object(pd.Series([x]))[0] % 1000000000000),
            right_on='video_id',
            how='left',
            suffixes=('', '_trans')
        )
        
        # Update transcript column
        df['transcript'] = df['transcript_text'].fillna('')
        print(f"   Transcripts merged: {df['transcript_text'].notna().sum()}")
    else:
        print(f"\n⚠️  No transcriptions file found")
    
    # Load classifications
    classifications_path = config.PROJECT_ROOT / 'output' / 'classifications.csv'
    if os.path.exists(classifications_path):
        print(f"\n📂 Loading classifications...")
        class_df = pd.read_csv(classifications_path)
        
        # Merge classifications  
        if 'video_id' in df.columns and 'video_id' in class_df.columns:
            df = df.merge(
                class_df[[
                    'video_id', 'product_name', 'product_category',
                    'intended_age_category', 'intended_spending_category',
                    'brand', 'product_type'
                ]],
                on='video_id',
                how='left',
                suffixes=('', '_class')
            )
            print(f"   Classifications merged: {class_df['classification_success'].sum()}")
        else:
            print(f"   ⚠️  Could not merge - missing video_id column")
    else:
        print(f"\n⚠️  No classifications file found")
    
    # Select and order final columns
    final_columns = [
        'caption',
        'account_name',
        'view_count',
        'source_url',
        'product_category',
        'product_name',
        'transcript',
        'platform',
        'intended_age_category',
        'intended_spending_category',
        # Additional useful columns
        'likes_count',
        'comments_count',
        'detected_language',
        'audio_duration',
        'brand',
        'product_type',
        'timestamp'
    ]
    
    # Keep only columns that exist
    existing_cols = [col for col in final_columns if col in df.columns]
    final_df = df[existing_cols].copy()
    
    # Fill missing values
    for col in ['product_category', 'product_name', 'transcript', 
                'intended_age_category', 'intended_spending_category']:
        if col in final_df.columns:
            final_df[col] = final_df[col].fillna('')
    
    # Sort by view count
    final_df = final_df.sort_values('view_count', ascending=False)
    
    # Save final CSV
    final_output = config.PROJECT_ROOT / 'output' / 'viral_database_FINAL.csv'
    final_df.to_csv(final_output, index=False, encoding='utf-8')
    
    # Print statistics
    print("\n" + "=" * 60)
    print("✅ PHASE 5 COMPLETE - Final Database Created")
    print("=" * 60)
    print(f"\n📊 Final Statistics:")
    print(f"   Total videos: {len(final_df)}")
    print(f"   Platforms:")
    print(f"     Instagram: {(final_df['platform'] == 'Instagram').sum()}")
    print(f"     TikTok: {(final_df['platform'] == 'TikTok').sum()}")
    print(f"   With transcripts: {(final_df['transcript'] != '').sum()}")
    print(f"   With classifications: {(final_df['product_name'] != '').sum()}")
    print(f"   Total views: {final_df['view_count'].sum():,}")
    print(f"   Average views: {final_df['view_count'].mean():,.0f}")
    print(f"   Top video: {final_df['view_count'].max():,} views")
    
    if 'product_category' in final_df.columns:
        print(f"\n📦 Product Categories:")
        cat_counts = final_df[final_df['product_category'] != '']['product_category'].value_counts()
        for cat, count in cat_counts.items():
            print(f"     {cat}: {count}")
    
    if 'intended_spending_category' in final_df.columns:
        print(f"\n💰 Spending Categories:")
        spend_counts = final_df[final_df['intended_spending_category'] != '']['intended_spending_category'].value_counts()
        for cat, count in spend_counts.items():
            print(f"     {cat}: {count}")
    
    print(f"\n📁 Output file: {final_output}")
    print(f"✨ Your viral marketing database is ready!")
    print("=" * 60)
    
    return final_df

if __name__ == "__main__":
    merge_all_data()
