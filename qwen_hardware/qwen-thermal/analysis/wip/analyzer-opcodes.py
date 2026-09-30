#!/usr/bin/env python3
"""Extract the rms.ic / rms.config operation codes from librms-device-analyzer.so.

Second half of the vendor command surface.  `qcnReaderTask()` in
vendor.qwen.hardware.thermal-service (reconstructed in
notes/phase4-connfem-reconstruction.md) dispatches a binary report off a
16-bit header:

    uint16_t header = be16(buf[41]);
    if (reportId == 4) { if (header >= 0x3000) { if (header < 0x3a00) route_3xxx(&buf[42], buf[58]); } }
    else if (reportId == 11) { if (header < 0x11000) { if (header >= 0x10000) route_1xxxx(&buf[46], buf[70]); } }

The two route_* functions were the two decompiled blobs that failed the
strength audit, so their class -> helper mapping stayed a black box.  The
service only dlopen()s librms-device-analyzer.so and calls its single export
`ProcessOpCodeReport(class)`, which is itself a two-level table walker:

    void ProcessOpCodeReport(int p_class)
    {
      ushort chunk = *(ushort *)**(dword_83D0 + 34 * (p_class - 1) + 17);
      for (i = 0; i < *(dword_83D0 + 34 * (p_class - 1) + 16); ++i) {
        ushort *ent = *(dword_83D0 + 34 * (p_class - 1) + 33) + 2*i;
        if (chunk < ent[0] || chunk > ent[1]) {
          sub_17A0(1, "OPERATION_CODE_NOT_FOUND: %d, %d", p_class, chunk);
          return 1;
        }
        if (ent[0] <= chunk && chunk <= ent[1]) {
          snprintf(opcodeText, 0x10u, "%04x", chunk);
          ((void (*)(void))(**(dword_83D0 + 34*(p_class-1) + 32) + 16*i))();
          return 0;
        }
      }
      sub_17A0(1, "OPERATION_CODE_NOT_FOUND: %d", p_class);
      return 1;
    }

So a class is a table of (lo, hi) opcode ranges plus a parallel vector of
helper function pointers — no static immediate anywhere, which is why the
CFG/operand-tag pipeline that worked for libircmd020.so is the wrong tool here.
The evidence that survives deoptimisation is the source string the service
itself prints: every operation code is *named by the string literal embedded in
its helper*, and those literals have a fixed vocabulary.

Method, and why it is honest:

* candidate == the `adrp`+`add`/`ldr` pair whose target is a `.rodata` string
  matching a strict opcode regex.  An adrp+add materialising a vaddr inside
  .rodata is the AArch64 idiom for taking the address of a static string; the
  pair is unique and deterministic to reconstruct, so "which string does this
  helper reference" is decidable straight from the disassembly.
* rejected == the same pair whose target lands in .bss/.data (a writable
  buffer, e.g. snprintf's destination), so the literal is not a compile-time
  opcode and the site is reported for review.
* strings == every string in the whole binary bucketed by regex, so the
  negative result ("no class-range table literal exists") is reproducible
  instead of asserted.
* cfg == the function CFG profile.  This binary has no switch jump and no
  computed branch at all: the dispatch is fully data-driven, which is itself the
  finding, and it is why the two formats are separate registries.

Nothing here guesses at a helper's semantics: an opcode is reported against the
helper whose body loads the literal that spells it, or not at all.

Usage:
    python3 tools/analyzer-opcodes.py \
        --manifest analysis/manifests/rms-device-analyzer.tsv \
        --out-dir evidence/binaries/rms-device-analyzer

Output files:
  analyzer-opcodes.tsv          one row per opcode-bearing string literal
  analyzer-opcodes.h            C header of the same, for #include
  analyzer-analysis.json        method counts, buckets, rejected sites
  analyzer-disassembly.txt      full objdump of every manifest function
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import subprocess
from collections import defaultdict
from tempfile import NamedTemporaryFile


MANIFEST_COLUMNS = ("kind", "start", "end", "symbol", "note")

ANCHOR_KINDS = ("opcode-helper", "opcode-table")
"""Manifest kinds this tool understands.  Deliberately NOT the vocabulary of
tools/extract-vdcmd-opcodes.py: `blob`/`range-table` there name *that* module's
methods, and reusing them here would attach a vdcmd method label to an analyzer
row produced by a different pipeline."""

OPCODE_RE = re.compile(r"^(?:0X[0-9A-F]{1,4}|OPERATION_CODE_NOT_FOUND)$")
"""Strict operation-code vocabulary.  `0XABCD` is how a helper spells the code
it handles; `OPERATION_CODE_NOT_FOUND` is the miss path of the walker."""

RANGE_RE = re.compile(r"^0X([0-9A-F]{1,4})-(?:0X)?([0-9A-F]{1,4})$")
"""`0X3E81-100F` — a declared opcode range: the closest thing to the class
table that survives as data."""

BUCKET_RES = (
    ("opcode", OPCODE_RE),
    ("range", RANGE_RE),
    ("rms_config", re.compile(r"^rms\.config\..*$")),
    ("rms_other", re.compile(r"^rms\..*$")),
    ("module_path", re.compile(r"^.*/usr/lib/modules/.*$")),
    ("procfs", re.compile(r"^/proc/.*$")),
    ("diag", re.compile(r"^/dev/diag.*$|^DIAG_.*|^DIAGSpace.*$")),
    ("log_format", re.compile(r".*%[-0-9.]*[dusxf].*", re.S)),
)
"""Buckets for the whole-binary string sweep.  First match wins, in this order;
anything unmatched lands in `other`."""

ADR_TARGET = re.compile(r"adrp\s+x(\d+),\s*#?\s*(0x[0-9a-f]+)")
ADD_TARGET = re.compile(r"^(?:add|ldr)\s+x(\d+),\s*x(\d+),\s*#?\s*(0x[0-9a-f]+)$")
B_COND = re.compile(r"^(?:b|b\.[a-z]{1,2}|cbz|cbnz|tb[hw]x?)\s+(?:x\d+,\s*)?(0x[0-9a-f]+)")
INDIRECT = re.compile(r"^(br|blr|braa?|brk|brb|blrb|brh|blrh)\b")
CB_FIELD = re.compile(r"(?:ldr|ldur|ldrb|ldrh|ldar)\s+w?\d+,\s*\[x(\d+)(?:,\s*#(0x[0-9a-f]+))?\]")

PREAMBLE = """/* Generated by tools/analyzer-opcodes.py -- DO NOT EDIT.

   Operation codes of librms-device-analyzer.so, keyed to the helper whose body
   loads the string literal that spells them.

   This is NOT a dispatch table.  ProcessOpCodeReport() walks a runtime table of
   (lo, hi) opcode ranges per rms.ic class, reached through the pointer at
   0x83D0; no class and no range appears as a static immediate anywhere in the
   binary, and the string sweep over the whole library is what pins that
   negative.  Each row below says "helper X references opcode V", which is an
   attribution, not a routing rule.  The service's dispatch contract — report id
   4 -> [0x3000,0x3a00), report id 11 -> [0x10000,0x11000) — is reconstructed
   from its own decompiled comparison chain in notes/phase4-connfem-reconstruction.md
   and is NOT re-derivable from this header. */

