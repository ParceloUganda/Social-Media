"""
Phase 3: Transcription - PARALLEL VERSION
Uses ThreadPoolExecutor for concurrent API calls to Whisper
Optimized for M2 Pro with rate limiting
"""

import os
import json
import time
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from typing import Dict, Optional
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Parallel settings
MAX_WORKERS = 8  # For API calls, be conservative to avoid rate limits
RATE_LIMIT_DELAY = 0.05  # Small delay between requests

def transcribe_audio_file(audio_path: str, language: Optional[str] = None) -> Dict:
    """Transcribe a single audio file using Whisper API."""
    try:
        # Small delay to respect rate limits
        time.sleep(RATE_LIMIT_DELAY)
        
        with open(audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=audio_file,
                language=language,
                response_format='verbose_json',
                timestamp_granularities=['segment']
            )
        
        # Convert segments
        segments = getattr(transcript, 'segments', [])
        if segments and hasattr(segments[0], 'model_dump'):
            segments = [seg.model_dump() for seg in segments]
        elif segments and hasattr(segments[0], 'dict'):
            segments = [seg.dict() for seg in segments]
        
        return {
            'text': transcript.text,
            'language': getattr(transcript, 'language', 'unknown'),
            'duration': getattr(transcript, 'duration', 0),
            'segments': segments,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'text': '',
            'language': 'unknown',
            'duration': 0,
            'segments': [],
            'success': False,
            'error': str(e)
        }

def process_single_transcription(item):
    """Process a single audio file transcription."""
    video_id = item['video_id']
    audio_path = item['audio_path']
    
    # Check if transcript already exists
    transcript_path = os.path.join(config.TRANSCRIPTS_DIR, f"{video_id}.json")
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r') as f:
            result = json.load(f)
    else:
        # Transcribe
        result = transcribe_audio_file(audio_path, language=None)
        
        # Save transcript
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Calculate cost
    duration_minutes = item['audio_duration'] / 60
    cost = duration_minutes * 0.006
    
    return {
        'video_id': video_id,
        'source_url': item['source_url'],
        'platform': item['platform'],
        'transcript_text': result['text'],
        'detected_language': result.get('language', 'unknown'),
        'audio_duration': item['audio_duration'],
        'transcription_cost': cost,
        'success': result['success'],
        'error': result.get('error')
    }

def process_transcriptions_parallel():
    """Main function with parallel processing."""
    print("=" * 60)
    print("PHASE 3: Audio Transcription (PARALLEL)")
    print("=" * 60)
    
    # Check API key
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("\n❌ Error: OpenAI API key not set!")
        return
    
    # Load audio results
    results_path = 'audio_extraction_results.json'
    if not os.path.exists(results_path):
        print(f"\n❌ Error: {results_path} not found")
        return
    
    with open(results_path, 'r') as f:
        audio_results = json.load(f)
    
    audio_files = [r for r in audio_results if r['audio_extracted']]
    print(f"\n📂 Found {len(audio_files)} audio files to transcribe")
    print(f"   Using {MAX_WORKERS} parallel workers")
    print(f"   Rate limit delay: {RATE_LIMIT_DELAY}s per request")
    
    # Process in parallel
    transcripts = []
    
    print(f"\n🎙️  Transcribing audio files in parallel...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        futures = {executor.submit(process_single_transcription, item): idx 
                  for idx, item in enumerate(audio_files)}
        
        # Collect results with progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Transcribing"):
            try:
                result = future.result()
                transcripts.append(result)
            except Exception as e:
                print(f"\n⚠️  Error: {e}")
    
    # Save results
    transcripts_df = pd.DataFrame(transcripts)
    transcripts_csv = 'transcriptions.csv'
    transcripts_df.to_csv(transcripts_csv, index=False, encoding='utf-8')
    
    # Statistics
    successful = transcripts_df['success'].sum()
    total_cost = transcripts_df['transcription_cost'].sum()
    languages = transcripts_df['detected_language'].value_counts()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 3 COMPLETE - Transcription (PARALLEL)")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   Total transcriptions: {len(transcripts_df)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(transcripts_df) - successful}")
    print(f"   Total cost: ${total_cost:.2f}")
    print(f"\n🌍 Detected languages:")
    for lang, count in languages.head(10).items():
        print(f"   {lang}: {count}")
    print(f"\n📝 Transcripts saved to: {transcripts_csv}")
    print("=" * 60)

if __name__ == "__main__":
    process_transcriptions_parallel()
