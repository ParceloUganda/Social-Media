# 👨‍💻 Developer Guide - Social Media Viral Database

## 📞 Contact: Mutikanga Mark - +256769704668
*Call for OpenAI API key or any questions*

---

## 🎯 What This Project Does

AI pipeline that processes 1,286 viral videos (Instagram & TikTok) to create a marketing database with:
- Audio transcriptions (supports Luganda language)
- Product classifications (luxury levels)
- Demographics & targeting data

**Status:** Phase 1 done (1,286 videos parsed). You need to run Phases 2-5.

**Cost:** ~$24 total | **Time:** ~5 days (includes 24-hour batch processing waits)

---

## ⚡ Quick Setup (30 minutes)

### 1. Get OpenAI API Key
- **Option A:** Get your own at https://platform.openai.com/api-keys (need $25+ credits)
- **Option B:** Contact Mutikanga Mark: +256769704668

### 2. Install Dependencies

**macOS:**
```bash
brew install ffmpeg
pip install -r requirements.txt
pip install yt-dlp
```

**Ubuntu:**
```bash
sudo apt install ffmpeg
pip install -r requirements.txt
pip install yt-dlp
```

### 3. Configure API Key
```bash
cp .env.example .env
nano .env  # Add: OPENAI_API_KEY=sk-your-key-here
```

### 4. Verify Setup
```bash
ffmpeg -version
yt-dlp --version
python -c "import config; print('✅ Ready!' if config.OPENAI_API_KEY else '❌ No API key')"
```

---

## 🚀 How to Run the Pipeline

### Phase 2: Extract Audio (2-3 hours, $0)
```bash
python scripts/phase2_audio_extractor.py
```
Downloads 1,286 videos and extracts audio to MP3. Output: `output/extracted_audio/` folder

### Phase 3: Transcribe Audio (1-2 hours, ~$19)
```bash
python scripts/phase3_transcriber.py
```
Transcribes audio using OpenAI Whisper. Output: `output/transcripts/` + `output/transcriptions.csv`

### Phase 4: Classify Products (5 min + 24h wait, ~$5)
```bash
# Day 1: Submit batch job
python scripts/phase4_classifier.py

# Day 2: Retrieve results (after 24 hours)
python scripts/phase4_classifier.py
```
Uses GPT-4 Batch API (50% savings). Output: `output/classifications.csv`

### Phase 5: Generate Final CSV (< 5 min, $0)
```bash
python scripts/phase5_final_csv.py
```
Merges all data. Output: `output/viral_database_FINAL.csv` ← **This is your final deliverable!**

---

## 📊 Project Structure

```
Social Media/
├── 📄 README.md                    Main documentation
├── 📄 DEVELOPER_README.md          This file
├── 📄 .env                         Your API key (create from .env.example)
├── 📄 requirements.txt             Python dependencies
│
├── 📂 scripts/                     Pipeline phases
│   ├── phase1_data_parser.py      ✅ DONE (1,286 videos parsed)
│   ├── phase2_audio_extractor.py  ⏳ Download & extract audio
│   ├── phase3_transcriber.py      ⏳ Transcribe with Whisper
│   ├── phase4_classifier.py       ⏳ Classify with GPT-4
│   ├── phase5_final_csv.py        ⏳ Generate final CSV
│   ├── phase2_audio_extractor_parallel.py
│   └── phase3_transcriber_parallel.py
│
├── 📂 utils/                       Utility scripts
│   ├── check_full_status.py       Check progress
│   ├── create_subset.py           Create test subset
│   └── retry_transcriptions.py    Retry failures
│
├── 📂 config/                      Configuration
│   └── config.py                  Settings & paths
│
├── 📂 data/                        Input data
│   ├── instagram.json             Instagram (278 videos)
│   └── tiktok.json                TikTok (1,008 videos)
│
├── 📂 output/                      Generated files
│   ├── viral_database.csv         ✅ Phase 1 (exists)
│   ├── extracted_audio/           Phase 2 output
│   ├── transcripts/               Phase 3 output
│   ├── transcriptions.csv         Phase 3 summary
│   ├── classifications.csv        Phase 4 output
│   └── viral_database_FINAL.csv   Phase 5 ← DELIVERABLE
│
├── 📂 docs/                        Documentation
│   ├── PROJECT_SUMMARY.md
│   ├── QUICKSTART.md
│   └── OPENAI_API_RESEARCH.md
│
└── 📂 logs/                        Log files
```

---

## 💰 Cost & Time Breakdown

| Phase | What It Does | Time | Cost |
|-------|--------------|------|------|
| 1 | Parse JSON → CSV | - | ✅ Done |
| 2 | Download videos, extract audio | 2-3h | $0 |
| 3 | Whisper transcription | 1-2h | ~$19 |
| 4 | GPT-4 classification (batch) | 24h | ~$5 |
| 5 | Generate final CSV | <5m | $0 |
| **TOTAL** | | **~50h** | **~$24** |

