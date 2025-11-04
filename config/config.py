import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# File paths (relative to project root)
INSTAGRAM_JSON = PROJECT_ROOT / 'data' / 'instagram.json'
TIKTOK_JSON = PROJECT_ROOT / 'data' / 'tiktok.json'
OUTPUT_CSV = PROJECT_ROOT / 'output' / 'viral_database.csv'
TEMP_DIR = PROJECT_ROOT / 'output' / 'temp_media'
AUDIO_DIR = PROJECT_ROOT / 'output' / 'extracted_audio'
TRANSCRIPTS_DIR = PROJECT_ROOT / 'output' / 'transcripts'

# Luxury categorization thresholds (UGX)
LOW_END_MAX = int(os.getenv('LOW_END_MAX', 150_000_000))
MEDIUM_END_MAX = int(os.getenv('MEDIUM_END_MAX', 400_000_000))

# Processing settings
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))
MAX_AUDIO_DURATION = int(os.getenv('MAX_AUDIO_DURATION', 7200))

# OpenAI Model settings
WHISPER_MODEL = 'whisper-1'
GPT_MODEL = 'gpt-4o-mini'  # Using mini version to avoid token limits

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
