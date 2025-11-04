"""
Phase 1: Data Parser - Extract initial data from JSON files to CSV
Creates a basic CSV with available fields from Instagram and TikTok data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pandas as pd
from typing import List, Dict
import config

def load_json_file(filepath: str) -> List[Dict]:
    """Load JSON file and return data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing {filepath}: {e}")
        return []

def parse_instagram_data(data: List[Dict]) -> pd.DataFrame:
    """Parse Instagram JSON data into DataFrame."""
    records = []
    
    for item in data:
        # Only process video content
        if item.get('type') != 'Video':
            continue
        
        # Extract username from inputUrl (e.g., https://www.instagram.com/kydyuzhini/?hl=en)
        account_name = 'Unknown'
        input_url = item.get('inputUrl', '')
        if input_url:
            # Extract username from URL
            parts = input_url.split('/')
            if len(parts) >= 4:
                account_name = parts[3].split('?')[0]  # Get username, remove query params
            
        record = {
            'caption': item.get('caption', ''),
            'account_name': account_name,
            'view_count': item.get('videoViewCount', 0),
            'source_url': item.get('url', ''),
            'video_url': item.get('videoUrl', ''),  # Direct video URL for download
            'platform': 'Instagram',
            'likes_count': item.get('likesCount', 0),
            'comments_count': item.get('commentsCount', 0),
            'timestamp': item.get('timestamp', ''),
            # Fields to be filled in later phases
            'product_category': '',
            'product_name': '',
            'transcript': '',
            'intended_age_category': '',
            'intended_spending_category': '',
        }
        records.append(record)
    
    return pd.DataFrame(records)

def parse_tiktok_data(data: List[Dict]) -> pd.DataFrame:
    """Parse TikTok JSON data into DataFrame."""
    records = []
    
    for item in data:
        record = {
            'caption': item.get('text', ''),
            'account_name': item.get('authorMeta.name', 'Unknown'),
            'view_count': item.get('playCount', 0),
            'source_url': item.get('webVideoUrl', ''),
            'video_url': item.get('webVideoUrl', ''),  # TikTok uses web URL
            'platform': 'TikTok',
            'likes_count': item.get('diggCount', 0),
            'comments_count': item.get('commentCount', 0),
            'share_count': item.get('shareCount', 0),
            'video_duration': item.get('videoMeta.duration', 0),
            'music_name': item.get('musicMeta.musicName', ''),
            'timestamp': '',  # TikTok data doesn't have timestamp in this format
            # Fields to be filled in later phases
            'product_category': '',
            'product_name': '',
            'transcript': '',
            'intended_age_category': '',
            'intended_spending_category': '',
        }
        records.append(record)
    
    return pd.DataFrame(records)

def create_initial_csv():
    """Main function to create initial CSV from JSON files."""
    print("=" * 60)
    print("PHASE 1: Data Parsing - Creating Initial CSV")
    print("=" * 60)
    
    # Load data
    print(f"\n📂 Loading {config.INSTAGRAM_JSON}...")
    instagram_data = load_json_file(config.INSTAGRAM_JSON)
    print(f"   Found {len(instagram_data)} Instagram posts")
    
    print(f"\n📂 Loading {config.TIKTOK_JSON}...")
    tiktok_data = load_json_file(config.TIKTOK_JSON)
    print(f"   Found {len(tiktok_data)} TikTok videos")
    
    # Parse data
    print("\n🔄 Parsing Instagram data...")
    instagram_df = parse_instagram_data(instagram_data)
    print(f"   Parsed {len(instagram_df)} Instagram videos")
    
    print("\n🔄 Parsing TikTok data...")
    tiktok_df = parse_tiktok_data(tiktok_data)
    print(f"   Parsed {len(tiktok_df)} TikTok videos")
    
    # Combine dataframes
    print("\n🔗 Combining data from both platforms...")
    combined_df = pd.concat([instagram_df, tiktok_df], ignore_index=True)
    
    # Sort by view count (descending)
    combined_df = combined_df.sort_values('view_count', ascending=False)
    
    # Save to CSV
    print(f"\n💾 Saving to {config.OUTPUT_CSV}...")
    combined_df.to_csv(config.OUTPUT_CSV, index=False, encoding='utf-8')
    
    # Print statistics
    print("\n" + "=" * 60)
    print("✅ PHASE 1 COMPLETE - Initial CSV Created")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   Total videos: {len(combined_df)}")
    print(f"   Instagram: {len(instagram_df)}")
    print(f"   TikTok: {len(tiktok_df)}")
    print(f"   Total views: {combined_df['view_count'].sum():,}")
    print(f"   Average views: {combined_df['view_count'].mean():,.0f}")
    print(f"   Top video views: {combined_df['view_count'].max():,}")
    print(f"\n📝 Output saved to: {config.OUTPUT_CSV}")
    print("\n🔜 Next: Run phase2_audio_extractor.py to download videos and extract audio")
    print("=" * 60)
    
    return combined_df

if __name__ == "__main__":
    create_initial_csv()
