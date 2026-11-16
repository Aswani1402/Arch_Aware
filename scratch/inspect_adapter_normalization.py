import re

with open('backend/app/services/discovery_adapters.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Find classify_adapter_exception
m = re.search(r'def classify_adapter_exception.*?\n\n', text, re.DOTALL)
if m:
    print("=== classify_adapter_exception ===")
    print(m.group(0))

# Find normalization methods
for adp in ['PinterestAdapter', 'InstagramAdapter', 'YouTubeAdapter', 'RedditAdapter']:
    m_cls = re.search(r'class ' + adp + r'\(', text)
    if m_cls:
        start = m_cls.start()
        next_cls = re.search(r'\nclass ', text[start+10:])
        end = start + 10 + next_cls.start() if next_cls else len(text)
        sub = text[start:end]
        
        m_norm = re.search(r'def _normalize.*?\n    def ', sub, re.DOTALL)
        if not m_norm:
            m_norm = re.search(r'def _normalize.*?\n    async def ', sub, re.DOTALL)
        print(f"=== {adp} Normalization ===")
        if m_norm:
            print(m_norm.group(0)[:1500])
        else:
            print("Not found direct _normalize")

