#!/usr/bin/env python3
"""
st21-fw-loader-recovery.py — reconstruct the ST21NFC firmware-loader / patch
path from the *persistent* HAL driver blob and emit it as a reviewable trace.

Why: the original Phase 4b recovery (``firmware-loader.md``) was written against
vendor blobs that existed only in an ephemeral ``/tmp`` extraction, so none of it
could be re-verified. This script rebuilds the same conclusion from blobs that
are committed in ``runtime-blobs/`` (``nfc_nci.st21nfc.st.so`` is byte-identical
to the shipped stock vendor copy), which is why it exists.

Each row is one call site inside the firmware-download region, with the callee
resolved through ``.rela.plt`` and the string literal the call site is primed
with — i.e. the control flow *and* the file names / config keys it consumes.

Usage:
  st21-fw-loader-recovery.py [blob] [--lo ADDR] [--hi ADDR] > fw-loader-recovery.tsv
"""
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.normpath(os.path.join(HERE, "..", "analysis", "st21-gemini-audit"))
DEFAULT_BLOB = os.path.join(AUDIT, "runtime-blobs", "nfc_nci.st21nfc.st.so")

# The firmware-download region is bounded by the two exported symbols that bracket
# the (inlined) ST HAL_FwDownload implementation: ft_cmd_HwReset .. the start of
# BackToFactoryLoaderIfPossible. Override with --lo/--hi for another build.
DEFAULT_LO = 0x218A8
DEFAULT_HI = 0x237F0


def load_helper():
    spec = importlib.util.spec_from_file_location("st21ann", os.path.join(HERE, "st21-annotate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    argv = sys.argv[1:]
    blob = argv[0] if argv and not argv[0].startswith("--") else DEFAULT_BLOB

    def flag(name, default):
        return int(argv[argv.index(name) + 1], 16) if name in argv else default

    lo, hi = flag("--lo", DEFAULT_LO), flag("--hi", DEFAULT_HI)
    h = load_helper()
    syms, strings, ins = h.load(blob)
    ins, _starts = h.annotate(ins, syms, strings)
    stubs = h.plt_stubs(blob)
    dem = lambda n: (subprocess.run(["c++filt", n], capture_output=True, text=True).stdout.strip()
                    if n.startswith("_Z") else n)
    named = {s["addr"]: s["name"] for s in syms}

    def region():
        """One pass over the annotated listing: (addr, callee, literals since it).

        `annotate()` puts the folded adrp+add literal on the *address-forming*
        instruction, which precedes the call by a few slots, so literals are
        carried forward to the next ``bl`` rather than looked up on its own row.
        """
        pending = []
        for e in ins:
            if not (lo <= e["addr"] < hi):
                continue
            if '"' in e["note"]:
                pending.append(e["note"].split('"')[1])
                continue
            if e["op"] != "bl":
                continue
            m = re.match(r"^0x([0-9a-f]+)", e["rest"])
            if not m:
                continue
            t = int(m.group(1), 16)
            callee = stubs.get(t) or dem(named.get(t, f"local:0x{t:x}"))
            yield e["addr"], callee, " | ".join(pending)
            pending = []

    print("# addr\tcallee\tstring-literal-primed-at-call-site")
    n = 0
    for addr, callee, lit in region():
        print(f"0x{addr:x}\t{callee}\t{lit}")
        n += 1
    print(f"# {n} call sites in [0x{lo:x},0x{hi:x}) of {os.path.basename(blob)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
