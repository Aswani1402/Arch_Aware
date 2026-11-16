import glob
import re

test_files = sorted(glob.glob("backend/app/tests/**/*.py", recursive=True))

findings = []
for tf in test_files:
    if tf.endswith("conftest.py"):
        continue
    content = open(tf, encoding="utf-8").read()
    
    # Check for client fixture or TestClient
    has_testclient = "TestClient(" in content
    has_client_fixture = re.search(r"@pytest\.fixture\s+def client\b", content)
    has_sessionlocal = "SessionLocal" in content
    
    overrides_get_db = "dependency_overrides[get_db]" in content
    uses_conftest_client = "def test_" in content and "client" in content and not has_client_fixture and not has_testclient
    
    issues = []
    if has_client_fixture and not overrides_get_db:
        issues.append("Custom client fixture without dependency_overrides[get_db]")
    if has_testclient and not overrides_get_db and not "client" in tf: # Direct TestClient instantiation
        # Check if it makes API calls
        issues.append("Direct TestClient(app) instantiation")
    if has_sessionlocal:
        issues.append("Direct SessionLocal usage")
        
    if issues:
        findings.append((tf, issues))

print("=== TEST ISOLATION LEAK AUDIT ===")
for tf, issues in findings:
    print(f"\nFile: {tf}")
    for iss in issues:
        print(f"  - {iss}")

