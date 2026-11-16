import json

transcript_path = r'C:\Users\Aswini_Ayappan\.gemini\antigravity\brain\45f9c0e2-f31d-4a6d-895b-d7a5259ba7f9\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get('step_index')
        if idx in (6985, 6986, 7196, 7197):
            print(f"=== STEP {idx} ({obj.get('type')}) ===")
            print(str(obj.get('content'))[:500])