**Note:** Timeline includes two 24-hour batch processing waits

---

## 🧪 Test First (Recommended)

Before processing all 1,286 videos, test with a subset:

```bash
# Create test subset
python utils/create_subset.py

# Run phases 2-5 on subset
python scripts/phase2_audio_extractor.py
python scripts/phase3_transcriber.py
python scripts/phase4_classifier.py
# Wait 24 hours
python scripts/phase4_classifier.py
python scripts/phase5_final_csv.py

# Test cost: ~$0.60, Time: ~1 hour
```

---

## 🛠️ Utility Commands

```bash
# Check processing status
python utils/check_full_status.py

# Create test subset
python utils/create_subset.py

# Retry failed transcriptions
python utils/retry_transcriptions.py

# Check OpenAI API balance
# Visit: https://platform.openai.com/usage

# Check batch job status
# Visit: https://platform.openai.com/batches
```

---

## 🐛 Troubleshooting

### "OpenAI API key not set"
```bash
nano .env  # Add: OPENAI_API_KEY=sk-your-key-here
```

### "ffmpeg not found"
```bash
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

### "yt-dlp not found"
```bash
pip install yt-dlp
```

### Video downloads fail
- Some videos may be private/deleted (normal, pipeline continues)
- Re-run the command - it skips already processed files

### Transcription fails
- Check API credits at https://platform.openai.com/usage
- Run `python retry_transcriptions.py` to retry failures

### Batch job taking too long
- Batch API takes up to 24 hours
- Check status: `python phase4_classifier.py`
- Or visit: https://platform.openai.com/batches

---

## 📦 Final Deliverable

You need to deliver `viral_database_FINAL.csv` with these columns:

| Column | Example |
|--------|---------|
| caption | "Lx600 petrol 2023 Ugx 780m" |
| account_name | "lemax__autos" |
| view_count | 110900 |
| source_url | Video URL |
| product_category | "high-end" / "medium-end" / "low-end" |
| product_name | "Lexus LX600 Petrol 2023" |
| transcript | Audio transcription text |
| platform | "TikTok" / "Instagram" |
| intended_age_category | "35-45" |
| intended_spending_category | "luxury" |
| likes_count | 9653 |
| comments_count | 318 |
| detected_language | "en" / "lg" (Luganda) |
| brand | "Lexus" |
| product_type | "SUV" |

**Target:** >95% success rate on transcriptions and classifications

---

## 🚀 Push to GitHub

When done, push code to: https://github.com/ParceloUganda/Social-Media.git

```bash
git init
git add .
git status  # VERIFY .env is NOT listed (it's in .gitignore)

git commit -m "Social Media Viral Database Pipeline - Complete"

git remote add origin https://github.com/ParceloUganda/Social-Media.git
git branch -M main
git push -u origin main
```

**IMPORTANT:** Never commit `.env` file (your API key)! Verify it's in `.gitignore`.

---

## ✅ Success Checklist

- [ ] Environment setup complete (API key configured)
- [ ] Phase 2 complete (audio extracted)
- [ ] Phase 3 complete (transcriptions done)
- [ ] Phase 4 complete (classifications done)
- [ ] Phase 5 complete (final CSV generated)
- [ ] `viral_database_FINAL.csv` has all 1,286 videos with data
- [ ] >95% success rate on transcriptions
- [ ] >95% success rate on classifications
- [ ] Code pushed to GitHub (without .env file)

---

## 💡 Key Points

1. **API Key Required:** You MUST have your own OpenAI API key
2. **Checkpointing:** All phases resume from where they stopped if interrupted
3. **Cost Control:** Test with subset first (~$0.60) before full run (~$24)
4. **Be Patient:** Batch API takes 24 hours - this is normal
5. **Some Failures Expected:** A few videos may fail (deleted/private) - target >95% success

---

## 📞 Need Help?

**Mutikanga Mark: +256769704668**

Call for:
- OpenAI API key assistance
- Technical questions
- Project clarifications
- Troubleshooting help

---

## 🎯 Summary

**Your Tasks:**
1. Set up environment (30 min)
2. Run Phase 2 (2-3 hours)
3. Run Phase 3 (1-2 hours, ~$19)
4. Submit Phase 4 batch (5 min, ~$5)
5. Wait 24 hours
6. Retrieve Phase 4 results
7. Run Phase 5 (<5 min)
8. Push to GitHub

**Total Time:** ~5 days (includes waits)  
**Total Cost:** ~$24  
**Deliverable:** `viral_database_FINAL.csv` + GitHub repo

**Start here:** Run the setup commands above, then execute phases 2-5 in order.

Good luck! 🚀
