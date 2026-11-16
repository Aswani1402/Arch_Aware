import glob
import re

count = 0
for f in glob.glob('frontend/**/*.tsx', recursive=True):
    content = open(f, encoding='utf-8').read()
    def replacer(match):
        tag = match.group(0)
        if 'referrerPolicy' in tag:
            return tag
        return tag.replace('<img', '<img referrerPolicy="no-referrer"', 1)
    
    new_content = re.sub(r'<img\s+[^>]*>', replacer, content)
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as out:
            out.write(new_content)
        count += 1
        print(f"Updated {f}")

print(f"Total files updated: {count}")
