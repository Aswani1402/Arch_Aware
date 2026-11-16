import os
import subprocess
import sys

# Test running test_master_prompt_features.py with isolated DATABASE_URL
env = os.environ.copy()
env["PYTHONPATH"] = "backend;."
env["DATABASE_URL"] = "sqlite:///:memory:"

mtime_before = os.path.getmtime("backend/architect_ai.db")

print("Running test_master_prompt_features.py with DATABASE_URL=sqlite:///:memory: ...")
res = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/app/tests/test_master_prompt_features.py", "-q"],
    capture_output=True,
    text=True,
    env=env,
)

mtime_after = os.path.getmtime("backend/architect_ai.db")
print("Pytest stdout:", res.stdout.strip())
print("Pytest stderr:", res.stderr.strip()[:200])
print("Return code:", res.returncode)
print(f"DB mtime before: {mtime_before}")
print(f"DB mtime after:  {mtime_after}")
print(f"DB touched? {mtime_before != mtime_after}")