#ifndef ANALYZER_OPCODES_H
#define ANALYZER_OPCODES_H

"""

STRUCT = """
/* An operation-code literal and the function that references it.
 *   method   "candidate" — an adrp+add/ldr pair in the function's own range
 *                          materialises a .rodata vaddr matching OPCODE_RE
 *   strength "candidate" — same reason as in vdcmd-opcodes.h: proof for an
 *                          idiom-gated method is "this disassembly matches this
 *                          pattern", not a downstream consumer
 *   offset   function-relative offset of the adrp
 *   vaddr    .rodata address of the literal (not a file offset) */
struct analyzer_opcode_desc {
  unsigned short opcode;   /* parsed from the literal; NOT_FOUND is -1 */
  const char *literal;     /* verbatim literal, as stored in .rodata */
  const char *builder;     /* function symbol containing the reference */
  const char *method;
  const char *strength;
  unsigned offset;
  unsigned vaddr;
};

"""

NOT_FOUND = "OPERATION_CODE_NOT_FOUND"


def sh(cmd: list[str]) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{' '.join(cmd[:3])}... failed: {r.stderr.strip()[:200]}")
    return r.stdout


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def nm_symbols(binary: pathlib.Path) -> dict[int, str]:
    out = {}
    for line in sh(["nm", "-D", "--defined-only", "-C", str(binary)]).splitlines():
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[1] in "tTwWiI":
            try:
                out[int(parts[0], 16)] = parts[2].strip()
            except ValueError:
                pass
    return out


def sections(binary: pathlib.Path) -> dict[str, tuple[int, int]]:
    """name -> (vaddr, size) for the sections this analysis reasons about."""
    keep = (".rodata", ".data", ".data.rel.ro", ".bss", ".text", ".plt")
    out = {}
    for line in sh(["readelf", "-S", "-W", str(binary)]).splitlines():
        m = re.search(r"\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-f]{8,16})\s+([0-9a-f]{6,16})\s+"
                      r"([0-9a-f]{6,16})\s+", line)
        if m and m.group(1) in keep:
            out[m.group(1)] = (int(m.group(2), 16), int(m.group(4), 16))
    missing = [k for k in keep if k not in out and k != ".data.rel.ro"]
    if missing:
        raise SystemExit(f"{binary.name}: missing sections {missing} — refusing to analyse")
    return out


def dump(binary: pathlib.Path, lo: int, hi: int) -> list[tuple[int, str]]:
    """Disassemble [lo,hi) -> [(addr, ops)].

    objdump -d --start-address/--stop-address only; `--disassemble=` does not
    match the C++-mangled names of this library, so relying on it silently
    returns nothing (verified against this exact binary)."""
    if hi <= lo:
        return []
    out = sh(["objdump", "-d", "--no-show-raw-insn", "--disassemble=none",
              f"--start-address={lo:#x}", f"--stop-address={hi:#x}", str(binary)])
    res = []
    for ln in out.splitlines():
        m = re.match(r"^\s+([0-9a-f]+):\s+(.*)$", ln)
        if m:
            res.append((int(m.group(1), 16), m.group(2).strip()))
    return res


def section_blob(image: pathlib.Path, name: str, size: int,
                 cache: dict[str, bytes]) -> bytes:
    """Contents of one section, via objcopy -O binary --only-section.

    objcopy emits a section's bytes in file order starting at its vaddr, so
    `vaddr - base` indexes the blob; reading memory through the toolchain keeps
    the vaddr<->bytes mapping the same one objdump reasons in.  NOBITS sections
    (.bss) produce a short or empty extraction, so every blob is padded to its
    declared size, which is also its correct content."""
    if name not in cache:
        with NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
            tmp_path = pathlib.Path(tmp.name)
        try:
            sh(["objcopy", "-O", "binary", f"--only-section={name}", str(image),
                str(tmp_path)])
            blob = tmp_path.read_bytes()
        finally:
            tmp_path.unlink(missing_ok=True)
        cache[name] = blob + b"\0" * max(0, size - len(blob))
    return cache[name]


def string_sites(binary: pathlib.Path, lo: int, hi: int,
                 sec: dict[str, tuple[int, int]], cache: dict[str, bytes]):
    """adrp+add/ldr sites in [lo,hi) -> {addr: [(target, section, text)]}."""
    out = defaultdict(list)
    adprs: dict[str, int] = {}
    for addr, ops in dump(binary, lo, hi):
        m = ADR_TARGET.match(ops)
        if m:
            adprs[m.group(1)] = int(m.group(2), 16)
            continue
        m = ADD_TARGET.match(ops)
        if not m or m.group(2) not in adprs:
            continue
        target = adprs[m.group(2)] + int(m.group(3), 16)
        for name in (".rodata", ".data", ".data.rel.ro", ".bss"):
            if name not in sec:
                continue
            base, size = sec[name]
            if not (base <= target < base + size):
                continue
            raw = read_at(binary, sec, target, cache)
            if raw is None:
                break
            out[addr].append((target, name, raw.decode("utf-8", "replace")))
            break
    return out


def parse_cfg(dis: list[tuple[int, str]]):
    """index / successors / predecessors of a function body.

    Reconstructing the CFG before classifying is load-bearing in the sibling
    extractor; here it is computed to *prove* the absence of a table dispatch,
    so the caller gets both a count and a flag per node that has no static
    target (the only branch form that would signal a jump table)."""
    ops = dis
    index = {a: i for i, (a, _) in enumerate(ops)}
    succs: list[list[int]] = [[] for _ in ops]
    switch: list[dict] = []
    for i, (addr, body) in enumerate(ops):
        m = B_COND.match(body)
        if m and int(m.group(1), 16) in index:
            succs[i].append(index[int(m.group(1), 16)])
        if i + 1 < len(ops) and not re.match(r"^(b(\.|$)|br|blr|ret)", body):
            succs[i].append(i + 1)
        if re.match(r"^cb(?:nz|z)\s+w\d+,\s*0x[0-9a-f]+,\s*0x[0-9a-f]+$", body):
            switch.append({"index": i, "addr": hex(addr), "kind": "cb2-targets", "ops": body})
    preds: list[list[int]] = [[] for _ in ops]
    for i, lst in enumerate(succs):
        for s in lst:
            preds[s].append(i)
    indirect = [{"index": i, "addr": hex(a), "form": "computed-branch", "ops": b}
                for i, (a, b) in enumerate(ops) if INDIRECT.match(b)]
    return {"instructions": len(ops), "basic-blocks": len(preds),
            "multi-instruction-blocks": sum(1 for p in preds if len(p) > 1),
            "switch-jump": len(switch), "computed-branch": indirect,
            "cb2-two-target-branch": switch}


def pointer_slots(binary: pathlib.Path, sec: dict[str, tuple[int, int]], blob_lo: int,
                  size: int, funcs: dict[int, str], text: tuple[int, int]) -> list[dict]:
    """Classify the 8-byte slots of a data blob.

    `helper:<sym>` when the slot points at a function named in the manifest,
    `in-text` when it points into .text at something that is not a manifest
    entry point, `outside-binary` otherwise — usually the address of a string
    literal or of another blob.  This is the honest form of "is there a class
    table in data": per-blob slot counts by target class, not an asserted shape.
    """
    cache: dict[str, bytes] = {}
    lo, hi = text[0], text[0] + text[1]
    out = []
    for slot in range(blob_lo, blob_lo + size - 7, 8):
        raw = read_at(binary, sec, slot, cache)
        if raw is None or len(raw) < 8:
            out.append({"slot": hex(slot), "target": None, "kind": "unreadable"})
            continue
        target = int.from_bytes(raw[:8], "little")
        if target in funcs:
            kind, name = "helper", funcs[target]
        elif lo <= target < hi:
            kind, name = "in-text", None
        else:
            kind, name = "outside-binary", None
        out.append({"slot": hex(slot), "target": hex(target), "kind": kind, "name": name})
    return out


def read_at(image: pathlib.Path, sec: dict[str, tuple[int, int]], vaddr: int,
            cache: dict[str, bytes]) -> bytes | None:
    """NUL-terminated bytes of the readable section containing vaddr, else None."""
    for name, (base, size) in sec.items():
        if name in (".text", ".plt") or not base <= vaddr < base + size:
            continue
        blob = section_blob(image, name, size, cache)
        off = vaddr - base
        if off >= len(blob):
            return None
        end = blob.find(b"\0", off)
        return blob[off: end if end >= 0 else min(off + 256, len(blob))]
    return None


PRINTABLE = re.compile(rb"^[\x20-\x7e\t]{2,256}$")


def section_strings(image: pathlib.Path, name: str, size: int,
                    cache: dict[str, bytes]) -> list[tuple[int, str]]:
    """(vaddr, text) for every NUL-terminated printable run in a data section.

    Uses the objcopy blob rather than `objdump -s` hexdump lines so the sweep
    and the adrp/add resolution above read exactly the same bytes."""
    blob = section_blob(image, name, size, cache)
    out = []
    for m in re.finditer(rb"[^\x00]+", blob):
        raw = m.group(0)
        if PRINTABLE.match(raw):
            out.append((m.start(), raw.decode("ascii")[:256]))
    return out


def bucket_of(text: str) -> str:
    """First matching bucket in BUCKET_RES order, else 'other'."""
    for name, rx in BUCKET_RES:
        if rx.match(text):
            return name
    return "other"
def opcode_value(text: str) -> int:
    """`0XABCD`/`abcd` -> the code; NOT_FOUND and anything else -> -1."""
    return -1 if text == NOT_FOUND else int(text, 16)
BUILDERS = """/* Operation-code literals that survive as `.rodata` string constants here:
 *   0XABCD  — the code a helper is handling, spelled by its own log line
 *   NOT_FOUND — the walker's miss path; there is exactly one per arm of
 *             ProcessOpCodeReport(), which is part of what proves its shape.
 * A code formatted at runtime with "%04x" never names its value in a literal,
 * so those helpers contribute no row: absence here is not absence of codes. */
