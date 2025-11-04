"""
Phase 2: Audio Extraction - Download videos and extract audio
Uses yt-dlp to download videos and ffmpeg to extract audio.
"""

import os
import subprocess
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import config
import json
import hashlib

def get_video_id(url: str) -> str:
    """Generate a unique ID for a video URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def download_video_ytdlp(url: str, output_path: str, video_id: str) -> bool:
    """
    Download video using yt-dlp.
    Returns True if successful, False otherwise.
    """
    try:
        # yt-dlp command with options optimized for Instagram and TikTok
        cmd = [
            'yt-dlp',
            '--no-playlist',
            '--no-warnings',
            '--quiet',
            '--progress',
            '-f', 'best',  # Best quality
            '-o', output_path,
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"   ⚠️  Timeout downloading {video_id}")
        return False
    except Exception as e:
        print(f"   ⚠️  Error downloading {video_id}: {e}")
        return False

def extract_audio_ffmpeg(video_path: str, audio_path: str) -> bool:
    """
    Extract audio from video using ffmpeg.
    Returns True if successful, False otherwise.
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # MP3 codec
            '-ar', '16000',  # 16kHz sample rate (optimal for Whisper)
            '-ac', '1',  # Mono
            '-b:a', '32k',  # 32kbps (keeps file size small)
            '-y',  # Overwrite output
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0 and os.path.exists(audio_path)
        
    except subprocess.TimeoutExpired:
        print(f"   ⚠️  Timeout extracting audio")
        return False
    except Exception as e:
        print(f"   ⚠️  Error extracting audio: {e}")
        return False

def get_audio_duration(audio_path: str) -> int:
    """Get audio duration in seconds using ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return int(float(result.stdout.strip()))
        return 0
    except:
        return 0

def process_videos():
    """Main function to download videos and extract audio."""
    print("=" * 60)
    print("PHASE 2: Audio Extraction")
    print("=" * 60)
    
    # Check if required tools are installed
    print("\n🔍 Checking dependencies...")
    tools = ['yt-dlp', 'ffmpeg', 'ffprobe']
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, timeout=5)
            print(f"   ✅ {tool} found")
        except:
            print(f"   ❌ {tool} not found - Please install it")
            print(f"      Install with: brew install {tool}" if tool != 'yt-dlp' else "      Install with: pip install yt-dlp")
            return
    
    # Load CSV
    if not os.path.exists(config.OUTPUT_CSV):
        print(f"\n❌ Error: {config.OUTPUT_CSV} not found. Run phase1_data_parser.py first.")
        return
    
    print(f"\n📂 Loading {config.OUTPUT_CSV}...")
    df = pd.read_csv(config.OUTPUT_CSV)
    print(f"   Found {len(df)} videos to process")
    
    # Track processing results
    results = []
    
    print(f"\n🎬 Processing videos...")
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
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
            results.append(result)
            continue
        
        # Download video
        if download_video_ytdlp(row['source_url'], video_path, video_id):
            result['video_downloaded'] = True
            
            # Extract audio
            if extract_audio_ffmpeg(video_path, audio_path):
                result['audio_extracted'] = True
                result['audio_duration'] = get_audio_duration(audio_path)
                result['audio_path'] = audio_path
                
                # Clean up video file to save space
                try:
                    os.remove(video_path)
                except:
                    pass
        
        results.append(result)
    
    # Save processing results
    results_df = pd.DataFrame(results)
    results_path = 'audio_extraction_results.json'
    results_df.to_json(results_path, orient='records', indent=2)
    
    # Print statistics
    successful = results_df['audio_extracted'].sum()
    total_duration = results_df['audio_duration'].sum()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 2 COMPLETE - Audio Extraction")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   Total videos: {len(results_df)}")
    print(f"   Successfully extracted: {successful}")
    print(f"   Failed: {len(results_df) - successful}")
    print(f"   Total audio duration: {total_duration // 60} minutes")
    print(f"   Estimated Whisper cost: ${(total_duration / 60) * 0.006:.2f}")
    print(f"\n📝 Results saved to: {results_path}")
    print(f"💾 Audio files in: {config.AUDIO_DIR}/")
    print("\n🔜 Next: Run phase3_transcriber.py to transcribe audio with Whisper")
    print("=" * 60)

if __name__ == "__main__":
    process_videos()
