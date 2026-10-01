#!/usr/bin/env python3
"""
st21-annotate.py — annotated AArch64 listing helper for the stock ST21NFC
vendor HAL blob (nfc_nci.st21nfc.st.so), used by the Phase 4b static audit.

Why this exists: the blob is stripped except for its exported symbols, so
range-based "functions" must be derived from branch targets. This helper folds
adrp+add pairs back into .rodata string references, names local call targets
(``<sym>[:delta]``), and resolves whole call graphs so the audit can be
reproduced without re-deriving it by hand.

The raw ``*.asm`` corpus is an unannotated ``llvm-objdump -d`` dump; this tool is
the interpretive layer over it. ``index`` turns a dump into an addr->callee table,
``calls`` joins that table with the exported-symbol/PLT names, which is what turns
"BL #0xe5d28" into "hal_conf_values_int32_load -> hal_config.ccfg_int32_load".

Usage:
  st21-annotate.py <blob.so> dump  <addr-or-name> [--max N]   # annotated listing
  st21-annotate.py <blob.so> xref  <regex>                   # funcs using a string
  st21-annotate.py <blob.so> calls <addr-or-name> --asm <dump>
  st21-annotate.py <blob.so> index --asm <dump>              # addr -> callee addr
"""
import re
import subprocess
import sys

BL_RE = re.compile(r"^\s*([0-9a-f]+):\s+bl\s+#?0x([0-9a-f]+)")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


def load(blob):
    syms = []
    for line in sh(f"nm -D --defined-only '{blob}'").splitlines():
        m = re.match(r"^([0-9a-f]{16}) (\S) (.*)$", line)
        if m:
            syms.append({"addr": int(m.group(1), 16), "type": m.group(2), "name": m.group(3)})
    syms.sort(key=lambda x: x["addr"])

    # .rodata string table: llvm-readelf prints section-relative *hex* offsets in
    # brackets (no 0x prefix), so absolute vaddrs need the section address added.
    out = sh(f"llvm-readelf -S '{blob}'")
    base = int(re.search(r"\.rodata\s+\w+\s+([0-9a-f]+)", out).group(1), 16)
    strings = {}
    for line in sh(f"llvm-readelf --string-dump .rodata '{blob}'").splitlines():
        m = re.match(r"^\s*\[\s*([0-9a-f]+)\]\s+(.*)$", line)
        if m:
            strings[base + int(m.group(1), 16)] = m.group(2)

    ins = []
    for line in sh(f"llvm-objdump -d --no-show-raw-insn '{blob}'").splitlines():
        m = re.match(r"^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$", line)
        if m:
            addr, op, rest = int(m.group(1), 16), m.group(2), m.group(3)
            ins.append({"addr": addr, "op": op, "rest": rest.split("//")[0].strip()})
    return syms, strings, ins


def bl_index(path):
    """Index BL targets from a raw `llvm-objdump -d` listing (addr -> callee addr).

    `annotate()` only labels a branch when its target is exactly an exported
    symbol start; every internal call becomes `<prev exported symbol>:+delta`,
    which loses the callee. Pairing the two gives candidate -> callee edges.
    """
    idx = {}
    with open(path, errors="replace") as fh:
        for line in fh:
            m = BL_RE.match(line)
            if m:
                idx[int(m.group(1), 16)] = int(m.group(2), 16)
    return idx


def plt_stubs(blob):
    """Map .plt stub addresses to the imported symbol they dispatch to.

    llvm-objdump labels only the ``<.plt>`` section header, never individual stubs,
    so calls into libc/C++ show up as bare ``bl #0x25440`` addresses. Pair the
    ``.rela.plt`` symbol order with the AArch64 stub layout (header stub 0x20 bytes,
    then 16 bytes per entry) to name them; every unresolved stub in a firmware
    loader would otherwise masquerade as an anonymous local helper.
    """
    base = None
    for line in sh(f"llvm-objdump -h --section=.plt '{blob}'").splitlines():
        # "15 .plt 000008c0 00000000000253f0 TEXT" -> fields are size THEN vma.
        m = re.match(r"^\s*\d+\s+\.plt\s+([0-9a-f]+)\s+([0-9a-f]+)", line)
        if m:
            base = int(m.group(2), 16)
    if base is None:
        return {}
    names, cur = [], None
    for line in sh(f"llvm-readelf --relocs '{blob}'").splitlines():
        if "'.rela.plt'" in line:
            cur = ".rela.plt"
            continue
        if not cur:
            continue
        m = re.match(r"^\s*[0-9a-f]+\s+[0-9a-f]+\s+R_AARCH64_JUMP_SLOT\s+([0-9a-f]+)\s+(\S+)", line)
        if m:
            names.append(m.group(2).split("@")[0])
        elif line.strip() and not line.startswith(" "):
            break
    stubs = {}
    for i, n in enumerate(names):
        stubs[base + 0x20 + 16 * i] = n
    return stubs


