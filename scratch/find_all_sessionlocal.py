import os

app_dir = "backend/app"
direct_calls = []

for root, dirs, files in os.walk(app_dir):
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                for idx, line in enumerate(fp, 1):
                    if "SessionLocal()" in line:
                        direct_calls.append(f"{p}:{idx}: {line.strip()[:80]}")

print("=== SessionLocal() calls in backend/app ===")
for c in direct_calls:
    print(" ", c)

