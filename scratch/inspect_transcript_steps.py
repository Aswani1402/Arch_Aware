import json

transcript_path = r'C:\Users\Aswini_Ayappan\.gemini\antigravity\brain\45f9c0e2-f31d-4a6d-895b-d7a5259ba7f9\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get('step_index')
        if idx and 6950 <= idx <= 7200:
            tc = obj.get('tool_calls')
            if tc:
                for c in tc:
                    name = c.get('name') or c.get('function', {}).get('name')
                    args = c.get('args') or c.get('function', {}).get('arguments')
                    if name == 'run_command':
                        print(f"[{idx}] run_command: {args.get('CommandLine')}")
                    elif name in ('write_file', 'edit_file'):
                        print(f"[{idx}] {name}: {args.get('Path')}")

