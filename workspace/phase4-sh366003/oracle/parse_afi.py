#!/usr/bin/env python3
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[3]
blob_path = Path(__file__).with_name("sinofs_afi_data.stock.bin")
blob = blob_path.read_bytes()
assert len(blob) == 2142
assert hashlib.sha256(blob).hexdigest() == "4888c5bc4b847ec6c118cd7bd334cbcffbf52c5fa2bf8f8660c3ac65e03359e1"
rows = []
i = 0
seq = 0
while i < len(blob):
    op = blob[i]
    if op in (1, 4):
        size = 4
    elif op in (2, 3):
        size = 4 + blob[i + 3]
    else:
        raise ValueError(f"bad op {op} at 0x{i:x}")
    rec = blob[i:i + size]
    if len(rec) != size:
        raise ValueError(f"truncated record at 0x{i:x}")
    if op == 1:
        detail = f"READ addr=0x{rec[1] >> 1:02x} reg=0x{rec[2]:02x} len={rec[3]}"
    elif op == 2:
        detail = (f"WRITE addr=0x{rec[1] >> 1:02x} reg=0x{rec[2]:02x} "
                  f"len={rec[3]} data={rec[4:].hex()}")
    elif op == 3:
        detail = (f"COMPARE addr=0x{rec[1] >> 1:02x} reg=0x{rec[2]:02x} "
                  f"len={rec[3]} expected={rec[4:].hex()}")
    else:
        detail = f"WAIT ms={int.from_bytes(rec[2:4], 'big')} selector={rec[1]}"
    rows.append((seq, i, op, size, rec.hex(), detail))
    i += size
    seq += 1
assert i == len(blob)
out = ROOT / "kernel/phase4-sh366003-afi-records.tsv"
out.write_text("seq\toffset\top\tsize\traw_hex\tdetail\n" + "".join(
    f"{n}\t0x{off:04x}\t{op}\t{size}\t{raw}\t{detail}\n"
    for n, off, op, size, raw, detail in rows
))
from collections import Counter
counts = Counter(r[2] for r in rows)
print(f"size={len(blob)} sha256={hashlib.sha256(blob).hexdigest()}")
print(f"records={len(rows)} type_counts={dict(sorted(counts.items()))}")
print(f"wait_total_ms={sum(int.from_bytes(bytes.fromhex(r[4])[2:4], 'big') for r in rows if r[2] == 4)}")
print(f"write_bytes={sum(bytes.fromhex(r[4])[3] for r in rows if r[2] == 2)}")
print(f"compare_bytes={sum(bytes.fromhex(r[4])[3] for r in rows if r[2] == 3)}")
print(f"output={out}")
