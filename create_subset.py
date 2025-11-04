"""
Create a budget-optimized subset of videos to process
"""
import pandas as pd

# Configuration
BUDGET = 9.0
COST_PER_VIDEO = 0.019  # $0.015 Whisper + $0.004 GPT-4
MAX_VIDEOS = int(BUDGET / COST_PER_VIDEO)

print(f"Creating subset of {MAX_VIDEOS} videos (Budget: ${BUDGET})")

# Load full dataset
df = pd.read_csv('viral_database.csv')
print(f"Total videos available: {len(df)}")

# Select top videos by view count
subset_df = df.nlargest(MAX_VIDEOS, 'view_count').copy()

# Save subset
subset_df.to_csv('viral_database_subset.csv', index=False)

print(f"\n✅ Subset created: viral_database_subset.csv")
print(f"   Videos: {len(subset_df)}")
print(f"   Platforms: Instagram={sum(subset_df['platform']=='Instagram')}, TikTok={sum(subset_df['platform']=='TikTok')}")
print(f"   Total views: {subset_df['view_count'].sum():,}")
print(f"   Estimated cost: ${len(subset_df) * COST_PER_VIDEO:.2f}")

# Show account breakdown
print(f"\n📊 Account breakdown:")
for acc, count in subset_df['account_name'].value_counts().head(10).items():
    print(f"   {acc}: {count} videos")
