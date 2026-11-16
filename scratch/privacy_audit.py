import sqlite3

conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()

tables = [
    r[0]
    for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
]

findings = {}
for t in tables:
    cols = [c[1].lower() for c in cur.execute(f"PRAGMA table_info({t});").fetchall()]
    count = cur.execute(f"SELECT count(*) FROM {t};").fetchone()[0]
    has_user_auth = any(
        k in cols for k in ["password", "hashed_password", "token", "secret"]
    )
    has_email = any("email" in k for k in cols)
    has_phone = any(k in cols for k in ["phone", "whatsapp", "mobile"])
    has_user_rel = "user_id" in cols
    findings[t] = {
        "count": count,
        "has_user_auth": has_user_auth,
        "has_email": has_email,
        "has_phone": has_phone,
        "has_user_rel": has_user_rel,
        "cols": cols,
    }
conn.close()

print("=== PRIVACY CATEGORY ANALYSIS (READ-ONLY, ZERO VALUES PRINTED) ===")
for t, info in sorted(findings.items()):
    flags = []
    if info["has_user_auth"]:
        flags.append("USER_AUTH_DATA")
    if info["has_email"]:
        flags.append("EMAIL_ADDRESSES")
    if info["has_phone"]:
        flags.append("PHONE_CONTACTS")
    if info["has_user_rel"]:
        flags.append("USER_ASSOCIATED_RECORDS")
    if flags:
        print(f"Table: {t:28s} (rows={info['count']:4d}) -> {', '.join(flags)}")

conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()
cols = [c[1] for c in cur.execute("PRAGMA table_info(source_connectors);").fetchall()]
has_keys = cur.execute(
    "SELECT COUNT(*) FROM source_connectors WHERE api_key IS NOT NULL AND api_key != ''"
).fetchone()[0]
print(f"source_connectors cols: {cols}")
print(f"source_connectors records with non-empty api_key: {has_keys}")
conn.close()
