#!/usr/bin/env python3
"""Recover inline (code-embedded) sensor register writes from a stock module.

Legacy-style MTK sub-drivers (s5kjn1*, s5kgn1sp, s5kgm2sp, ov32b40 ...) do not
keep their init sequence in a u16 table; they emit one
adaptor_i2c_wr_u16(client, addr8, reg, val) / wr_u8 call per register with
immediates.  This does a linear, constant-propagating scan of llvm-objdump
output for one function and prints every (reg, value) pair and every
__const_udelay/msleep/usleep_range, in program order.

Usage: inline_writes.py <module.ko> <func_start_hex> <func_end_hex> [label]
Limitations (documented in output): linear scan, so writes inside
conditional blocks are emitted with their address and a '?' marker when the
scan crossed a conditional branch target region; values loaded from memory
are printed as '<mem>'.
"""
from __future__ import annotations

import re
import subprocess
import sys

WR = {"adaptor_i2c_wr_u16": "u16", "adaptor_i2c_wr_u8": "u8", "adaptor_i2c_wr_u8_u8": "u8u8",
      "subdrv_i2c_wr_u16": "u16", "subdrv_i2c_wr_u8": "u8", "adaptor_i2c_wr_p16": "p16",
      "adaptor_i2c_wr_regs_u16": "regs16", "adaptor_i2c_wr_seq_p8": "seq_p8"}
DLY = {"__const_udelay", "msleep", "usleep_range_state", "usleep_range", "__udelay", "mdelay"}

ins_re = re.compile(r"^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$")
rel_re = re.compile(r"^\s*([0-9a-f]+):\s+R_AARCH64_(\S+)\s+(\S+)")


def imm(s):
    s = s.strip().lstrip("#")
    return int(s, 0)


def main():
    ko, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
    label = sys.argv[4] if len(sys.argv) > 4 else ""
    out = subprocess.run(["llvm-objdump", "-dr", "--no-show-raw-insn", f"--start-address=0x{int(a,16):x}",
                          f"--stop-address=0x{int(b,16):x}", ko], capture_output=True, text=True).stdout
    regs: dict[str, int | None] = {}
    pending = None
    rows = []
    branch_targets = set()
    lines = out.splitlines()
    for ln in lines:
        m = ins_re.match(ln)
        if m and (m.group(2).startswith(("b.", "cbz", "cbnz", "tbz", "tbnz")) or m.group(2) == "b"):
            t = re.search(r"0x([0-9a-f]+)", m.group(3))
            if t:
                branch_targets.add(int(t.group(1), 16))
    for ln in lines:
        r = rel_re.match(ln)
        if r and r.group(2) == "CALL26":
            fn = r.group(3)
            addr = int(r.group(1), 16)
            if fn in WR:
                rows.append((addr, WR[fn], regs.get("w2"), regs.get("w3"), regs.get("w1")))
            elif fn in DLY:
                rows.append((addr, "delay:" + fn, regs.get("w0"), regs.get("w1"), None))
            for k in ("w0", "w1", "w2", "w3", "w4", "x0", "x1", "x2", "x3"):
                regs.pop(k, None)
            continue
        m = ins_re.match(ln)
        if not m:
            continue
        op, args = m.group(2), m.group(3).split("//")[0]
        parts = [p.strip() for p in args.split(",")]
        try:
            if op == "mov" and len(parts) == 2:
                d, s = parts
                d = "w" + d[1:]
                if s in ("wzr", "xzr"):
                    regs[d] = 0
                elif s.startswith("#"):
                    regs[d] = imm(s) & 0xFFFFFFFF
                elif s[0] in "wx":
                    regs[d] = regs.get("w" + s[1:])
                else:
                    regs[d] = None
            elif op == "movk" and len(parts) >= 2:
                d = "w" + parts[0][1:]
                v = imm(parts[1])
                sh = int(parts[2].split()[-1].lstrip("#")) if len(parts) > 2 else 0
                if regs.get(d) is not None:
                    regs[d] = (regs[d] & ~(0xFFFF << sh) | (v << sh)) & 0xFFFFFFFF
            elif op == "orr" and len(parts) == 3 and parts[1] in ("wzr", "xzr") and parts[2].startswith("#"):
                regs["w" + parts[0][1:]] = imm(parts[2]) & 0xFFFFFFFF
            elif op in ("ldr", "ldrb", "ldrh", "ldp", "add", "sub", "lsr", "lsl", "and", "orr", "eor", "csel",
                        "ubfx", "sxtw", "uxtb", "uxth", "madd", "mul", "neg", "ldur", "ldrsw", "adrp", "cset"):
                if parts and parts[0][:1] in "wx":
                    regs["w" + parts[0][1:]] = None
                if op == "ldp" and len(parts) > 1 and parts[1][:1] in "wx":
                    regs["w" + parts[1][1:]] = None
        except (ValueError, IndexError):
            if parts and parts[0][:1] in "wx":
                regs["w" + parts[0][1:]] = None
    print(f"# inline register writes: {label} {ko.split('/')[-1]} [{a},{b})")
    print("addr\tkind\treg\tvalue\tnote")
    for addr, kind, x, y, z in rows:
        note = "branch-target-region" if addr in branch_targets else ""
        if kind.startswith("delay"):
            us = (x / 4295.0) if (kind.endswith("__const_udelay") and x is not None) else x
            print(f"0x{addr:x}\t{kind}\t\t{'%.0fus' % us if isinstance(us, float) else us}\t{note}")
        else:
            print(f"0x{addr:x}\t{kind}\t{'<mem>' if x is None else '0x%04x' % x}\t"
                  f"{'<mem>' if y is None else '0x%04x' % y}\t{note}")


if __name__ == "__main__":
    main()