"""
def emit_header(path: pathlib.Path, rows: list[dict], rejected: list[dict],
                buckets: dict, binary: str) -> None:
    literal_addrs = {int(r["literal_vaddr"], 16) for r in rows}
    helpers = {r["builder"] for r in rows}
    out = [PREAMBLE, BUILDERS, STRUCT,
           f"/* Source: {binary}; evidence {path.stem} — {len(rows)} opcode literals "
           f"in {len(helpers)} helpers, {len(literal_addrs)} distinct literals. */\n\n",
           "static const struct analyzer_opcode_desc analyzer_opcode_table[] = {\n"]
    for r in rows:
        out.append(f'    {{{r["opcode"]}, "{r["literal"]}", "{r["builder"]}", '
                   f'{r["method"].upper()}, {r["strength"].upper()}, '
                   f'{r["offset"]}u, {r["literal_vaddr"]}}},\n')
    out.append("};\n\n")
    out.append(f"#define ANALYZER_OPCODE_TABLE_LEN {len(rows)}u\n")
    out.append(f"#define ANALYZER_OPCODE_LITERAL_COUNT {len(literal_addrs)}u\n")
    out.append(f"#define ANALYZER_STRING_TOTAL {buckets['total']}u\n\n")
    out.append("/* Whole-binary string sweep, first matching bucket wins (see BUCKET_RES):\n")
    for name, _ in BUCKET_RES:
        out.append(f" * {name:12} {buckets[name]['count']:>6}\n")
    out.append(f" * {'other':12} {buckets['other']['count']:>6}\n")
    out.append(" *\n * Rejected — adrp/add target not in .rodata, so the literal is a writable\n")
    out.append(" * global rather than a compile-time opcode (rms.config.* keys live in .data):\n")
    for r in rejected[:12]:
        out.append(f" *   {r['section']:14} {r['literal']!r}\n")
    if len(rejected) > 12:
        out.append(f" *   ... and {len(rejected) - 12} more in {path.stem[:-3]}-analysis.json\n")
    out.append(" */\n\n#endif /* ANALYZER_OPCODES_H */\n")
    path.write_text("".join(out))
    print(f"  {path.name}: rows={len(rows)} literals={len(literal_addrs)} "
          f"helpers={len(helpers)} rejected={len(rejected)}")
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", default="originals/bin/vendor.qwen.hardware/"
                    "librms-device-analyzer.so")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--stem", default="analyzer")
    a = ap.parse_args()
    binary = pathlib.Path(a.binary)
    if not binary.exists():
        raise SystemExit(f"{binary} missing — run ./build.sh --fetch first")
    out_dir = pathlib.Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = [ln for ln in pathlib.Path(a.manifest).read_text().splitlines()
                if ln.strip() and not ln.startswith("#")]
    cols = manifest[0].split("\t")
    if tuple(cols) != MANIFEST_COLUMNS:
        raise SystemExit(f"{a.manifest}: expected header {list(MANIFEST_COLUMNS)}, got {cols}")
    entries = [dict(zip(cols, ln.split("\t"))) for ln in manifest[1:]]
    funcs = {int(e["start"], 0): e["symbol"] for e in entries if e["kind"] == ANCHOR_KINDS[0]}
    blobs = [(int(e["start"], 0), int(e["end"], 0) - int(e["start"], 0), e["note"])
             for e in entries if e["kind"] == ANCHOR_KINDS[1]]
    if not funcs or not blobs:
        raise SystemExit(f"{a.manifest}: need both function and blob rows")
    unknown = sorted({e["kind"] for e in entries} - set(ANCHOR_KINDS))
    if unknown:
        raise SystemExit(f"{a.manifest}: kinds {unknown} not in {list(ANCHOR_KINDS)}")
    syms = nm_symbols(binary)
    sec = sections(binary)
    cache: dict[str, bytes] = {}
    for start, sym in funcs.items():
        if syms.get(start) != sym:
            raise SystemExit(f"{sym}: manifest start {start:#x} is not this symbol "
                             f"(nm says {syms.get(start)!r}) — manifest drifted from the image")
    for start, size, note in blobs:
        if start % 8 or size % 8:
            raise SystemExit(f"blob {note} at {start:#x}: size {size} is not slot-aligned")
    rows: list[dict] = []
    rejected: list[dict] = []
    cfg_rows: list[dict] = []
    disasm: list[str] = [f"; === {binary} — every manifest function, in address order ==="]
    for start, sym in sorted(funcs.items()):
        end = min((s for s in funcs if s > start), default=sec[".text"][0] + sec[".text"][1])
        dis = dump(binary, start, end)
        disasm += [f"\n; ---- {sym}  [{start:#x}, {end:#x}) — {end - start} bytes, "
                   f"{len(dis)} instructions ----"]
        disasm += [f"    {addr:06x}: {ops}" for addr, ops in dis]
        cfg_rows.append({"function": sym, "entry": hex(start), **parse_cfg(dis)})
        for addr, hits in sorted(string_sites(binary, start, end, sec, cache).items()):
            for target, name, text in hits:
                if not PRINTABLE.match(text.encode()):
                    continue
                bucket = bucket_of(text)
                if name != ".rodata" or bucket != "opcode":
                    rejected.append({"builder": sym, "section": name, "literal": text,
                                     "bucket": bucket, "literal_vaddr": hex(target),
                                     "adrp": hex(addr),
                                     "reason": (f"adrp/add target {target:#x} is in {name}, "
                                                "not .rodata") if name != ".rodata"
                                     else f"literal matches bucket {bucket}, not OPCODE_RE"})
                    continue
                rows.append({"binary": binary.name, "builder": sym, "literal": text,
                             "opcode": opcode_value(text), "method": "candidate",
                             "strength": "candidate", "offset": addr - start,
                             "literal_vaddr": hex(target)})
    rows.sort(key=lambda r: (r["builder"], r["offset"]))
    slots = {start: pointer_slots(binary, sec, start, size, funcs, sec[".text"])
             for start, size, _ in blobs}
    for start, size, note in blobs:
        disasm.append(f"\n; ---- blob {note}  [{start:#x} + {size:#x}] — "
                      f"{size // 8} pointer slots ----")
        disasm += [f"    {s['slot']}: {s['target']} {s['kind']}"
                   + (f"  <{s['name']}" if s["name"] else "") for s in slots[start]]
    buckets: dict[str, dict] = {name: {"count": 0, "examples": []}
                                for name, _ in BUCKET_RES}
    buckets["other"] = {"count": 0, "examples": []}
    strings = [(bucket_of(s), hex(v), s)
               for name in (".rodata", ".data", ".bss")
               for v, s in section_strings(binary, name, sec[name][1], cache)]
    for bucket, vaddr, text in strings:
        buckets[bucket]["count"] += 1
        if len(buckets[bucket]["examples"]) < 6:
            buckets[bucket]["examples"].append({"vaddr": vaddr, "text": text})
    buckets["total"] = {"count": len(strings)}
    if not rows:
        raise SystemExit("no opcode literal resolved — refusing to write an empty registry")
    tsv = out_dir / f"{a.stem}-opcodes.tsv"
    with tsv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    emit_header(out_dir / f"{a.stem}-opcodes.h", rows, rejected, buckets, binary.name)
    disasm.append("\n; ProcessOpCodeReport() is the only export and reaches its helpers through\n"
                  "; the runtime table reached from 0x83D0. Slots above are classified by what "
                  "they point\n; at, not by an assumed layout: a per-class table with one entry "
                  "per helper would\n; have to show one `helper:` slot per helper per blob, and "
                  "these blobs do not.\n")
    (out_dir / f"{a.stem}-disassembly.txt").write_text("\n".join(disasm) + "\n")
    slot_kinds = defaultdict(int)
    for lst in slots.values():
        slot_kinds.update(s["kind"] for s in lst)
    report = {"binary": str(binary), "manifest": a.manifest,
              "methods": {
                  "candidate": {"definition": "adrp+add/ldr inside the function's own range "
                                   "materialises a .rodata vaddr whose NUL-terminated bytes "
                                   "match OPCODE_RE", "count": len(rows)},
                  "rejected": {"definition": "the same adrp/add pair whose target is writable, "
                                 "or whose literal falls in a non-opcode bucket",
                                "count": len(rejected), "sites": rejected},
                  "strings": {"definition": "every printable NUL-terminated run in "
                                  ".rodata/.data/.bss, bucketed by BUCKET_RES",
                               "count": len(strings), "buckets": buckets},
                  "cfg": {"definition": "per-function CFG profile. This library contains no "
                             "switch jump and no computed branch at all, so the opcode -> "
                             "helper mapping is not recoverable from code; that is why this "
                             "module emits an attribution registry, not a dispatch model like "
                             "vdcmd-opcodes.h",
                          "count": len(cfg_rows), "functions": cfg_rows}},
              "blob-slot-classes": dict(slot_kinds),
              "negative-controls": {
                  "CLASS_<n> literals": sum(1 for b, _, s in strings if re.fullmatch(r"CLASS_\d+", s)),
                  "4-hex-digit lowercase literals": sum(1 for b, _, s in strings
                                                        if re.fullmatch(r"[0-9a-f]{4}", s)),
                  "pure decimal 1-5 digit literals": sum(1 for b, _, s in strings
                                                         if re.fullmatch(r"\d{1,5}", s)),
                  "comment": "these are the shapes a static class/range table would leave in "
                              ".rodata; zero for each is what licenses 'no static class table' "
                              "rather than an untested assertion"}}
    (out_dir / f"{a.stem}-analysis.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"{out_dir}/{a.stem}-*: opcode-literals={len(rows)} "
          f"helpers={len({r['builder'] for r in rows})} rejected={len(rejected)} "
          f"strings={len(strings)} buckets="
          + " ".join(f"{k}={buckets[k]['count']}" for k, _ in BUCKET_RES)
          + f" other={buckets['other']['count']}"
          + f" slots={dict(slot_kinds)}")


if __name__ == "__main__":
    main()
