import subprocess
import os

env = os.environ.copy()
env["PYTHONPATH"] = f".;backend;{env.get('PYTHONPATH', '')}"
env["TESTING"] = "1"

venv_python = os.path.abspath(r"venv\Scripts\python.exe")
cmd = [venv_python, "-m", "pytest", "backend/app/tests", "--tb=short", "-q"]

print(f"Running pytest using {venv_python}...")
proc = subprocess.run(cmd, env=env, capture_output=True, text=True)

print(f"Exit code: {proc.returncode}")
print("--- STDOUT ---")
print(proc.stdout[-500:] if len(proc.stdout) > 500 else proc.stdout)

if proc.stderr:
    print("--- STDERR ---")
    print(proc.stderr[-500:] if len(proc.stderr) > 500 else proc.stderr)

with open("scratch/pytest_full_output.txt", "w", encoding="utf-8") as f:
    f.write(proc.stdout)
    if proc.stderr:
        f.write("\n\n--- STDERR ---\n")
        f.write(proc.stderr)
print("Saved full output to scratch/pytest_full_output.txt")
