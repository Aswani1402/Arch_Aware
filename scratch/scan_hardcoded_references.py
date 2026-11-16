import glob
import os
import re

patterns = {
    "localhost": re.compile(r'localhost:\d+', re.I),
    "127.0.0.1": re.compile(r'127\.0\.0\.1(:\d+)?'),
    "windows_path": re.compile(r'[a-zA-Z]:[\\/](?:Users|Program|Windows|temp)', re.I),
    "http_url": re.compile(r'http://(?:localhost|127\.0\.0\.1)'),
}

exclude_dirs = {".git", "node_modules", ".next", "venv", "__pycache__", ".pytest_cache", "brain", "scratch"}

def should_scan(path):
    parts = Path(path).parts
    return not any(ex in parts for ex in exclude_dirs)

findings = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith((".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".yaml", ".yml", ".env", ".example")):
            filepath = os.path.join(root, file)
            try:
                content = open(filepath, "r", encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for name, pat in patterns.items():
                for match in pat.finditer(content):
                    line_no = content[:match.start()].count("\n") + 1
                    line = content.splitlines()[line_no - 1].strip()
                    findings.append((filepath, line_no, name, match.group(0), line))

print(f"Total findings: {len(findings)}")
for fp, lno, name, match, line in findings:
    # Filter out test fixtures and expected local config
    print(f"{fp}:{lno} [{name}] '{match}' -> {line[:100]}")

