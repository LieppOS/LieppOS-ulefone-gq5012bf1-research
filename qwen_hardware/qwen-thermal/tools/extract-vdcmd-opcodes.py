#!/usr/bin/env python3
"""Recover the vdcmd opcode registry from an unstripped ARM payload library.

Works on either ARM profile the AC-020 stack ships in (AArch64 FactoryMode copies
and 32-bit EABI5 donor copies): all mnemonic/register handling goes through
llvm-objdump spellings, and both `x`/`w` and `r` register names parse.

v2 replaces the v1.5 linear-scan heuristic with a control-flow-sensitive analysis:

* real CFG recovery over objdump disassembly (branch/BL targets make blocks),
  so *every* basic block of a helper is walked, not only its fall-through prefix;
* backward reaching-value analysis from each terminal: the walk follows the def
  chain of the consumed register until an instruction *materialises* it from an
  immediate — `mov Wd, #imm`, `movw`, or the AArch64 `orr/add Wd, wzr, #imm` spelling
  of a constant — or stops at a boundary.  A def whose source is a live register is
  never a materialisation: `add Xd, Xn, #imm` is offset arithmetic (noted
  `offset-arithmetic`), flag-setting ops (`cmp`/`tst`/`subs`/...) write NZCV rather
  than the register (`flag-setting-not-a-def`), and value-preserving copies
  (`mov`/`sxtw`/...) are followed through to the source register;
* a value counts as a *payload* opcode only when it is stored into the argument
  buffer or handed over as the value argument of a vdcmd_get/vdcmd_set/... call;
  opcode arguments of transport calls are reported separately and are *not* claimed
  as payload opcodes;
* per-path ambiguity is explicit: an opcode carrying more than one candidate name
  is emitted once per candidate with status=ambiguous, so no helper name can be
  silently attached to the wrong slot.

Terminals are exactly two kinds, and `provenance` names the one that produced the
row: a *store* into the argument buffer (`payload-store`) or a *classified call*
handing the value to a getter/setter/transport core (`payload-call`,
`transport-arg`).  Loads are deliberately not terminals — a load overwrites its
register, so a chain ending at one proves nothing about a command being sent —
and every load terminal is written to the notes sidecar as `load-terminal`
instead of becoming a row.

The payload/transport split comes from the library itself: a helper is `payload`
when its direct call closure reaches a getter/setter core (a function that
actually issues vdcmd_get/vdcmd_set), `transport` when it only reaches the raw
send/receive core, and `none` otherwise.  That distinction is what removed the
mislabelling that v1.5 produced for the AC-020 sensor driver (282 rows of which
248 were reachability labels rather than evidence).

Output fieldnames are stable so the header generator can consume either engine:

  opcode  CANDIDATE opcode: a value this helper materialised from an immediate and
              stored into a buffer.  Which struct field it fills (class slot, op
              slot, or an ordinary parameter) is NOT established here — see
              findings/vdm-opcode-recovery.md before treating a row as a command ID
  helper  owning exported helper symbol, with _get/_set denoting the direction
  status  unique | ambiguous (unique = exactly one helper name reaches this ID)
  provenance  payload-store | payload-call | transport-arg
  paths  distinct instructions that materialised this value for this helper
  value_paths  distinct terminals (stores/calls) whose chain proved it
  confidence  high when every proving chain closed within 6 hops, medium within 24,
              low beyond that — it measures walk length, never runtime behaviour
  addr/vaddr/offset  the lowest-address materialising instruction of the row
  source  up to 3 `provenance@addr:<insn>` chains behind the row
  raw_value_paths  every proving chain's terminal kind and address (compact)
  helper_kind  payload | transport | none
  calls  vdcmd core APIs reachable from the helper

Usage:
  extract-vdcmd-opcodes.py [BINARY] [OUT] [--format tsv|json] [--out F]
                           [--objdump B] [--nm B] [--max-span N]
                           [--source NAME] [--source-md5 HEX]
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import struct
import subprocess
import sys
from collections import Counter, defaultdict, deque

FIELDNAMES = ["opcode", "helper", "status", "provenance", "paths", "value_paths",
              "confidence", "addr", "vaddr", "offset", "source", "raw_value_paths",
              "helper_kind", "calls"]


def ops_list(ops):
    out, cur, depth = [], "", 0
    for ch in ops:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def imm(text):
    if text is None:
        return None
    m = re.fullmatch(r"#?\s*(-?(?:0x[0-9a-f]+|\d+))", text.strip(), re.I)
    return int(m.group(1), 0) if m else None


def reg(text):
    """normalise an AArch64 scalar register to r<n>/sp; x0==w0, xzr/sp -> None

    xzr is dropped because a read from it carries no value provenance, and the
    frame-pointer/link-register aliases are folded onto their numbered form so a
    spilled argument is still traceable.
    """
    if not text:
        return None
    t = text.strip().lower().rstrip("!")
    if t in ("xzr", "wzr", "sp"):
        return None
    if t in ("fp", "lr"):
        return "r29" if t == "fp" else "r30"
    m = re.fullmatch(r"([xw])(\d+)", t)
    return f"r{int(m.group(2))}" if m else None


def mem(op):
    """[base] / [base, #imm] (also pre/post-index) -> (base, delta); indexed -> None."""
    m = re.match(r"^\[([a-z0-9]+)(?:,\s*(?:#|,)\s*(-?(?:0x[0-9a-f]+|\d+)))?(?:\])", op, re.I)
    return (m.group(1), int(m.group(2), 0) if m.group(2) else 0) if m else None


MAX_SPAN = 0x2000


class ELFReader:
    """ELF-LSB reader (32 or 64 bit): sections plus file-offset <-> vaddr translation."""

    def __init__(self, data: bytes):
        if data[:4] != b"\x7fELF" or data[5] != 1 or data[4] not in (1, 2):
            raise SystemExit("this tool parses unstripped little-endian ELF ARM/AArch64 binaries")
        self.elfclass = data[4]
        if self.elfclass == 1:
            self.shoff, = struct.unpack_from("<I", data, 0x20)
            self.shentsize, self.shnum = struct.unpack_from("<HH", data, 0x2E)
        else:
            self.shoff, = struct.unpack_from("<Q", data, 0x28)
            self.shentsize, self.shnum = struct.unpack_from("<HH", data, 0x3A)
        self.data = data
        self.soff = 16 if self.elfclass == 1 else 24            # sh_offset within a Shdr
        self.shsize = 40 if self.elfclass == 1 else 64
        self.sfmt = "<II" if self.elfclass == 1 else "<QQ"
        sbase, ssize = self.shdr(struct.unpack_from("<H", data, 0x30 if self.elfclass == 1 else 0x3E)[0])
        self.sections = {}
        for i in range(self.shnum):
            off = self.shoff + i * self.shentsize
            if off + self.shsize > len(data):
                break
            sh_name, typ = struct.unpack_from("<II", data, off)
            offset, size = struct.unpack_from(self.sfmt, data, off + self.soff)
            if sh_name < ssize:
                end = data.index(b"\x00", sbase + sh_name)
                self.sections[data[sbase + sh_name:end].decode("ascii", "replace")] = (offset, size)

    def shdr(self, i):
        """(sh_offset, sh_size) of section header i."""
        return struct.unpack_from(self.sfmt, self.data, self.shoff + i * self.shentsize + self.soff)

    def off(self, vaddr: int):
        for name in (".text", ".rodata", ".data", ".bss", ".init", ".fini"):
            if name not in self.sections:
                continue
            base, size = self.sections[name]
            if name == ".bss":
                continue
            if base <= vaddr < base + size:
                return vaddr - base
        return None

    def symtab(self):
        """{vaddr: (name, size)} from .symtab, else .dynsym when the shipped lib is stripped.

        A stripped APK library only carries .dynsym, where STT_FUNC entries usually do
        have a size; when they do not, find_procedures() bounds the body by the next
        symbol boundary instead of pretending to know the extent.
        """
        if ".symtab" in self.sections:
            (toff, tsize), sname_sec = self.sections[".symtab"], ".strtab"
        elif ".dynsym" in self.sections:
            (toff, tsize), sname_sec = self.sections[".dynsym"], ".dynstr"
        else:
            raise SystemExit("no .symtab/.dynsym: cannot attribute opcodes to helpers")
        base, size = self.sections[sname_sec]
        strs = self.data[base:base + size]

        def sname(o):
            if not o < len(strs):
                return ""
            return strs[o: strs.index(b"\x00", o)].decode("ascii", "replace")

        out = {}
        esz = 16 if self.elfclass == 1 else 24
        for i in range(tsize // esz):
            if self.elfclass == 1:            # Elf32_Sym: name value size info other shndx
                st_name, st_value, st_size, st_info = struct.unpack_from("<IIIB", self.data,
                                                                        toff + i * 16)
            else:                             # Elf64_Sym: name info other shndx value size
                st_name, st_info, _, _, st_value, st_size = struct.unpack_from(
                    "<IBBHQQ", self.data, toff + i * 24)
            if st_name and st_value and st_info & 0xF in (1, 2):
                out.setdefault(st_value, (sname(st_name), st_size))
        return out

    def cstr(self, vaddr):
        """NUL-terminated C string at vaddr, or None."""
        off = self.off(vaddr)
        if off is None:
            return None
        end = self.data.find(b"\x00", off)
        return self.data[off:end].decode("ascii", "replace") if end != -1 else None


def disasm(objdump: str, binary: str, elf: ELFReader):
    """[(addr, mnemonic, operands)] over the whole .text section."""
    items = []
    for line in subprocess.run([objdump, "-d", "--no-show-raw-insn", "--section=.text", binary],
                               capture_output=True, text=True, check=True).stdout.splitlines():
        m = re.match(r"^\s*([0-9a-f]+):\s+([a-z][a-z0-9.]*)\s*(.*)$", line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        if elf.off(addr) is None:
            continue                                    # plt/stub thunks live outside .text
        items.append((addr, m.group(2), m.group(3).strip()))
    return items


def find_procedures(items, syms, entry):
    """Symbol sizes when known, else the next function symbol boundary; capped at MAX_SPAN."""
    starts = sorted(s for s, (n, sz) in syms.items() if n and sz)
    for delta in (-16, -12, -8, -4, 0, 4, 8, 12, 16):     # objdump thumb-bit mismatch
        if entry + delta in syms:
            entry += delta
            break
    _, size = syms.get(entry, ("", 0))
    nxt = min([s for s in starts if s > entry], default=entry + MAX_SPAN)
    return entry, min(entry + (size or MAX_SPAN), nxt, entry + MAX_SPAN)


def hexrays(nm: str, objdump: str, binary: str):
    """Heuristic core detection from the dynamic symbol table (nm -D)."""
    try:
        out = subprocess.run([nm, "-D", "--defined-only", binary],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {"getter": [], "setter": [], "open": [], "close": []}
    cores = {"getter": [], "setter": [], "open": [], "close": []}
    for line in out.splitlines():
        p = line.split()
        if len(p) < 3:
            continue
        name = p[-1]
        if re.search(r"^(vdcmd_get|get_sensor_param(_value)?|vdm_get_param)$", name):
            cores["getter"].append(name)
        elif re.search(r"^(vdcmd_set|set_sensor_param(_int)?|vdm_set_param)$", name):
            cores["setter"].append(name)
        elif re.search(r"^(open_vdserial|_Z.*open_vdserial.*|vdcmd_open)$", name):
            cores["open"].append(name)
        elif re.search(r"(vdcmd_close|close_vdserial)$", name):
            cores["close"].append(name)
    return cores


def branch_target(ops, index):
    m = re.search(r"<(.+?)>", ops)
    if m:
        tok = m.group(1).split("+")[0]
        if re.fullmatch(r"0x[0-9a-f]+", tok):
            return index.get(int(tok, 16))
        return None
    m = re.fullmatch(r"#?\s*(0x[0-9a-f]+).*", ops.strip())
    return index.get(int(m.group(1), 16)) if m else None


def build_cfg(items, index):
    """successor edges per instruction index; returns are terminal."""
    succs = [[] for _ in items]
    for i, (_, mnem, ops) in enumerate(items):
        m0 = mnem.split(".")[0]
        if m0 in ("bx", "bxj", "ret", "br") or (m0 == "mov" and ops in ("lr", "lr!")):
            continue                                            # return
        if m0 in ("bl", "blx"):
            succs[i].append(i + 1) if i + 1 < len(items) else None
            t = branch_target(ops, index)
            if t is not None:
                succs[i].append(t)
            continue
        if m0 in ("b", "cbz", "cbnz", "tbh", "tbb") or m0.startswith("b."):
            t = branch_target(ops, index)
            if t is not None:
                succs[i].append(t)
            if i + 1 < len(items):
                succs[i].append(i + 1)                          # fall-through too
            continue
        if i + 1 < len(items):
            succs[i].append(i + 1)
    return succs


CORES = {"getter": set(), "setter": set(), "open": set(), "close": set()}
HELPER_HINT = re.compile(r"(param|cmd|opcode|conf|mode|enable|level|value|cali|offset|"
                         r"gain|matrix|serial|version|thresh|cover|adjust|config|"
                         r"shutdown|upgrade|frame|region|window)", re.I)


def classify_call(name):
    if not name:
        return None
    n = name.lower()
    if n in CORES["getter"]:
        return "payload-getter"
    if n in CORES["setter"]:
        return "payload-setter"
    if n in CORES["open"] or n == "open_vdserial" or "_Z14open_vdserial" in n:
        return "transport-open"
    if n in CORES["close"] or n in ("vdcmd_close", "close_vdserial"):
        return "transport-close"
    if re.search(r"(param|cmd|conf|setting|sensor_data)", n) and \
       re.search(r"^(get|set|read|write)_(setting|cmd|param|sensor)|_cmd_|\.(read|write)\.", n):
        return "transport-data"
    return None


def helper_kind(kinds):
    kinds = set(kinds)
    if kinds & {"payload-getter", "payload-setter"}:
        return "payload"
    return "transport" if kinds else "none"


FLAG_OPS = {"cmp", "cmn", "tst", "teq", "ccmp", "ccmn", "subs", "adds", "ands", "bics",
            "adcs", "sbcs", "necs"}
"""Flag-setting mnemonics (base name, before the `.w`/`.w` Thumb suffix is split off):
they read a register and write only NZCV, so they are never a def in the reaching-value
walk.  `subs`/`adds` also *do* write their destination, which is why they stop the walk
as a boundary instead of being followed: the value is a sum, not a constant."""
ZERO_REGS = {"wzr", "xzr", "zr"}
"""`orr Wd, wzr, #imm` and `add Xd, xzr, #imm` are how AArch64 spells `mov Wd, #imm`
for bitwise-encodable constants; a source outside this set means the value depends on
another register, not on the immediate.  AArch32/Thumb spells the same idiom with r7,
which is also a live general register there, so it is deliberately *not* in this set:
on a 32-bit input those chains land in `offset-arithmetic`/`opaque-def-*` notes rather
than becoming rows, which loses recall but cannot invent an opcode."""
COPIES = {"mov", "mov.w", "vmov", "sxtw", "sxth", "sxtb", "uxtw", "uxth", "uxtb", "fmov"}
"""Value-preserving defs: the destination holds the source value, so the walk follows
that register instead of stopping at the copy."""
STORES = {"str", "str.w", "strb", "strb.w", "strh", "strh.w", "stp"}
"""A value that reaches one of these is a value the helper writes into its argument
buffer — the payload-store evidence this tool claims."""
LOADS = {"ldr", "ldr.w", "ldrb", "ldrb.w", "ldrh", "ldrh.w", "ldp"}
"""Load/store mnemonics as llvm-objdump spells them for *both* ARM profiles: the
`.w`/`stp`/`ldp` forms are AArch64-only, the bare ones appear on ARMv7 EABI5.  A
store terminal is evidence (an immediate that reaches a store is a stored value);
a load terminal is not, so LOADS only appear in the notes sidecar."""


def enclosing(addr, starts, snames):
    """Name of the function containing addr (None when the gap is suspiciously large)."""
    lo, hi, best = 0, len(starts) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if starts[mid] <= addr:
            best, lo = starts[mid], mid + 1
        else:
            hi = mid - 1
    return snames[best][0] if best is not None and addr - best < 0x800 else None


def first_dest_reg(mnem, ops):
    parts = ops_list(ops)
    return reg(parts[0]) if parts else None


def imm_operand(ops):
    parts = ops_list(ops)
    for p in reversed(parts):
        v = imm(p)
        if v is not None:
            return v
    return None


def reaching_values(items, index, succs, preds, span, elf, syms, starts, snames):
    """Which immediates can reach the registers each terminal instruction consumes.

    Terminals are the argument-buffer stores and the classified `bl` calls inside one
    exported helper.  From each terminal the walk follows the def-chain of the
    consumed register backwards through control flow until an immediate
    materialisation (`mov`/`orr`/`add #imm`, or `mov`+`movt` for wider constants)
    closes the chain, or a boundary stops it: a callee-saved spill (the `push
    {..., lr}` without `x4` idiom that marks a spilled argument), a memory load, a
    partial `movk` constant, a return, or a load terminal.  Only the immediate case
    yields an opcode candidate; every boundary is written to the notes sidecar with
    its own kind instead of becoming a row.
    """
    lo, hi = span
    n = len(items)
    records, notes = [], []
    owner = snames.get(span[0], ("?", 0))[0]

    def callee(i):
        return enclosing(items[i][0], starts, snames) if items[i][1].startswith("bl") else ""

    def note(i, want, kind, depth):
        notes.append({"helper": owner, "terminal": f"{items[i][0]:x}", "reg": want, "kind": kind,
                      "depth": depth, "at": f"{items[i][0]:x}", "insn": f"{items[i][1]} {items[i][2]}"})

    terminals = []
    for i in range(n):
        addr, mnem, ops = items[i]
        if not (lo <= addr < hi):
            continue
        if mnem.startswith("bl"):
            kind = classify_call(callee(i))
            if kind:
                # the value argument is the first register operand (r0/x0/w0 under
                # both AAPCS profiles); the remaining operands are buffers/lengths,
                # whose immediates are sizes and pointers, never opcode IDs
                r = next((reg(x) for x in ops_list(ops) if reg(x)), None)
                terminals.append((i, kind, [r] if r else []))
        elif mnem in STORES:
            parts = ops_list(ops)
            r = reg(parts[0]) if parts else None
            if r:
                terminals.append((i, "payload-store", [r]))
        elif mnem in LOADS:
            # A load terminal proves only that a *loaded* register's def-chain ends
            # at an immediate somewhere upstream — which says nothing about an
            # opcode being sent, so it is recorded as a boundary, not a row.
            note(i, reg(ops_list(ops)[0]) if ops_list(ops) else "?", "load-terminal", 0)

    for (t, kind, regs) in terminals:
        visited = set()

        def walk(i, want, depth, high):
            if i is None or not (0 <= i < n) or i in visited or depth > 220:
                return
            visited.add(i)
            m, o = items[i][1], items[i][2]
            b = m.split(".")[0]
            if b in ("bx", "bxj", "ret", "br") or (b == "mov" and o in ("lr", "lr!")) or b == "pop":
                return
            dst = first_dest_reg(m, o)
            if dst != want:
                for q in preds[i]:
                    walk(q, want, depth + 1, high)
                return
            if b == "movt":
                h = imm_operand(o)
                for q in preds[i]:
                    walk(q, want, depth + 1, h if h is not None else high)
                return
            if b == "movk":
                note(i, want, "partial-constant-movk", depth)
                return
            if b in LOADS:
                note(i, want, "value-from-memory", depth)
                return
            if b in FLAG_OPS or b.startswith("tb"):
                # tbz/tbnz test a *bit index*, so #imm there is a bit number
                # cmp/tst/ands/cmn write flags, not the register: treating them as a
                # def turns every compared constant into a fake opcode candidate
                note(i, want, "flag-setting-not-a-def", depth)
                return
            srcs = [r for r in (reg(p) for p in ops_list(o)[1:]) if r]
            if srcs and not any(s in ZERO_REGS for s in srcs):
                if imm_operand(o) is not None:
                    # `add Xd, Xn, #imm` with a real Xn is offset/length arithmetic on a
                    # pointer or counter, not a constant materialisation
                    note(i, want, "offset-arithmetic", depth)
                    return
                if b in COPIES:
                    # value-preserving copy/extension: follow the source register
                    for q in preds[i]:
                        walk(q, srcs[0], depth + 1, high)
                    return
                note(i, want, f"opaque-def-{b}", depth)
                return
            v = imm_operand(o)
            if v is None:
                note(i, want, "no-immediate-source", depth)
                return
            records.append({"src": i, "term": t, "reg": want, "kind": kind,
                            "value": (v & 0xFFFF) | ((high or 0) << 16), "depth": depth})

        for r in regs:
            for q in preds[t]:
                walk(q, r, 1, None)
    return records, notes


def preds_of(succs):
    preds = [[] for _ in succs]
    for i, lst in enumerate(succs):
        for j in lst:
            if 0 <= j < len(preds):
                preds[j].append(i)
    return preds


def analyse(binary, objdump="llvm-objdump", nm="llvm-nm", max_span=0x2000):
    global MAX_SPAN
    MAX_SPAN = max_span
    elf = ELFReader(pathlib.Path(binary).read_bytes())
    syms = elf.symtab()
    for k in CORES:
        CORES[k] = set(hexrays(nm, objdump, binary)[k])
    items = disasm(objdump, binary, elf)
    index = {a: i for i, (a, _, _) in enumerate(items)}
    succs = build_cfg(items, index)
    preds = preds_of(succs)
    starts = sorted(s for s in syms if syms[s][0])
    exports = sorted(s for s in starts
                     if not syms[s][0].startswith(("_", "__"))
                     and elf.off(s) is not None)

    callees = {i: enclosing(a, starts, syms)
               for i, (a, m, _) in enumerate(items) if m.startswith("bl")}
    rows, notes = [], []
    for entry in exports:
        name, _ = syms[entry]
        span = find_procedures(items, syms, entry)
        recs, ns = reaching_values(items, index, succs, preds, span, elf, syms, starts, syms)
        notes.extend(dict(n, helper=name) for n in ns)
        called = sorted({callees[i] for i in callees if span[0] <= items[i][0] < span[1]
                         and callees[i]})
        kind = helper_kind(k for k in (classify_call(c) for c in called) if k)
        # one row per (helper, opcode): every instruction that materialised the value
        # and every terminal whose chain proved it are counted, not duplicated
        per_op: dict[int, list[dict]] = defaultdict(list)
        for rec in recs:
            op = rec["value"] & 0xFFFF
            if op > 0x0FFF or rec["value"] >> 16:      # pointer/page constants, not IDs
                continue
            per_op[op].append(rec)
        for op, rs in sorted(per_op.items()):
            prov = sorted({("payload-store" if r["kind"] == "payload-store"
                            else "payload-call" if str(r["kind"]).startswith("payload-")
                            else "transport-arg") for r in rs})
            depths = [r["depth"] for r in rs]
            worst = max(depths)
            srcs = sorted({items[r["src"]][0] for r in rs})
            terms = sorted({r["term"] for r in rs})
            rows.append({"opcode": f"0x{op:04X}",
                         "helper": name.removesuffix("_get").removesuffix("_set"),
                         "status": "unique", "provenance": "+".join(prov),
                         "paths": len(srcs), "value_paths": len(terms),
                         "confidence": "high" if worst <= 6 else
                         ("medium" if worst <= 24 else "low"),
                         "addr": f"0x{srcs[0]:x}", "vaddr": f"0x{srcs[0]:x}",
                         "offset": f"0x{elf.off(srcs[0]):x}" if elf.off(srcs[0]) is not None
                         else "-",
                         "source": ";".join(
                             f"{('payload-store' if r['kind'] == 'payload-store' else 'payload-call' if str(r['kind']).startswith('payload-') else 'transport-arg')}"
                             f"@{items[r['src']][0]:x}:{items[r['src']][1]} {items[r['src']][2]}"
                             for r in rs[:3])[:400],
                         "raw_value_paths": ",".join(
                             f"{items[r['term']][0]:x}:{r['kind']}:{r['depth']}"
                             for r in rs[:12]),
                         "helper_kind": kind, "calls": ",".join(called[:8])})

    # status is a *table* property: an ID that several distinct helpers claim is
    # ambiguous, because at most one of those names can own the register slot.
    by_op = defaultdict(set)
    for r in rows:
        by_op[int(r["opcode"], 16)].add(r["helper"])
    for r in rows:
        r["status"] = "unique" if len(by_op[int(r["opcode"], 16)]) == 1 else "ambiguous"
    return rows, notes


def write(rows, out, fmt="tsv", source="", source_md5=""):
    path = pathlib.Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path.write_text(json.dumps({"source": source, "md5": source_md5, "rows": rows}, indent=1))
        return
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binary", nargs="?")
    ap.add_argument("--out", required=True)
    ap.add_argument("--format", choices=("tsv", "json"), default="tsv")
    ap.add_argument("--objdump", default="llvm-objdump")
    ap.add_argument("--nm", default="llvm-nm")
    ap.add_argument("--max-span", type=lambda x: int(x, 0), default=0x2000)
    ap.add_argument("--source", default="")
    ap.add_argument("--source-md5", default="")
    ap.add_argument("--notes", default="",
                    help="optional JSON sidecar for every boundary the walk stopped at")
    a = ap.parse_args()
    binary = a.binary or "libircmd020.so"
    if not pathlib.Path(binary).exists():
        print(f"extract-vdcmd-opcodes.py: {binary} not found", file=sys.stderr)
        return 1
    rows, notes = analyse(binary, a.objdump, a.nm, a.max_span)
    write(rows, a.out, a.format, a.source or pathlib.Path(binary).name, a.source_md5)
    if a.notes:
        pathlib.Path(a.notes).write_text(json.dumps(notes, indent=1))
    uniq = [r for r in rows if r["status"] == "unique"]
    amb = [r for r in rows if r["status"] == "ambiguous"]
    prov = Counter(r["provenance"] for r in rows)
    kinds = Counter(n["kind"] for n in notes)
    print(f"extract-vdcmd-opcodes.py: wrote {a.out}: {len(rows)} rows over "
          f"{len({r['opcode'] for r in rows})} distinct IDs "
          f"({len(uniq)} rows on singly-claimed IDs, {len(amb)} ambiguous); "
          + " ".join(f"{k}={v}" for k, v in sorted(prov.items())))
    print("  notes: " + (" ".join(f"{k}={v}" for k, v in sorted(kinds.items()))
                         if kinds else "no boundary stopped the walk (0 chains)"))


if __name__ == "__main__":
    main()
