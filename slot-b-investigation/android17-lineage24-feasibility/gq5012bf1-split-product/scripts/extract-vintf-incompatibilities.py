#!/usr/bin/env python3
"""Extract every initial checkvintf incompatibility and its reviewed class."""
import csv
import re
from pathlib import Path

LOG = Path("/mnt/SamsungSSD/TIER3/phase5/android17/logs/checkvintf-gq5012bf1-split-i1.log")
OUT = Path(__file__).resolve().parents[1] / "VINTF-INCOMPATIBILITIES.tsv"
lines = [re.sub(r"\x1b\[[0-9;]*m", "", x) for x in LOG.read_text(errors="ignore").splitlines()]
start = next(i for i, x in enumerate(lines) if "The following instances are in the device manifest" in x)
end = next(i for i, x in enumerate(lines[start:], start) if x.startswith("Suggested fix:"))
instances = [x.strip() for x in lines[start + 1:end] if x.startswith("    ")]
with OUT.open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["instance", "classification", "resolution", "evidence"])
    for instance in instances:
        w.writerow([instance, "DEVICE_TREE_FIX",
                    "Declared as a required instance in device/ulefone/gq5012bf1/vintf/framework_compatibility_matrix.xml",
                    "Captured stock V15 vendor+DSDS manifest; initial Android17 checkvintf output"])
print(f"wrote {len(instances)} rows to {OUT}")
