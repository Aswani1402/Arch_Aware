import sqlite3
import re
from pathlib import Path

seed_path = Path("backend/seed_catalogue.sqlite")
conn = sqlite3.connect(f"file:{seed_path.as_posix()}?mode=ro", uri=True)
cur = conn.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
print("Tables in seed:", tables)

# Regex patterns for scanning
re_email = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
re_phone = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
re_indian_mobile = re.compile(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b')
re_whatsapp = re.compile(r'wa\.me|whatsapp', re.IGNORECASE)
re_gstin = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b')
re_api_key = re.compile(r'(?:AIza[0-9A-Za-z-_]{35}|Bearer\s+[A-Za-z0-9-_.]+|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{32,})')
re_password = re.compile(r'(?:password|secret|hash|\$2[aby]\$|argon2)', re.IGNORECASE)

findings = {}

for t in tables:
    cols_info = cur.execute(f'PRAGMA table_info("{t}")').fetchall()
    cols = [c[1] for c in cols_info]
    count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    
    findings[t] = {
        "count": count,
        "cols": cols,
        "scanned_columns": {}
    }
    
    for c in cols:
        col_type = [ci[2] for ci in cols_info if ci[1] == c][0]
        # fetch all non-null values
        values = [r[0] for r in cur.execute(f'SELECT "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL').fetchall()]
        
        email_hits = []
        phone_hits = []
        mobile_hits = []
        whatsapp_hits = []
        gstin_hits = []
        api_hits = []
        pwd_hits = []
        
        for idx, v in enumerate(values):
            s = str(v)
            if re_email.search(s):
                email_hits.append(idx)
            if re_indian_mobile.search(s):
                mobile_hits.append(idx)
            elif re_phone.search(s):
                phone_hits.append(idx)
            if re_whatsapp.search(s):
                whatsapp_hits.append(idx)
            if re_gstin.search(s):
                gstin_hits.append(idx)
            if re_api_key.search(s):
                api_hits.append(idx)
            if re_password.search(s):
                pwd_hits.append(idx)
        
        findings[t]["scanned_columns"][c] = {
            "type": col_type,
            "non_null_count": len(values),
            "email_hits": len(email_hits),
            "mobile_hits": len(mobile_hits),
            "phone_hits": len(phone_hits),
            "whatsapp_hits": len(whatsapp_hits),
            "gstin_hits": len(gstin_hits),
            "api_hits": len(api_hits),
            "pwd_hits": len(pwd_hits),
        }

conn.close()

print("\n=== SUMMARY OF SENSITIVE PATTERN MATCHES IN SEED ===")
for t, d in findings.items():
    print(f"\n--- TABLE: {t} (Rows: {d['count']}) ---")
    for c, sc in d["scanned_columns"].items():
        hits = [f"{k}={v}" for k, v in sc.items() if k.endswith("_hits") and v > 0]
        if hits:
            print(f"  Column '{c}' ({sc['type']}): {', '.join(hits)}")
        else:
            # print column with 0 hits
            pass

