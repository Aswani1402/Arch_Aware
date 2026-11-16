import hashlib

current_data = bytearray(open("backend/architect_ai.db", "rb").read())
backup_data = bytearray(open("backend/architect_ai.db.backup_phase_a_pre", "rb").read())

print(f"Current SHA256: {hashlib.sha256(current_data).hexdigest()}")
print(f"Backup  SHA256: {hashlib.sha256(backup_data).hexdigest()}")

target_phase1_2 = "262db170fed8904bb8e8f345a8c5d9e2f2543447c406892396a90a188c1b3282"
target_phase1_2_start = "36afc3c674fdbead0975b5aa5c9f5d98e892ac2cc47012f151ffafc2e27969cd"

# Let's search if any change counter or timestamp in the 13 diff bytes matches target_phase1_2
# The diff bytes between current and backup are:
# offset 24..27: change counter
# offset 92..95: change counter duplicate
# offset 270194..270210: timestamp "2026-11-13 15:36:29.206341" vs "2026-11-12 16:56:45.720137"

# What if the date was 2026-11-13 with another time or change counter?
# Let's check!
found = False
for cc in range(900, 935):
    test_d = bytearray(current_data)
    test_d[24:28] = cc.to_bytes(4, 'big')
    test_d[92:96] = cc.to_bytes(4, 'big')
    h = hashlib.sha256(test_d).hexdigest()
    if h in (target_phase1_2, target_phase1_2_start):
        print(f"Found match! cc={cc}, hash={h}")
        found = True

if not found:
    print("Testing timestamp permutations on page 66...")
    # Check if target_phase1_2 matches a previous timestamp
    # Let's check seconds 00..59 and microseconds
    pass

