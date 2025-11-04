"""
Create a Lemax-focused subset within budget
"""
import pandas as pd

# Configuration
BUDGET = 9.0
COST_PER_VIDEO = 0.019
MAX_VIDEOS = int(BUDGET / COST_PER_VIDEO)

print(f"Creating Lemax-focused subset (Budget: ${BUDGET})")

# Load full dataset
df = pd.read_csv('viral_database.csv')

# Get all Lemax videos
lemax_df = df[df['account_name'] == 'lemax__autos'].copy()
print(f"\nLemax videos available: {len(lemax_df)}")

# If Lemax fits in budget, use all of them
if len(lemax_df) <= MAX_VIDEOS:
    # Use all Lemax + fill remaining with top other videos
    remaining_slots = MAX_VIDEOS - len(lemax_df)
    other_df = df[df['account_name'] != 'lemax__autos'].nlargest(remaining_slots, 'view_count')
    subset_df = pd.concat([lemax_df, other_df]).sort_values('view_count', ascending=False)
    print(f"Using ALL {len(lemax_df)} Lemax videos + {remaining_slots} others")
else:
    # Use top Lemax by view count
    subset_df = lemax_df.nlargest(MAX_VIDEOS, 'view_count')
    print(f"Using top {MAX_VIDEOS} Lemax videos")

# Save subset
subset_df.to_csv('viral_database_lemax_subset.csv', index=False)

print(f"\n✅ Subset created: viral_database_lemax_subset.csv")
print(f"   Total videos: {len(subset_df)}")
print(f"   Estimated cost: ${len(subset_df) * COST_PER_VIDEO:.2f}")

# Account breakdown
print(f"\n📊 Account breakdown:")
for acc, count in subset_df['account_name'].value_counts().head(10).items():
    views = subset_df[subset_df['account_name']==acc]['view_count'].sum()
    print(f"   {acc}: {count} videos ({views:,} views)")

# Platform breakdown
print(f"\n🎬 Platform breakdown:")
print(f"   Instagram: {sum(subset_df['platform']=='Instagram')}")
print(f"   TikTok: {sum(subset_df['platform']=='TikTok')}")
print(f"\n💰 This will use ${len(subset_df) * COST_PER_VIDEO:.2f} of your $9 budget")
