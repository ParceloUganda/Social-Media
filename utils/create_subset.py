"""
Create a budget-optimized subset of videos to process
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import config

# Configuration
BUDGET = 9.0
COST_PER_VIDEO = 0.019  # $0.015 Whisper + $0.004 GPT-4
MAX_VIDEOS = int(BUDGET / COST_PER_VIDEO)

print(f"Creating subset of {MAX_VIDEOS} videos (Budget: ${BUDGET})")

# Load full dataset
df = pd.read_csv(config.OUTPUT_CSV)
print(f"Total videos available: {len(df)}")

# Select top videos by view count
subset_df = df.nlargest(MAX_VIDEOS, 'view_count').copy()

# Save subset
subset_path = config.PROJECT_ROOT / 'output' / 'viral_database_subset.csv'
subset_df.to_csv(subset_path, index=False)

print(f"\n✅ Subset created: {subset_path}")
print(f"   Videos: {len(subset_df)}")
print(f"   Platforms: Instagram={sum(subset_df['platform']=='Instagram')}, TikTok={sum(subset_df['platform']=='TikTok')}")
print(f"   Total views: {subset_df['view_count'].sum():,}")
print(f"   Estimated cost: ${len(subset_df) * COST_PER_VIDEO:.2f}")

# Show account breakdown
print(f"\n📊 Account breakdown:")
for acc, count in subset_df['account_name'].value_counts().head(10).items():
    print(f"   {acc}: {count} videos")
