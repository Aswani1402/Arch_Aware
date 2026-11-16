import hashlib

target_sha = "262db170fed8904bb8e8f345a8c5d9e2f2543447c406892396a90a188c1b3282"

with open("backend/architect_ai.db", "rb") as f:
    data = bytearray(f.read())

found = False
# Try different change counter values (bytes 24-27 and bytes 92-95)
for c in range(800, 1000):
    b = c.to_bytes(4, "big")
    data[24:28] = b
    data[92:96] = b
    h = hashlib.sha256(data).hexdigest()
    if h == target_sha:
        print(f"FOUND MATCH! Change counter = {c} produces {target_sha}")
        found = True
        break

if not found:
    print("No direct change counter match found with current body. Checking other offsets...")

