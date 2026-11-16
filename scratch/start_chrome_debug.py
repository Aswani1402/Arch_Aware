import subprocess
import time
import os
import urllib.request
import json

profile_dir = r"C:\Users\Aswini_Ayappan\.chrome-dev-profile"
os.makedirs(profile_dir, exist_ok=True)

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome_exe,
    "--remote-debugging-port=9222",
    f"--user-data-dir={profile_dir}",
    "--no-first-run",
    "--no-default-browser-check",
    "http://localhost:3000"
]

proc = subprocess.Popen(cmd)
print("Started Chrome with PID:", proc.pid)
time.sleep(3)

try:
    with urllib.request.urlopen("http://localhost:9222/json/version", timeout=5) as resp:
        data = json.loads(resp.read().decode())
        print("Chrome Version Data:", data)
        ws_url = data.get("webSocketDebuggerUrl", "")
        # ws://localhost:9222/devtools/browser/d9b4b...
        path = ws_url.replace("ws://localhost:9222", "").replace("ws://127.0.0.1:9222", "")
        print("DevTools Browser Path:", path)
        
        target_dir = r"C:\Users\Aswini_Ayappan\AppData\Local\Google\Chrome\User Data"
        os.makedirs(target_dir, exist_ok=True)
        active_port_file = os.path.join(target_dir, "DevToolsActivePort")
        with open(active_port_file, "w", encoding="utf-8") as f:
            f.write(f"9222\n{path.lstrip('/')}\n")
        print("DevToolsActivePort written successfully to:", active_port_file)
except Exception as e:
    print("Error querying 9222:", e)

