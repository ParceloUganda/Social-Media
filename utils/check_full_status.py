import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import os
import config

# Full dataset
full_df = pd.read_csv(config.OUTPUT_CSV)

# Check audio files
audio_files = set([f.replace('.mp3', '') for f in os.listdir(config.AUDIO_DIR) if f.endswith('.mp3')])

# Check transcripts
transcript_files = set([f.replace('.json', '') for f in os.listdir(config.TRANSCRIPTS_DIR) if f.endswith('.json')])

print('='*60)
print('FULL DATASET PROCESSING STATUS')
print('='*60)

print(f'\n📊 Full dataset: {len(full_df)} videos')
print(f'\n👥 Accounts:')
for acc, count in full_df['account_name'].value_counts().head(10).items():
    print(f'   {acc}: {count} videos')

print(f'\n🎵 Audio extraction:')
print(f'   Completed: {len(audio_files)} / {len(full_df)}')
print(f'   Remaining: {len(full_df) - len(audio_files)}')

print(f'\n📝 Transcriptions:')
print(f'   Completed: {len(transcript_files)} / {len(full_df)}')
print(f'   Remaining: {len(full_df) - len(transcript_files)}')

print(f'\n💰 Cost estimate for remaining:')
remaining_videos = len(full_df) - len(transcript_files)
est_whisper = remaining_videos * 2.5 * 0.006  # ~2.5 min avg
est_gpt4 = remaining_videos * 0.002  # GPT-4o-mini batch
print(f'   Whisper (~2.5 min/video): ${est_whisper:.2f}')
print(f'   GPT-4 batch: ${est_gpt4:.2f}')
print(f'   Total remaining: ${est_whisper + est_gpt4:.2f}')
print(f'   Already spent: ~$3.68')
print(f'   Grand total: ${3.68 + est_whisper + est_gpt4:.2f}')

print('='*60)
