#!/usr/bin/env python3
"""
st21-fw-path-literals.py — dump the firmware-loader-relevant literals and symbol
evidence from the *committed* runtime blobs, so the Phase 4b loader findings are
re-derivable without any transient extraction directory.

For each blob it reports, per pattern:
  * string literals found by scanning the whole file for NUL-separated runs
    (with their file offsets, so a reviewer can re-check with `dd`), and
  * which of those patterns also appear as dynamic symbols (defined / undefined),
    which is what distinguishes "this blob contains the loader" from "this blob
    merely links against it".

Usage: st21-fw-path-literals.py [blob ...] > fw-path-literals.txt
"""
import re
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLOBDIR = os.path.normpath(os.path.join(HERE, "..", "analysis", "st21-gemini-audit", "runtime-blobs"))

DEFAULT_BLOBS = [
    "nfc_nci.st21nfc.st.so",
    "libstnfc-nci.so",
    "android.hardware.nfc-service-st",
    "libstnfc_nci_jni.so",
]

# Loader-relevant literal families: firmware images, config dirs, the GPO/OTP
# scratch areas, patch/factory-loader vocabulary, and the trace tag the ST
# firmware-download code prints under.
PATTERNS = [
    ("firmware-dir", re.compile(r"^(?:/[\w.\-]+)+/?$")),
    ("fw-image-name", re.compile(r"\.(?:bin|elf|cfg|s19|hex)$")),
    ("loader-symbol", re.compile(r"^(?:ft_|hal_fd_|HAL_|ST21B_|NXP_)|FwDownload|fw_update|FwUpdate|unlzba|FactoryLoader|configuration_id|core_cfg|GPO|Gpo|gpo", re.I)),
    ("trace-tag", re.compile(r"[A-Z]{2,}[-_][A-Z]{2,}.*(?:TIME|LOADER|PATCH|UPDATE|BOOT)", re.I)),
]


def literals(blob):
    data = open(blob, "rb").read()
    out, start = [], -1
    for i, ch in enumerate(data):
        if ch == 0:
            if start >= 0 and i - start > 2:
                try:
                    out.append((start, data[start:i].decode("ascii")))
                except UnicodeDecodeError:
                    pass
            start = -1
        elif start < 0:
            start = i
    return out


def dynsyms(blob):
    p = subprocess.run(["readelf", "--dyn-syms", "--wide", blob], capture_output=True, text=True)
    return re.findall(r"\s(\S+)$", p.stdout, re.M)


def main(argv):
    blobs = argv[1:] or [os.path.join(BLOBDIR, n) for n in DEFAULT_BLOBS]
    for blob in blobs:
        print("=" * 74)
        print("### " + os.path.relpath(blob, os.path.join(HERE, "..")) + "  (" + str(os.path.getsize(blob)) + " bytes)")
        lits = literals(blob)
        dsyms = dynsyms(blob)
        for label, pat in PATTERNS:
            hits = [(o, s) for o, s in lits if pat.search(s)]
            if label == "firmware-dir":
                hits = [(o, s) for o, s in hits if len(s.split("/")) > 2 and len(s) <= 56]
                hits.sort(key=lambda kv: kv[0])
            print(f"  -- {label} ({len(hits)})")
            for o, s in hits[:40]:
                print(f"       0x{o:05x}  {s}")
        loader = sorted({s for s in dsyms if PATTERNS[2][1].search(s)})
        print(f"  -- dynamic symbols matching loader-symbol ({len(loader)}, sorted unique)")
        for s in loader[:80]:
            print("       " + s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
