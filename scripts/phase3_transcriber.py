"""
Phase 3: Transcriber - Transcribe audio files using OpenAI Whisper API
Supports both regular API and Batch API for cost savings.
Handles Luganda and multilingual content.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

def transcribe_audio_file(audio_path: str, language: Optional[str] = None) -> Dict:
    """
    Transcribe a single audio file using Whisper API.
    
    Args:
        audio_path: Path to audio file
        language: ISO language code (None for auto-detect, 'en' for English prompt)
    
    Returns:
        Dictionary with transcript and metadata
    """
    try:
        with open(audio_path, 'rb') as audio_file:
            # Whisper API call
            transcript = client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=audio_file,
                language=language,  # None = auto-detect, 'en' = English, etc.
                response_format='verbose_json',  # Get detailed response with language detection
                timestamp_granularities=['segment']
            )
        
        # Convert segments to dict if they exist
        segments = getattr(transcript, 'segments', [])
        if segments and hasattr(segments[0], 'model_dump'):
            segments = [seg.model_dump() for seg in segments]
        elif segments and hasattr(segments[0], 'dict'):
            segments = [seg.dict() for seg in segments]
        
        result = {
            'text': transcript.text,
            'language': getattr(transcript, 'language', 'unknown'),
            'duration': getattr(transcript, 'duration', 0),
            'segments': segments,
            'success': True,
            'error': None
        }
        
        return result
        
    except Exception as e:
        return {
            'text': '',
            'language': 'unknown',
            'duration': 0,
            'segments': [],
            'success': False,
            'error': str(e)
        }

def create_batch_request(audio_files: list) -> str:
    """
    Create batch request file for Whisper API (if supported).
    Note: As of now, Whisper doesn't support Batch API.
    This is a placeholder for when it becomes available.
    """
    # Batch API format for transcriptions (when available)
    requests = []
    for idx, audio_file in enumerate(audio_files):
        request = {
            "custom_id": f"request-{idx}",
            "method": "POST",
            "url": "/v1/audio/transcriptions",
            "body": {
                "model": config.WHISPER_MODEL,
                "file": audio_file
            }
        }
        requests.append(request)
    
    batch_file = "batch_transcription_requests.jsonl"
    with open(batch_file, 'w') as f:
        for req in requests:
            f.write(json.dumps(req) + '\n')
    
    return batch_file

def process_transcriptions():
    """Main function to transcribe all audio files."""
    print("=" * 60)
    print("PHASE 3: Audio Transcription with OpenAI Whisper")
    print("=" * 60)
    
    # Check API key
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("\n❌ Error: OpenAI API key not set!")
        print("   Please set OPENAI_API_KEY in your .env file")
        return
    
    # Load audio extraction results
    results_path = 'audio_extraction_results.json'
    if not os.path.exists(results_path):
        print(f"\n❌ Error: {results_path} not found. Run phase2_audio_extractor.py first.")
        return
    
    with open(results_path, 'r') as f:
        audio_results = json.load(f)
    
    # Filter successful audio extractions
    audio_files = [r for r in audio_results if r['audio_extracted']]
    print(f"\n📂 Found {len(audio_files)} audio files to transcribe")
    
    # Check for Luganda content (Lemax videos)
    print("\n⚠️  Note: Luganda language detection:")
    print("   - Whisper will auto-detect language")
    print("   - For better Luganda transcription, we'll use auto-detect first")
    print("   - If accuracy is poor, consider using English prompts for translation")
    
    # Process transcriptions
    transcripts = []
    total_cost = 0
    
    print(f"\n🎙️  Transcribing audio files...")
    for item in tqdm(audio_files, desc="Transcribing"):
        video_id = item['video_id']
        audio_path = item['audio_path']
        
        # Check if transcript already exists
        transcript_path = os.path.join(config.TRANSCRIPTS_DIR, f"{video_id}.json")
        if os.path.exists(transcript_path):
            with open(transcript_path, 'r') as f:
                result = json.load(f)
        else:
            # Transcribe with auto language detection
            result = transcribe_audio_file(audio_path, language=None)
            
            # If Luganda was detected but quality seems poor, could retry with 'en' prompt
            # This is an optional enhancement for later
            
            # Save transcript
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Calculate cost (Whisper: $0.006 per minute)
        duration_minutes = item['audio_duration'] / 60
        cost = duration_minutes * 0.006
        total_cost += cost
        
        transcripts.append({
            'video_id': video_id,
            'source_url': item['source_url'],
            'platform': item['platform'],
            'transcript_text': result['text'],
            'detected_language': result.get('language', 'unknown'),
            'audio_duration': item['audio_duration'],
            'transcription_cost': cost,
            'success': result['success'],
            'error': result.get('error')
        })
        
        # Rate limiting - avoid hitting API limits (optional)
        time.sleep(0.1)
    
    # Save all transcripts
    transcripts_df = pd.DataFrame(transcripts)
    transcripts_csv = config.PROJECT_ROOT / 'output' / 'transcriptions.csv'
    transcripts_df.to_csv(transcripts_csv, index=False, encoding='utf-8')
    
    # Print statistics
    successful = transcripts_df['success'].sum()
    languages = transcripts_df['detected_language'].value_counts()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 3 COMPLETE - Transcription")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   Total transcriptions: {len(transcripts_df)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(transcripts_df) - successful}")
    print(f"   Total cost: ${total_cost:.2f}")
    print(f"\n🌍 Detected languages:")
    for lang, count in languages.items():
        print(f"   {lang}: {count}")
    print(f"\n📝 Transcripts saved to:")
    print(f"   CSV: {transcripts_csv}")
    print(f"   JSON files: {config.TRANSCRIPTS_DIR}/")
    print("\n🔜 Next: Run phase4_classifier.py to classify products with GPT-4")
    print("=" * 60)

if __name__ == "__main__":
    process_transcriptions()
