import os

tests_dir = "backend/app/tests"
files = [f for f in os.listdir(tests_dir) if f.endswith(".py")]

direct_sessionlocal = []
direct_db_path = []
for f in files:
    p = os.path.join(tests_dir, f)
    with open(p, "r", encoding="utf-8", errors="ignore") as fp:
        lines = fp.readlines()
        for idx, line in enumerate(lines, 1):
            if "SessionLocal()" in line and "TestingSessionLocal" not in line:
                direct_sessionlocal.append(f"{f}:{idx}: {line.strip()[:80]}")
            if "architect_ai.db" in line and not line.strip().startswith("#"):
                direct_db_path.append(f"{f}:{idx}: {line.strip()[:80]}")

print("=== Direct SessionLocal() in tests ===")
for m in direct_sessionlocal:
    print(" ", m)

print("\n=== Direct architect_ai.db in tests ===")
for m in direct_db_path:
    print(" ", m)