def annotate(ins, syms, strings):
    """Fold adrp+add pairs into string refs and name local branch targets."""
    def fn(addr):
        cur = None
        for s in syms:
            if s["addr"] <= addr:
                cur = s
            else:
                break
        return cur
    # Boundaries use exported symbol starts only: the blob is stripped beyond them,
    # so a "function" here really means "region up to the next exported symbol".
    starts = {s["addr"] for s in syms}
    out = []
    for i, e in enumerate(ins):
        note = ""
        if e["op"] == "adrp":
            g = re.match(r"^(x\d+), (0x[0-9a-f]+)$", e["rest"])
            if g:
                page = int(g.group(2), 16)
                for j in range(i + 1, min(i + 8, len(ins))):
                    if ins[j]["op"] == "adrp":
                        break
                    h = re.match(r"^(x\d+), (x\d+), #0x([0-9a-f]+)$", ins[j]["rest"])
                    if h and h.group(2) == g.group(1):
                        v = page + int(h.group(3), 16)
                        if v in strings:
                            note = '   ; "' + strings[v].replace("\n", "\\n")[:90] + '"'
                        break
        if not note:
            m = re.match(r"^0x([0-9a-f]+)", e["rest"])
            if m and e["op"] in ("bl", "b"):
                t = int(m.group(1), 16)
                f = fn(t)
                if f and f["addr"] == t:
                    note = f"   ; -> {f['name']}"
                elif f:
                    note = f"   ; -> {f['name']}+0x{t - f['addr']:x}"
        out.append({**e, "fn": fn(e["addr"]), "note": note})
    return out, starts


def resolve(ann, syms, key):
    if re.fullmatch(r"0x[0-9a-f]+", key):
        t = int(key, 16)
        for e in ann:
            if e["addr"] == t:
                return e["fn"]
        sys.exit(f"no instruction at {key}")
    for e in ann:
        if e["fn"] and e["fn"]["name"] == key:
            return e["fn"]
    sys.exit(f"no function named {key}")


def main():
    blob, mode, key = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None
    flag = lambda name: sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None
    syms, strings, ins = load(blob)
    ann, starts = annotate(ins, syms, strings)

    if mode == "index":
        asm = flag("--asm") or sys.exit("index mode needs --asm <raw disassembly>")
        for addr, tgt in sorted(bl_index(asm).items()):
            print(f"0x{addr:x} 0x{tgt:x}")
        return

    if key is None:
        sys.exit(f"{mode} mode needs <addr-or-name>")

    if mode == "xref":
        # `key` here is a regex over the annotation, not a symbol name.
        pat = re.compile(key, re.I)
        for e in ann:
            if pat.search(e["note"]):
                fn_ = e["fn"]
                print(f"{'~' if fn_ and fn_['addr'] != e['addr'] else ' '}{fn_['name'] if fn_ else '?'} "
                      f"@0x{e['addr']:x} {e['note']}")
        return

    f = resolve(ann, syms, key)
    lo = f["addr"]
    hi = min((s for s in sorted(starts) if s > lo), default=lo + 4 * 4000)

    if mode == "calls":
        # Interpretive layer: one row per call site, callee resolved to a symbol
        # name (PLT stub or previous-exported-symbol + delta) plus the string the
        # call site is primed with. Derived mechanically from the ELF.
        asm = flag("--asm") or sys.exit("calls mode needs --asm <raw disassembly>")
        idx, stubs = bl_index(asm), plt_stubs(blob)
        rows = 0
        for e in ann:
            if not (lo <= e["addr"] < hi) or e["op"] != "bl":
                continue
            tgt = idx.get(e["addr"])
            if tgt is None:
                continue
            callee = stubs.get(tgt)
            if callee is None:
                g = resolve(ann, syms, hex(tgt)) if any(x["addr"] == tgt for x in ann) else None
                callee = (g["name"] if g and g["addr"] == tgt
                         else f"{g['name']}+0x{tgt - g['addr']:x}" if g else "?")
            print(f"0x{e['addr']:x} -> 0x{tgt:x} {callee}{'  ' + e['note'].strip() if e['note'] else ''}")
            rows += 1
        print(f"# {rows} call sites in {f['name']} [0x{lo:x},0x{hi:x})")
        return

    print(f"===== {f['name']} @0x{lo:x} (range to 0x{hi:x}) =====")
    lim = int(flag("--max") or 4000)
    n = 0
    for e in ann:
        if not (lo <= e["addr"] < hi):
            continue
        print(f"  {e['addr']:6x}: {e['op']:<8} {e['rest']}{e['note']}")
        n += 1
        if n >= lim:
            print("  ... (truncated)")
            break


if __name__ == "__main__":
    main()
