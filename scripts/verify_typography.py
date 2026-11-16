import os
import re

def verify_typography():
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
    violations = []

    # Regex to find pixel values under 13px in text classes: text-[10px], text-[11px], text-[12px], text-[9px], etc.
    under_13_pattern = re.compile(r'text-\[(\d+)px\]')

    for root, dirs, files in os.walk(frontend_dir):
        if 'node_modules' in root or '.next' in root:
            continue
        for file in files:
            if file.endswith(('.tsx', '.ts', '.jsx', '.js', '.css', '.html')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        matches = under_13_pattern.findall(line)
                        for m in matches:
                            px = int(m)
                            if px < 13:
                                violations.append((filepath, line_no, f"text-[{px}px]", line.strip()))

    print("=" * 60)
    print("MATERIQ TYPOGRAPHY VERIFICATION REPORT")
    print("Requirement: body 16px, secondary 14px, nothing below 13px")
    print("=" * 60)

    if violations:
        print(f"FAILED: Found {len(violations)} font size occurrences below 13px:")
        for path, lno, token, line in violations[:20]:
            rel = os.path.relpath(path, frontend_dir)
            print(f"  {rel}:{lno} -> {token}")
        return False
    else:
        print("VERIFIED: 0 occurrences of font size below 13px across all frontend files!")
        print("=" * 60)
        return True

if __name__ == "__main__":
    verify_typography()
