with open("backend/architect_ai.db", "rb") as f:
    f.seek(65 * 4096)
    page66 = f.read(4096)

# Page header
# Byte 0: page type (0x0d = leaf table b-tree, 0x05 = interior table, etc.)
page_type = page66[0]
first_freeblock = int.from_bytes(page66[1:3], "big")
cell_count = int.from_bytes(page66[3:5], "big")
cell_content_offset = int.from_bytes(page66[5:7], "big")
fragmented_free_bytes = page66[7]

print(f"Page 66 (Offset {65*4096}):")
print(f"  Page type: 0x{page_type:02x} ({'leaf table' if page_type == 0x0d else 'other'})")
print(f"  First freeblock offset: {first_freeblock}")
print(f"  Cell count: {cell_count}")
print(f"  Cell content start offset: {cell_content_offset}")
print(f"  Fragmented free bytes: {fragmented_free_bytes}")

# Read cell pointers
cell_offsets = []
for i in range(cell_count):
    ptr = int.from_bytes(page66[8 + i*2 : 10 + i*2], "big")
    cell_offsets.append(ptr)

print(f"  Active Cell Pointers ({len(cell_offsets)}): {cell_offsets}")

# Check where 270194 is relative to page start (270194 - 65*4096 = 3954)
rel_offset = 270194 - 65 * 4096
print(f"  Relative offset of changed string in Page 66: {rel_offset}")
is_in_active_cell = any(ptr <= rel_offset < (cell_offsets[idx+1] if idx+1 < len(cell_offsets) else 4096) for idx, ptr in enumerate(cell_offsets))
print(f"  Is offset {rel_offset} inside an active cell?: {is_in_active_cell}")
for idx, ptr in enumerate(cell_offsets):
    print(f"    Cell {idx}: starts at relative offset {ptr} (absolute {65*4096 + ptr})")

