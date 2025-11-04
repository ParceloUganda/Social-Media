"""
Phase 2: Audio Extraction - PARALLEL VERSION
Uses ThreadPoolExecutor for concurrent downloads and processing
Optimized for M2 Pro with 8-12 cores
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import subprocess
import hashlib
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import config

# Number of parallel workers (adjust based on your M2 Pro)
MAX_WORKERS = 10  # M2 Pro can handle 8-12

def get_video_id(url: str) -> str:
    """Generate unique ID from URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def get_audio_duration(audio_path: str) -> float:
    """Get audio duration using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except:
        return 0

def download_video_ytdlp(url: str, output_path: str, video_id: str) -> bool:
    """Download video using yt-dlp."""
    try:
        subprocess.run(
            ['yt-dlp', '-f', 'best', '-o', output_path, url, '--quiet', '--no-warnings'],
            capture_output=True, timeout=120, check=True
        )
        return os.path.exists(output_path)
    except:
        return False

def extract_audio_ffmpeg(video_path: str, audio_path: str) -> bool:
    """Extract audio from video using ffmpeg."""
    try:
        subprocess.run(
            ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'libmp3lame',
             '-ar', '16000', '-ac', '1', '-b:a', '64k', audio_path,
             '-loglevel', 'error', '-y'],
            capture_output=True, timeout=60, check=True
        )
        return os.path.exists(audio_path)
    except:
        return False

def process_single_video(row):
    """Process a single video (download + extract audio)."""
    video_id = get_video_id(row['source_url'])
    video_path = os.path.join(config.TEMP_DIR, f"{video_id}.mp4")
    audio_path = os.path.join(config.AUDIO_DIR, f"{video_id}.mp3")
    
    result = {
        'video_id': video_id,
        'source_url': row['source_url'],
        'platform': row['platform'],
        'video_downloaded': False,
        'audio_extracted': False,
        'audio_duration': 0,
        'audio_path': ''
    }
    
    # Skip if audio already exists
    if os.path.exists(audio_path):
        result['audio_extracted'] = True
        result['audio_duration'] = get_audio_duration(audio_path)
        result['audio_path'] = audio_path
        return result
    
    # Download video
    if download_video_ytdlp(row['source_url'], video_path, video_id):
        result['video_downloaded'] = True
        
        # Extract audio
        if extract_audio_ffmpeg(video_path, audio_path):
            result['audio_extracted'] = True
            result['audio_duration'] = get_audio_duration(audio_path)
            result['audio_path'] = audio_path
            
            # Clean up video file
            try:
                os.remove(video_path)
            except:
                pass
    
    return result

def process_videos_parallel():
    """Main function with parallel processing."""
    print("=" * 60)
    print("PHASE 2: Audio Extraction (PARALLEL)")
    print("=" * 60)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    tools = ['yt-dlp', 'ffmpeg', 'ffprobe']
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, timeout=5)
            print(f"   ✅ {tool} found")
        except:
            print(f"   ❌ {tool} not found")
            return
    
    # Load CSV
    if not os.path.exists(config.OUTPUT_CSV):
        print(f"\n❌ Error: {config.OUTPUT_CSV} not found")
        return
    
    print(f"\n📂 Loading {config.OUTPUT_CSV}...")
    df = pd.read_csv(config.OUTPUT_CSV)
    print(f"   Found {len(df)} videos to process")
    print(f"   Using {MAX_WORKERS} parallel workers")
    
    # Process in parallel
    results = []
    
    print(f"\n🎬 Processing videos in parallel...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        futures = {executor.submit(process_single_video, row): idx 
                  for idx, row in df.iterrows()}
        
        # Collect results with progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"\n⚠️  Error: {e}")
    
    # Save results
    results_df = pd.DataFrame(results)
    results_path = 'audio_extraction_results.json'
    results_df.to_json(results_path, orient='records', indent=2)
    
    # Statistics
    successful = results_df['audio_extracted'].sum()
    total_duration = results_df['audio_duration'].sum()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 2 COMPLETE - Audio Extraction (PARALLEL)")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   Total videos: {len(results_df)}")
    print(f"   Successfully extracted: {successful}")
    print(f"   Failed: {len(results_df) - successful}")
    print(f"   Total audio duration: {total_duration // 60} minutes")
    print(f"   Estimated Whisper cost: ${(total_duration / 60) * 0.006:.2f}")
    print(f"\n📝 Results saved to: {results_path}")
    print("=" * 60)

if __name__ == "__main__":
    process_videos_parallel()
