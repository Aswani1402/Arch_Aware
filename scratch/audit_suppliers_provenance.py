import sqlite3

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cur = conn.cursor()

print("=== 1. SUPPLIER COUNTS ===")
cur.execute("SELECT COUNT(*) FROM suppliers;")
total_suppliers = cur.fetchone()[0]
print(f"Total suppliers: {total_suppliers}")

print("\n=== 2. COUNTS BY VERIFICATION STATUS ===")
cur.execute("SELECT verification_status, COUNT(*) FROM suppliers GROUP BY verification_status;")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n=== 3. COUNTS BY IS_POTENTIAL (SOURCE) ===")
cur.execute("SELECT is_potential, COUNT(*) FROM suppliers GROUP BY is_potential;")
for r in cur.fetchall():
    print(f"  is_potential={r[0]}: {r[1]}")

print("\n=== 4. COUNTS WITH COORDINATES ===")
cur.execute("SELECT COUNT(*) FROM suppliers WHERE latitude IS NOT NULL AND longitude IS NOT NULL;")
with_coords = cur.fetchone()[0]
print(f"  With lat/lon: {with_coords}")
print(f"  Without lat/lon: {total_suppliers - with_coords}")

print("\n=== 5. COUNTS WITH PHONE & WHATSAPP ===")
cur.execute("SELECT COUNT(*) FROM suppliers WHERE phone IS NOT NULL AND trim(phone) != '';")
with_phone = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM suppliers WHERE whatsapp IS NOT NULL AND trim(whatsapp) != '';")
with_wa = cur.fetchone()[0]
print(f"  With phone: {with_phone}")
print(f"  With whatsapp explicitly supplied: {with_wa}")

print("\n=== 6. COUNTS WITH MATERIAL-SPECIFIC PRODUCT EVIDENCE (supplier_products) ===")
cur.execute('''
    SELECT COUNT(DISTINCT s.id)
    FROM suppliers s
    JOIN supplier_products sp ON sp.supplier_id = s.id;
''')
with_products = cur.fetchone()[0]
print(f"  Suppliers with linked products in supplier_products: {with_products}")
cur.execute("SELECT COUNT(*) FROM supplier_products;")
total_links = cur.fetchone()[0]
print(f"  Total supplier_product links: {total_links}")

print("\n=== 7. GEOGRAPHIC DISTRIBUTION (STATE & CITY) ===")
cur.execute("SELECT state, COUNT(*) FROM suppliers GROUP BY state ORDER BY COUNT(*) DESC;")
print("States:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

cur.execute("SELECT city, COUNT(*) FROM suppliers GROUP BY city ORDER BY COUNT(*) DESC LIMIT 15;")
print("Cities (Top 15):")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n=== 8. SUSPICIOUS / DEMO / SEED / TEST SUPPLIERS ===")
cur.execute('''
    SELECT id, name, city, state, verification_status, phone, website
    FROM suppliers
    WHERE name LIKE '%Test%' OR name LIKE '%Demo%' OR city NOT IN ('Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Thrissur', 'Kollam', 'Alappuzha', 'Kottayam', 'Palakkad', 'Kannur')
    LIMIT 25;
''')
suspicious = cur.fetchall()
print(f"Non-Kerala / Test suppliers count: {len(suspicious)}")
for s in suspicious:
    print(" ", s)

conn.close()

