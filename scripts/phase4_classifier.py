"""
Phase 4: Product Classification - Use GPT-4 to classify products and demographics
Uses Batch API for 50% cost savings.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import json
import time
import pandas as pd
from openai import OpenAI
from typing import Dict, List
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

CLASSIFICATION_PROMPT = """You are an expert at analyzing social media product content. 
Analyze the following social media post and identify the product being promoted.

POST DETAILS:
Platform: {platform}
Caption: {caption}
Transcript: {transcript}

Provide your analysis in this exact JSON format:
{{
    "product_name": "Specific product name with model/details (e.g., 'Lexus LX600 Petrol 2023', 'LED Sign Board 60x40', 'Wireless Earbuds Pro')",
    "product_category": "low-end|medium-end|high-end",
    "price_ugx": estimated_price_in_ugx_or_null,
    "intended_age_category": "18-25|25-35|35-45|45-55|55+",
    "intended_spending_category": "budget|mid-range|premium|luxury|ultra-luxury",
    "product_type": "vehicle|electronics|gadget|led_sign|lighting|toy|smart_device|accessory|home_product|other",
    "brand": "brand_name (e.g., Toyota, Samsung, Apple, etc.)",
    "key_features": ["feature1", "feature2"],
    "marketing_angle": "brief description of how product is marketed",
    "niche": "automotive|electronics|lighting|gadgets|home_goods|other"
}}

PRICING GUIDELINES (UGX) - Adjust context based on product type:
- For VEHICLES: Low-end (0-150M), Medium-end (150M-400M), High-end (400M+)
- For ELECTRONICS/GADGETS: Low-end (0-500K), Medium-end (500K-5M), High-end (5M+)
- For LED SIGNS/LIGHTING: Low-end (0-1M), Medium-end (1M-10M), High-end (10M+)

