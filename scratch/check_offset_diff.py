with open("backend/architect_ai.db", "rb") as f1, open("backend/architect_ai.db.backup_phase_a_pre", "rb") as f2:
    f1.seek(270100)
    data1 = f1.read(200)
    f2.seek(270100)
    data2 = f2.read(200)

print("Data 1 (Current):", data1)
print("\nData 2 (Backup):", data2)

