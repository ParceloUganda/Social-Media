# 🚀 Quick Start Guide

## ✅ Phase 1 Complete!

Your initial CSV has been created with **1,286 videos**:
- 📸 Instagram: 278 videos
- 🎵 TikTok: 1,008 videos
- 👀 Total views: 4+ billion!

**File created:** `viral_database.csv`

---

## 📋 Next Steps

### Before Starting Phase 2

1. **Install system dependencies:**
   ```bash
   # Install ffmpeg (audio processing)
   brew install ffmpeg
   
   # Install yt-dlp (video downloader)
   pip install yt-dlp
   ```

2. **Set up your OpenAI API key:**
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit and add your key
   nano .env
   ```
   
   Add: `OPENAI_API_KEY=sk-your-actual-key-here`

3. **Verify installation:**
   ```bash
   # Check ffmpeg
   ffmpeg -version
   
   # Check yt-dlp
   yt-dlp --version
   
   # Check Python packages
   pip list | grep -E "openai|yt-dlp|ffmpeg"
   ```

---

## 🎬 Running the Pipeline

### Phase 2: Extract Audio (1-2 hours)
```bash
cd "/Volumes/ Lachie Hd/Parcelo_Uganda/Parcelo Social Media"
python phase2_audio_extractor.py
```

**What happens:**
- Downloads 1,286 videos
- Extracts audio to MP3
- Estimates: ~2-3 hours total

**Cost:** $0 (no API calls)

---

### Phase 3: Transcribe Audio (30-60 min)
```bash
python phase3_transcriber.py
```

**What happens:**
- Transcribes all audio with Whisper
- Detects languages (including Luganda!)
- Saves transcripts

**Estimated cost:** 
- Assume avg 2.5 min per video
- 1,286 videos × 2.5 min = 3,215 minutes
- **Cost: ~$19.29** ($0.006/min)

**Note:** You can test with a subset first! Edit `phase3_transcriber.py` to limit processing.

---

### Phase 4: Classify Products (5 min setup + 24h wait)
```bash
python phase4_classifier.py
```

**What happens:**
- Creates batch classification requests
- Uploads to OpenAI Batch API
- Processes async (24 hours)
- **Saves 50% on costs!**

**Estimated cost:**
- ~$8-10 for 1,286 classifications
- **With batch discount: ~$4-5**

**Check status:**
```bash
# Run again after 24 hours
python phase4_classifier.py
```

---

### Phase 5: Generate Final CSV (instant)
```bash
python phase5_final_csv.py
```

**What happens:**
- Merges all data
- Creates `viral_database_FINAL.csv`
- Your complete marketing database!

---

## 💰 Total Cost Estimate

| Phase | Service | Estimated Cost |
|-------|---------|----------------|
| 1 | Data parsing | $0 |
| 2 | Video/audio extraction | $0 |
| 3 | Whisper transcription | **~$19** |
| 4 | GPT-4 classification (batch) | **~$5** |
| 5 | CSV generation | $0 |
| **TOTAL** | | **~$24** |

**Without Batch API:** ~$29  
**With Batch API:** ~$24  
**Savings:** ~$5

---

## 🧪 Testing with a Subset

To test the pipeline with fewer videos:

### Option 1: Edit Phase 1 to limit videos
```python
# In phase1_data_parser.py, after parsing:
instagram_df = instagram_df.head(10)  # First 10 Instagram videos
tiktok_df = tiktok_df.head(20)        # First 20 TikTok videos
```

### Option 2: Test one platform at a time
```python
# Comment out one platform in phase1_data_parser.py
# combined_df = pd.concat([instagram_df], ignore_index=True)  # Instagram only
```

**Test run cost:**
- 30 videos × 2.5 min × $0.006 = **~$0.45** (Whisper)
- 30 classifications × $0.005 = **~$0.15** (GPT-4 batch)
- **Total: ~$0.60**

---

## 📊 Current Status

### ✅ Completed
- [x] Phase 1: Initial CSV created (1,286 videos)

### 📝 Ready to Run
- [ ] Phase 2: Audio extraction
- [ ] Phase 3: Transcription
- [ ] Phase 4: Classification (batch)
- [ ] Phase 5: Final CSV

---

## 🎯 Recommended Workflow

### For Full Dataset (1,286 videos)
1. **Morning:** Start Phase 2 (audio extraction)
2. **Afternoon:** Start Phase 3 (transcription)
3. **Evening:** Submit Phase 4 (batch job)
4. **Next Day:** Retrieve results & run Phase 5

**Timeline:** 1.5 days  
**Cost:** ~$24

### For Test Run (30 videos)
1. Edit Phase 1 to limit videos
2. Run all phases in sequence
3. Review results

**Timeline:** 2-3 hours  
**Cost:** ~$0.60

---

## 🆘 Need Help?

1. **Check README.md** for detailed documentation
2. **Review OPENAI_API_RESEARCH.md** for API details
3. **Check error messages** in console output
4. **Verify API key** in `.env` file

---

## 🎉 You're All Set!

Your data is parsed and ready. Choose your approach:
- 🚀 **Full run:** Process all 1,286 videos (~$24)
- 🧪 **Test run:** Try 30 videos first (~$0.60)

**Ready to continue? Run Phase 2:**
```bash
python phase2_audio_extractor.py
```

Good luck! 🍀
