import json

with open(r'C:\Users\Aswini_Ayappan\.gemini\antigravity\brain\45f9c0e2-f31d-4a6d-895b-d7a5259ba7f9\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'backup_pre_phase1_20261115_160539' in line:
            obj = json.loads(line)
            if obj.get('tool_calls'):
                for tc in obj['tool_calls']:
                    print(f'Line {idx}: {tc.get("name")}')
                    args = tc.get('args', {})
                    if 'CommandLine' in args:
                        print('  CommandLine:', args['CommandLine'][:140])
                    if 'BypassSandbox' in args:
                        print('  BypassSandbox:', args['BypassSandbox'])

