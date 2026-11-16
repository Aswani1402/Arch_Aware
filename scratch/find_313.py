import json

tf_file = r'C:\Users\Aswini_Ayappan\.gemini\antigravity\brain\45f9c0e2-f31d-4a6d-895b-d7a5259ba7f9\.system_generated\logs\transcript_full.jsonl'
with open(tf_file, 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        content = obj.get('content', '')
        if '313 passed' in content:
            print(f"STEP {obj.get('step_index')} content snippet:")
            print(content[:500])

