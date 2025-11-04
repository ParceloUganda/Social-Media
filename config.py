import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# File paths
INSTAGRAM_JSON = 'instagram.json'
TIKTOK_JSON = 'tiktok.json'
OUTPUT_CSV = 'viral_database.csv'  # Full dataset - all accounts
TEMP_DIR = 'temp_media'
AUDIO_DIR = 'extracted_audio'
TRANSCRIPTS_DIR = 'transcripts'

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
