# 🎬 Social Media Viral Database Builder

AI-powered pipeline to analyze social media content (Instagram & TikTok) and create a comprehensive viral marketing database with audio transcription, product classification, and demographic analysis.

## 📞 Contact & Support
**Project Owner:** Mutikanga Mark  
**Phone:** +256769704668  
**Contact for:** OpenAI API key assistance, project questions, technical support

**Important:** You will need your own OpenAI API key to run this pipeline. If you don't have one, please contact Mutikanga Mark at the number above.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pipeline Phases](#pipeline-phases)
- [Cost Estimation](#cost-estimation)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This pipeline processes social media videos to extract:
- **Audio transcriptions** (via OpenAI Whisper)
- **Product classifications** (luxury level: low/medium/high-end)
- **Demographic targeting** (age & spending categories)
- **Marketing insights** (brand, features, marketing angles)

**Perfect for:** Marketing teams, content analysts, social media managers analyzing viral content.

---

## ✨ Features

### 🎙️ Multi-language Transcription
- OpenAI Whisper API with 99+ language support
- **Luganda language handling** (for Uganda-specific content)
- Auto-detect language or specify explicitly
- Timestamp support for segment analysis

### 🤖 AI-Powered Classification
- **GPT-4 Batch API** (50% cost savings!)
- Product categorization (low/medium/high-end luxury)
- Age demographic targeting
- Spending category analysis
- Brand and feature extraction

### 📊 Comprehensive Data Export
- CSV format compatible with Excel, Google Sheets
- Matches your viral database structure (see sample image)
- Sortable by views, engagement, categories
- Ready for marketing analysis

### 🔧 Robust Processing
- Resume capability (checkpoints after each phase)
- Error handling and retry logic
- Progress tracking
- Cost estimation and monitoring

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- ffmpeg (for audio processing)
- yt-dlp (for video downloading)

### Step 1: Install System Dependencies

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Step 2: Install Python Dependencies

```bash
# Clone or navigate to project directory
cd "/Volumes/ Lachie Hd/Parcelo_Uganda/Parcelo Social Media"

# Install Python packages
pip install -r requirements.txt
```

### Step 3: Set Up Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use any text editor
```

Add your API key to `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

### File Paths
```python
INSTAGRAM_JSON = 'instagram.json'  # Your Instagram data
TIKTOK_JSON = 'tiktok.json'        # Your TikTok data
OUTPUT_CSV = 'viral_database.csv'   # Initial output
```

### Luxury Price Thresholds (UGX)
```python
LOW_END_MAX = 150_000_000      # 0-150M UGX
MEDIUM_END_MAX = 400_000_000   # 150-400M UGX
# HIGH_END = 400M+ UGX
```

### Model Selection
```python
WHISPER_MODEL = 'whisper-1'        # Or 'gpt-4o-transcribe'
GPT_MODEL = 'gpt-4o'               # Or 'gpt-4o-mini' for cheaper
```

---

## 🚀 Usage

### Quick Start - Run All Phases

```bash
# Phase 1: Parse JSON data
python phase1_data_parser.py

# Phase 2: Download videos and extract audio
python phase2_audio_extractor.py

# Phase 3: Transcribe audio with Whisper
python phase3_transcriber.py

# Phase 4: Classify products with GPT-4 (Batch API)
python phase4_classifier.py

# Wait 24 hours for batch processing...

# Check batch status
python phase4_classifier.py

# Phase 5: Generate final CSV
python phase5_final_csv.py
```

### Detailed Usage

#### Phase 1: Data Parsing
```bash
python phase1_data_parser.py
```
**Output:** `viral_database.csv` with basic info (caption, account, views, URL, platform)

**What it does:**
- Reads `instagram.json` and `tiktok.json`
- Extracts video metadata
- Creates initial CSV structure

#### Phase 2: Audio Extraction
```bash
python phase2_audio_extractor.py
```
**Output:** MP3 audio files in `extracted_audio/`, processing log in `audio_extraction_results.json`

**What it does:**
- Downloads videos using yt-dlp
- Extracts audio using ffmpeg (16kHz mono, optimized for Whisper)
- Calculates audio durations
- Estimates transcription costs

**Time:** ~1-2 minutes per video (network dependent)

#### Phase 3: Transcription
```bash
python phase3_transcriber.py
```
**Output:** Transcripts in `transcripts/` folder + `transcriptions.csv`

**What it does:**
- Transcribes each audio file with Whisper
- Auto-detects language (handles Luganda!)
- Stores transcripts with metadata
- Reports detected languages

**Cost:** $0.006 per minute of audio  
**Time:** ~30 seconds per minute of audio

**Example:** 100 videos × 3 min = 300 min = $1.80

#### Phase 4: Classification (Batch)
```bash
python phase4_classifier.py
```
**Output:** `batch_classification_status.json` → `classifications.csv` (after 24h)

**What it does:**
- Creates batch classification requests
- Uploads to OpenAI Batch API
- Submits job for async processing
- **Saves 50% on costs!**

**First run:** Submits batch job  
**Subsequent runs:** Checks status & retrieves results when complete

**Cost:** ~$0.25 per 100 videos (with batch discount)  
**Time:** 24 hours (async processing)

#### Phase 5: Final CSV
```bash
python phase5_final_csv.py
```
**Output:** `viral_database_FINAL.csv` - Your complete marketing database!

**What it does:**
- Merges all data from phases 1-4
- Fills in missing values
- Sorts by view count
- Generates final statistics

---

## 📊 Pipeline Phases

```
┌─────────────────┐
│  instagram.json │
│   tiktok.json   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   PHASE 1: Data Parser          │
│   • Parse JSON files             │
│   • Extract metadata             │
│   • Create initial CSV           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   PHASE 2: Audio Extractor      │
│   • Download videos (yt-dlp)    │
│   • Extract audio (ffmpeg)      │
│   • Prepare for transcription   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   PHASE 3: Transcriber           │
│   • Whisper API transcription   │
│   • Language detection           │
│   • Handle Luganda content       │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   PHASE 4: Classifier (Batch)   │
│   • GPT-4 product analysis      │
│   • Demographic classification  │
│   • 50% cost savings!            │
│   • 24h processing window        │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   PHASE 5: Final CSV             │
│   • Merge all data               │
│   • Generate viral database      │
│   • Export for analysis          │
└─────────────────────────────────┘
```

---

## 💰 Cost Estimation

### Sample Calculation (100 videos, 3 min avg)

| Phase | Service | Unit Cost | Quantity | Total |
|-------|---------|-----------|----------|-------|
| **3** | Whisper Transcription | $0.006/min | 300 min | **$1.80** |
| **4** | GPT-4o Classification (Batch) | ~$0.0025/video | 100 videos | **$0.25** |
| | | | **TOTAL** | **~$2.05** |

**Without Batch API:** ~$2.55  
**With Batch API (50% off):** ~$2.05  
**💰 Savings:** $0.50 per 100 videos

### Cost Scaling

| Videos | Audio Minutes | Whisper Cost | GPT-4 (Batch) | Total Cost |
|--------|---------------|--------------|---------------|------------|
| 10 | 30 | $0.18 | $0.03 | **$0.21** |
| 50 | 150 | $0.90 | $0.13 | **$1.03** |
| 100 | 300 | $1.80 | $0.25 | **$2.05** |
| 500 | 1500 | $9.00 | $1.25 | **$10.25** |
| 1000 | 3000 | $18.00 | $2.50 | **$20.50** |

---

## 🎓 Output Format

### Final CSV Columns

| Column | Description | Example |
|--------|-------------|---------|
| `caption` | Original post caption | "Lx600 petrol 2023 Ugx 780m" |
| `account_name` | Social media account | "lemax__autos" |
| `view_count` | Number of views | 110900 |
| `source_url` | Original video URL | "https://www.tiktok.com/@lemax__autos/video/..." |
| `product_category` | Luxury level | "high-end" |
| `product_name` | Specific product | "Lexus LX600 Petrol 2023" |
| `transcript` | Audio transcription | "This is a Lexus LX600..." |
| `platform` | Social platform | "TikTok" / "Instagram" |
| `intended_age_category` | Target age range | "35-45" |
| `intended_spending_category` | Spending level | "luxury" |
| `likes_count` | Number of likes | 9653 |
| `comments_count` | Number of comments | 318 |
| `detected_language` | Transcribed language | "en" / "lg" (Luganda) |
| `brand` | Product brand | "Lexus" |
| `product_type` | Vehicle type | "SUV" |

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **"OpenAI API key not set"**
**Solution:**
```bash
# Edit .env file
nano .env

# Add your key
OPENAI_API_KEY=sk-your-actual-key-here
```

#### 2. **"yt-dlp not found"**
**Solution:**
```bash
pip install yt-dlp
# Or
brew install yt-dlp
```

#### 3. **"ffmpeg not found"**
**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

#### 4. **Video download fails**
**Common reasons:**
- Video is private/deleted
- Rate limiting
- URL expired

**Solution:** Check `audio_extraction_results.json` for specific errors

#### 5. **Luganda transcription poor quality**
**Solution:** The pipeline handles this automatically, but you can:
- Check `detected_language` in transcriptions
- Review transcript quality manually
- Consider post-processing with GPT-4 (add to Phase 3)

#### 6. **Batch still processing after 24h**
**Solution:**
```bash
# Check status
python phase4_classifier.py

# If stuck, check OpenAI dashboard
# https://platform.openai.com/batches
```

### Debug Mode

Add logging for debugging:
```python
# In any phase file, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Additional Resources

- **OpenAI Whisper Docs:** https://platform.openai.com/docs/guides/speech-to-text
- **Batch API Guide:** https://platform.openai.com/docs/guides/batch
- **API Research:** See `OPENAI_API_RESEARCH.md` for detailed findings
- **yt-dlp Documentation:** https://github.com/yt-dlp/yt-dlp

---

## 🔗 GitHub Repository

**Repository:** https://github.com/ParceloUganda/Social-Media.git

### Clone This Project
```bash
git clone https://github.com/ParceloUganda/Social-Media.git
cd Social-Media
```

### Setup After Cloning
```bash
# Install dependencies
pip install -r requirements.txt
pip install yt-dlp

# Create .env file with your API key
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

See [GIT_SETUP.md](./GIT_SETUP.md) for detailed Git instructions.

---

## 🤝 Support

For issues or questions:
1. Check this README and [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
2. Review `OPENAI_API_RESEARCH.md` for API details
3. Check phase-specific error messages and `*.log` files
4. Verify API key and credits at https://platform.openai.com/usage
5. Contact Mutikanga Mark: +256769704668

---

## 📝 License

This project is for internal marketing analysis use.

---

## 🎉 Success!

Once complete, you'll have a comprehensive viral marketing database with:
- ✅ Transcribed audio content
- ✅ Product classifications
- ✅ Demographic insights
- ✅ Engagement metrics
- ✅ Ready for marketing strategy!

**Happy analyzing! 🚀**
