"""
Retry failed transcriptions and continue from where we left off
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import pandas as pd
from openai import OpenAI
import config
import json

print("=" * 60)
print("CLEANING UP FAILED TRANSCRIPTIONS")
print("=" * 60)

# Get all transcript files
transcript_files = []
for f in os.listdir('transcripts'):
    if f.endswith('.json'):
        transcript_files.append(f)

# Check for errors and delete failed transcripts
deleted = 0
for filename in transcript_files:
    filepath = f'transcripts/{filename}'
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if not data.get('success', True):
                os.remove(filepath)
                deleted += 1
                print(f"Deleted failed: {filename}")
    except:
        # If we can't read it, delete it
        os.remove(filepath)
        deleted += 1
        print(f"Deleted corrupted: {filename}")

print(f"\n✅ Cleaned up {deleted} failed transcriptions")

# Count remaining
audio_count = len([f for f in os.listdir('extracted_audio') if f.endswith('.mp3')])
transcript_count = len([f for f in os.listdir('transcripts') if f.endswith('.json')])
remaining = audio_count - transcript_count

print(f"\n📊 Status:")
print(f"   Total audio files: {audio_count}")
print(f"   Successful transcripts: {transcript_count}")
print(f"   Remaining to process: {remaining}")
print(f"\n🔄 Ready to resume transcription!")
print("=" * 60)
