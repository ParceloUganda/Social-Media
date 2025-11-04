# OpenAI API Research Summary

## 📝 Documentation Sources
1. Speech to Text: https://platform.openai.com/docs/guides/speech-to-text
2. Batch API: https://platform.openai.com/docs/guides/batch
3. Pricing: https://platform.openai.com/docs/pricing

---

## 🎙️ Whisper Speech-to-Text API

### Models Available
- **whisper-1** (legacy): Original Whisper model
- **gpt-4o-transcribe**: Newer transcription model
- **gpt-4o-mini-transcribe**: Cheaper transcription model

### Key Features
1. **Language Support**: 99+ languages with automatic detection
   - Auto-detect language with `language=None`
   - Can specify language code (e.g., 'en', 'es')
   - Luganda may not be explicitly supported, but auto-detect should work

2. **Transcription Options**:
   - Standard transcription: Single API call per file
   - Streaming transcription: Real-time transcription with `stream=True`
   - Response formats: `text`, `json`, `verbose_json`, `diarized_json` (with speaker labels)

3. **File Constraints**:
   - Maximum file size: 25MB
   - Maximum duration: ~2 hours of audio
   - Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

4. **Prompting**:
   - Can provide a `prompt` parameter to help with:
     - Uncommon words, acronyms, product names
     - Context about the content
     - Style guidance

5. **Timestamps**:
   - Request `timestamp_granularities=['segment']` for segment-level timestamps
   - Useful for understanding where in audio specific content appears

### Pricing
- **whisper-1**: $0.006 per minute
- **gpt-4o-transcribe**: Likely similar pricing (check current docs)
- **NO BATCH API DISCOUNT** for Whisper currently (as of documentation review)

### Code Example
```python
from openai import OpenAI
client = OpenAI()

# Standard transcription
with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=None,  # Auto-detect
        response_format="verbose_json",
        timestamp_granularities=["segment"]
    )
    
print(transcript.text)
print(transcript.language)  # Detected language
```

---

## 🔄 Batch API

### Overview
The Batch API allows you to send **async groups of API requests** with:
- **50% lower cost** than synchronous APIs
- **24-hour processing window**
- **Separate rate limits** (doesn't affect your standard rate limits)

### Supported Endpoints
- `/v1/chat/completions` (GPT models)
- `/v1/embeddings`
- **NOT** `/v1/audio/transcriptions` (Whisper doesn't support batch yet)

### Limitations
- Max 50,000 requests per batch
- Max 200MB batch input file size
- Results may return out of order (use `custom_id` to match)
- 24-hour completion window, then batch expires

### Workflow
1. **Prepare** batch requests file (`.jsonl` format)
2. **Upload** file to OpenAI Files API
3. **Create** batch job
4. **Monitor** batch status
5. **Retrieve** results when complete

### Input Format (.jsonl)
```jsonl
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o", "messages": [{"role": "user", "content": "Classify this product..."}]}}
{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o", "messages": [{"role": "user", "content": "Analyze demographics..."}]}}
```

### Pricing Example
| Model | Standard Input | Standard Output | Batch Input | Batch Output |
|-------|----------------|-----------------|-------------|--------------|
| GPT-4o | $2.50/1M | $10.00/1M | $1.25/1M | $5.00/1M |
| GPT-4o Mini | $0.150/1M | $0.600/1M | $0.075/1M | $0.300/1M |

**50% discount on both input and output tokens!**

### Code Example
```python
from openai import OpenAI
client = OpenAI()

# 1. Upload batch file
batch_file = client.files.create(
    file=open("batch_requests.jsonl", "rb"),
    purpose="batch"
)

# 2. Create batch job
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)

# 3. Check status
batch_status = client.batches.retrieve(batch.id)
print(batch_status.status)  # validating, in_progress, completed, failed

# 4. Get results when complete
if batch_status.status == "completed":
    result_file = client.files.content(batch_status.output_file_id)
    results = result_file.text
```

---

## 🎯 Recommended Implementation Strategy

### For Whisper Transcription
❌ **Batch API NOT available** - Use standard API with:
1. Sequential processing with retry logic
2. Progress tracking and checkpoints
3. Rate limiting (respectful delays)
4. Cost: $0.006/minute

### For GPT-4 Classification
✅ **USE Batch API** for 50% savings:
1. After transcription, create batch classification requests
2. Submit all videos in one batch
3. Process results next day
4. Cost: 50% of standard pricing

### Cost Estimation Example
**100 videos, 3 minutes average**:
- Whisper transcription: 100 × 3 × $0.006 = **$1.80**
- GPT-4o classification (standard): ~$0.50
- GPT-4o classification (batch): ~$0.25
- **Total: ~$2.05** with batch optimization

---

## 🌍 Luganda Language Handling

### Challenge
Luganda is a Bantu language spoken in Uganda. Whisper supports 99+ languages but may not explicitly list Luganda.

### Solution Approach
1. **Auto-detect first**: Use `language=None` to let Whisper detect
2. **Check results**: If detection fails or quality is poor:
   - Try with `language='en'` and provide Luganda context in prompt
   - Use GPT-4 post-processing to improve/translate
3. **Hybrid approach**: 
   ```python
   # Step 1: Transcribe with auto-detect
   transcript_raw = transcribe(audio, language=None)
   
   # Step 2: If language is 'unknown' or confidence low
   if needs_improvement(transcript_raw):
       # Use GPT-4 to improve/translate
       improved = gpt4_improve(transcript_raw, context="Ugandan car dealer")
   ```

---

## ⚙️ Libraries & Tools

### Video/Audio Download
- **yt-dlp**: Universal downloader for TikTok, Instagram, YouTube
  ```bash
  pip install yt-dlp
  yt-dlp -f best -o "video.mp4" <url>
  ```

### Audio Processing
- **ffmpeg**: Audio extraction and conversion
  ```bash
  brew install ffmpeg
  ffmpeg -i video.mp4 -vn -ar 16000 -ac 1 -b:a 32k audio.mp3
  ```

### Python Libraries
```python
# requirements.txt
openai>=1.0.0
yt-dlp>=2024.0.0
ffmpeg-python>=0.2.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

---

## 🚀 Implementation Phases

### Phase 1: Data Extraction ✅
- Parse JSON files
- Create initial CSV
- Identify video URLs

### Phase 2: Audio Extraction
- Download videos with yt-dlp
- Extract audio with ffmpeg
- Validate audio quality

### Phase 3: Transcription (Standard API)
- Use Whisper API sequentially
- Handle Luganda detection
- Store transcripts with metadata

### Phase 4: Classification (Batch API)
- Create batch requests for GPT-4
- Classify products, demographics, price levels
- 50% cost savings!

### Phase 5: Final CSV
- Merge all data
- Generate comprehensive database
- Quality checks

---

## 💡 Best Practices

1. **Error Handling**: Robust retry logic with exponential backoff
2. **Progress Tracking**: Save intermediate results (don't re-process)
3. **Rate Limiting**: Respect API limits, add delays
4. **Cost Monitoring**: Track token usage and costs
5. **Logging**: Detailed logs for debugging
6. **Validation**: Check output quality at each step

---

## 📊 Expected Performance

**For ~100 videos (avg 3 min each)**:
- Download time: ~30-60 minutes (network dependent)
- Transcription time: ~10-20 minutes (API processing)
- Batch classification: 24 hours (async)
- Total cost: ~$2-3
- **Batch savings**: ~$0.25-0.50 per 100 videos

This approach balances speed, cost, and quality for your marketing analytics needs!