Be specific with product names. Extract price from caption if mentioned (look for "Ugx", "UGX", numbers followed by "m" or "M")."""

def create_classification_request(video_id: str, row: pd.Series, custom_id: str) -> Dict:
    """Create a single classification request for batch processing."""
    prompt = CLASSIFICATION_PROMPT.format(
        platform=row['platform'],
        caption=row.get('caption', 'N/A'),
        transcript=row.get('transcript_text', 'N/A')
    )
    
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": config.GPT_MODEL,
            "messages": [
                {"role": "system", "content": "You are an expert product analyst specializing in social media marketing and e-commerce. Analyze products from various niches including automotive, electronics, gadgets, lighting, and consumer goods. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
    }

def create_batch_file(transcripts_df: pd.DataFrame) -> str:
    """Create a .jsonl batch file for classification."""
    batch_requests = []
    
    for idx, row in transcripts_df.iterrows():
        if not row.get('transcript_text') or row.get('transcript_text') == '':
            continue
            
        custom_id = f"classify-{row['video_id']}"
        request = create_classification_request(row['video_id'], row, custom_id)
        batch_requests.append(request)
    
    # Save to .jsonl file
    batch_file_path = config.PROJECT_ROOT / 'output' / 'batch_classification_requests.jsonl'
    with open(batch_file_path, 'w', encoding='utf-8') as f:
        for req in batch_requests:
            f.write(json.dumps(req) + '\n')
    
    return batch_file_path

def submit_batch_job(batch_file_path: str) -> str:
    """Upload batch file and create batch job."""
    print(f"\n📤 Uploading batch file: {batch_file_path}")
    
    # Upload file
    with open(batch_file_path, 'rb') as f:
        batch_input_file = client.files.create(
            file=f,
            purpose="batch"
        )
    
    print(f"   ✅ File uploaded: {batch_input_file.id}")
    
    # Create batch job
    print(f"\n🚀 Creating batch job...")
    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    
    print(f"   ✅ Batch created: {batch.id}")
    print(f"   Status: {batch.status}")
    
    return batch.id

def check_batch_status(batch_id: str) -> Dict:
    """Check the status of a batch job."""
    batch = client.batches.retrieve(batch_id)
    return {
        'id': batch.id,
        'status': batch.status,
        'created_at': batch.created_at,
        'completed_at': getattr(batch, 'completed_at', None),
        'failed_at': getattr(batch, 'failed_at', None),
        'request_counts': getattr(batch, 'request_counts', {}),
        'output_file_id': getattr(batch, 'output_file_id', None),
        'error_file_id': getattr(batch, 'error_file_id', None)
    }

def retrieve_batch_results(batch_id: str) -> List[Dict]:
    """Retrieve results from a completed batch."""
    batch = client.batches.retrieve(batch_id)
    
    if batch.status != "completed":
        print(f"⚠️  Batch not completed yet. Status: {batch.status}")
        return []
    
    # Download results
    result_file_id = batch.output_file_id
    result = client.files.content(result_file_id)
    result_text = result.text
    
    # Parse JSONL results
    results = []
    for line in result_text.strip().split('\n'):
        if line:
            results.append(json.loads(line))
    
    return results

def process_batch_results(results: List[Dict]) -> pd.DataFrame:
    """Process batch results into a DataFrame."""
    processed = []
    
    for result in results:
        custom_id = result['custom_id']
        video_id = custom_id.replace('classify-', '')
        
        if result.get('error'):
            print(f"   ⚠️  Error for {video_id}: {result['error']}")
            processed.append({
                'video_id': video_id,
                'classification_success': False,
                'error': str(result['error'])
            })
            continue
        
        # Extract classification from response
        response_body = result['response']['body']
        content = response_body['choices'][0]['message']['content']
        
        try:
            classification = json.loads(content)
            classification['video_id'] = video_id
            classification['classification_success'] = True
            classification['error'] = None
            processed.append(classification)
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse JSON for {video_id}: {e}")
            processed.append({
                'video_id': video_id,
                'classification_success': False,
                'error': f'JSON parse error: {e}'
            })
    
    return pd.DataFrame(processed)

def classify_with_batch():
    """Main function to classify products using Batch API."""
    print("=" * 60)
    print("PHASE 4: Product Classification with GPT-4 (Batch API)")
    print("=" * 60)
    
    # Check API key
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("\n❌ Error: OpenAI API key not set!")
        return
    
    # Load transcriptions
    transcripts_path = config.PROJECT_ROOT / 'output' / 'transcriptions.csv'
    if not os.path.exists(transcripts_path):
        print(f"\n❌ Error: {transcripts_path} not found. Run phase3_transcriber.py first.")
        return
    
    print(f"\n📂 Loading transcriptions...")
    transcripts_df = pd.read_csv(transcripts_path)
    successful = transcripts_df[transcripts_df['success'] == True]
    print(f"   Found {len(successful)} successful transcriptions to classify")
    
    # Check if batch already exists
    batch_status_file = config.PROJECT_ROOT / 'output' / 'batch_classification_status.json'
    
    if os.path.exists(batch_status_file):
        print(f"\n📋 Found existing batch job...")
        with open(batch_status_file, 'r') as f:
            batch_info = json.load(f)
        
        batch_id = batch_info['batch_id']
        print(f"   Batch ID: {batch_id}")
        
        # Check current status
        status = check_batch_status(batch_id)
        print(f"   Status: {status['status']}")
        
        if status['status'] == 'completed':
            print(f"\n✅ Batch completed! Retrieving results...")
            results = retrieve_batch_results(batch_id)
            classifications_df = process_batch_results(results)
            
            # Save results
            output_path = config.PROJECT_ROOT / 'output' / 'classifications.csv'
            classifications_df.to_csv(output_path, index=False, encoding='utf-8')
            
            print(f"\n💾 Classifications saved to: {output_path}")
            print(f"   Total classified: {len(classifications_df)}")
            print(f"   Successful: {classifications_df['classification_success'].sum()}")
            print("\n🔜 Next: Run phase5_final_csv.py to generate final database")
        else:
            print(f"\n⏳ Batch still processing. Check back later.")
            print(f"   Request counts: {status['request_counts']}")
            print(f"   Started: {time.ctime(status['created_at'])}")
        
        return
    
    # Create new batch
    print(f"\n📝 Creating batch classification requests...")
    batch_file = create_batch_file(successful)
    print(f"   Created: {batch_file}")
    
    # Count requests
    with open(batch_file, 'r') as f:
        num_requests = sum(1 for _ in f)
    print(f"   Total requests: {num_requests}")
    
    # Estimate cost (50% discount)
    est_input_tokens = num_requests * 500  # Rough estimate
    est_output_tokens = num_requests * 300
    cost_per_1m_input = 1.25  # GPT-4o batch input
    cost_per_1m_output = 5.00  # GPT-4o batch output
    estimated_cost = (est_input_tokens / 1_000_000 * cost_per_1m_input +
                     est_output_tokens / 1_000_000 * cost_per_1m_output)
    print(f"   Estimated cost: ${estimated_cost:.2f} (with 50% batch discount)")
    
    # Submit batch
    batch_id = submit_batch_job(batch_file)
    
    # Save batch info
    batch_info = {
        'batch_id': batch_id,
        'created_at': time.time(),
        'num_requests': num_requests,
        'status': 'submitted'
    }
    with open(batch_status_file, 'w') as f:
        json.dump(batch_info, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ PHASE 4 - Batch Job Submitted")
    print("=" * 60)
    print(f"\n⏰ Processing will complete within 24 hours")
    print(f"📝 Batch ID saved to: {batch_status_file}")
    print(f"\n🔄 To check status, run this script again")
    print("=" * 60)

if __name__ == "__main__":
    classify_with_batch()
