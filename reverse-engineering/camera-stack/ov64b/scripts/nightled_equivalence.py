#!/usr/bin/env python3
"""Mechanical equivalence proof for the only differing function between the
shipped imgsensor.ko and the reconstruction: yft_ctrl_nightled_by_idx
(adaptor-ctrls.c; drives the night-vision LED for sensor idx 4 = OV64B).

1. Both versions are executed by a tiny AArch64 interpreter that covers exactly
   the instructions in this function, over every input combination:
   sensor idx in {4, 0, 1, 2, 3, 5}, state in {-1, 0, 1, 2}, and
   nightled_is_open in {0, 1}.  The observable trace is the sequence of calls
   with argument registers, plus the final nightled_is_open byte.
2. Every call site of the function in the shipped module is listed, together
   with the constant it puts in w1 (state).  The function's address is never
   taken (no relocation references it).
Verdict: traces are identical for every state the shipped callers can pass.

usage: nightled_equivalence.py <shipped.ko> <rebuilt.ko>
"""
import re
import subprocess
import sys

FN = "yft_ctrl_nightled_by_idx"


def disasm(path, sym=FN):
    out = subprocess.run(["llvm-objdump", "-d", "-r", "--no-show-raw-insn", f"--disassemble-symbols={sym}", path],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    ins, relocs = [], {}
    for line in out:
        m = re.match(r"\s+([0-9a-f]+):\s+(\S+)\s*(.*)$", line)
        if m and not m.group(2).startswith("R_AARCH64"):
            ins.append((int(m.group(1), 16), m.group(2), re.sub(r"\s*//.*", "", m.group(3)).strip()))
        m = re.match(r"\s+([0-9a-f]+):\s+(R_AARCH64_\w+)\s+(\S+)", line)
        if m:
            relocs[int(m.group(1), 16)] = (m.group(2), m.group(3))
    return ins, relocs


def run(ins, relocs, idx, state, led):
    pc = {a: i for i, (a, _, _) in enumerate(ins)}
    R = {f"x{i}": 0 for i in range(31)}
    R["x0"] = 0x1000      # ctx
    R["x1"] = state & 0xFFFFFFFF
    mem8 = {"nightled": led}
    mem = {(0x1000, 0x79A8): idx, (0x1000, 0x940): 0x2000, (0x2000, 0): 0x3000}
    flags = {"N": 0, "Z": 0, "C": 0, "V": 0}
    trace = []
    cur = ins[0][0]

    def reg(n):
        n = n.strip()
        if n in ("wzr", "xzr"):
            return 0
        v = R["x" + n[1:]]
        return v & 0xFFFFFFFF if n[0] == "w" else v

    def setr(n, v):
        R["x" + n.strip()[1:]] = v & (0xFFFFFFFF if n.strip()[0] == "w" else 0xFFFFFFFFFFFFFFFF)

    def imm(s):
        return int(s.strip().lstrip("#"), 0)

    def sub_flags(a, b):
        r = (a - b) & 0xFFFFFFFF
        flags["N"] = r >> 31
        flags["Z"] = int(r == 0)
        flags["C"] = int(a >= b)
        sa = a - (1 << 32) if a >> 31 else a
        sb = b - (1 << 32) if b >> 31 else b
        flags["V"] = int(not (-(1 << 31) <= sa - sb < (1 << 31)))

    def cond(c):
        return {"eq": flags["Z"] == 1, "ne": flags["Z"] == 0, "hs": flags["C"] == 1, "lo": flags["C"] == 0,
                "hi": flags["C"] == 1 and flags["Z"] == 0, "ls": not (flags["C"] == 1 and flags["Z"] == 0)}[c]

    steps = 0
    while True:
        steps += 1
        assert steps < 200
        a, op, args = ins[pc[cur]]
        nxt = ins[pc[cur] + 1][0] if pc[cur] + 1 < len(ins) else None
        A = [x.strip() for x in re.split(r",(?![^\[]*\])", args)] if args else []
        if op in ("paciasp", "autiasp", "stp", "str", "ldp", "nop") or (op == "ldr" and "[sp" in args) \
                or (op == "mov" and "sp" in A):
            pass
        elif op == "ret":
            return trace, mem8["nightled"]
        elif op == "mov":
            setr(A[0], imm(A[1]) if A[1].startswith("#") else reg(A[1]))
        elif op == "ldr":
            m = re.match(r"\[(x\d+), (x\d+)\]", A[1]) or re.match(r"\[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]", A[1])
            base = R[m.group(1)]
            off = R[m.group(2)] if m.group(2) and m.group(2).startswith("x") else int(m.group(2) or "0", 0)
            setr(A[0], mem.get((base, off), 0))
        elif op == "ldrb":
            setr(A[0], mem8["nightled"])
            assert relocs.get(a, ("", ""))[1] == ".bss+0x20"
        elif op == "strb":
            mem8["nightled"] = reg(A[0]) & 0xFF
            assert relocs.get(a, ("", ""))[1] == ".bss+0x20"
        elif op in ("adrp", "add"):
            setr(A[0], 0)
        elif op == "cmp":
            sub_flags(reg(A[0]), imm(A[1]) if A[1].startswith("#") else reg(A[1]))
        elif op == "ccmp":
            if cond(A[3]):
                sub_flags(reg(A[0]), imm(A[1]) if A[1].startswith("#") else reg(A[1]))
            else:
                nz = imm(A[2])
                flags.update(N=(nz >> 3) & 1, Z=(nz >> 2) & 1, C=(nz >> 1) & 1, V=nz & 1)
        elif op == "cset":
            setr(A[0], int(cond(A[1])))
        elif op == "eor":
            setr(A[0], reg(A[1]) ^ imm(A[2]))
        elif op.startswith("b.") or op == "b":
            tgt = int(A[-1].split()[0], 16)
            if op == "b" or cond(op[2:]):
                cur = tgt
                continue
        elif op in ("cbz", "cbnz"):
            if (reg(A[0]) == 0) == (op == "cbz"):
                cur = int(A[1].split()[0], 16)
                continue
        elif op in ("tbz", "tbnz"):
            bit = (reg(A[0]) >> imm(A[1])) & 1
            if (bit == 0) == (op == "tbz"):
                cur = int(A[2].split()[0], 16)
                continue
        elif op == "bl":
            callee = relocs.get(a, ("", "?"))[1]
            trace.append((callee, reg("w0") if callee != "_printk" else None,
                          reg("w4") if callee == "_printk" else None))
        else:
            raise SystemExit(f"unhandled {op} {args} @{a:#x}")
        cur = nxt


def call_sites(path):
    out = subprocess.run(["llvm-objdump", "-d", "-r", "--no-show-raw-insn", path],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    sites, fn, refs = [], None, 0
    for i, line in enumerate(out):
        m = re.match(r"^[0-9a-f]+ <(\w+)>:", line)
        if m:
            fn = m.group(1)
        if re.search(rf"\sbl?\s+0x[0-9a-f]+ <{FN}>$", line):
            w1 = "?"
            for x in reversed(out[max(0, i - 8):i]):
                mm = re.search(r"\smov\s+w1, (#0x[0-9a-f]+|#\d+|wzr)", x)
                if mm:
                    w1 = 0 if mm.group(1) == "wzr" else int(mm.group(1)[1:], 0)
                    break
                if re.search(r"\s(?:mov|ldr|add|orr|cset)\s+w1,", x):
                    break
            sites.append((fn, line.split(":")[0].strip(), w1))
        if FN in line and "R_AARCH64" in line:
            refs += 1
    return sites, refs


def main():
    shipped, rebuilt = sys.argv[1], sys.argv[2]
    SI, SR = disasm(shipped)
    BI, BR = disasm(rebuilt)
    sites, refs = call_sites(shipped)
    print("call sites in shipped module:")
    for s in sites:
        print(f"  {s[0]} @{s[1]}: state(w1) = {s[2]}")
    print(f"relocations naming {FN}: {refs} (address never taken)" if refs == 0 else f"RELOC REFS: {refs}")
    reachable = sorted({s[2] for s in sites})
    ok = True
    print("\nidx state led | shipped trace / led' || rebuilt trace / led' | equal")
    for idx in (4, 0, 1, 2, 3, 5):
        for state in (-1, 0, 1, 2):
            for led in (0, 1):
                ts, ls = run(SI, SR, idx, state, led)
                tb, lb = run(BI, BR, idx, state, led)
                eq = (ts, ls) == (tb, lb)
                if state in reachable and not eq:
                    ok = False
                if idx == 4 or not eq:
                    print(f"  {idx}  {state:>3}   {led} | {ts} / {ls} || {tb} / {lb} | "
                          f"{'yes' if eq else 'NO'}{'' if state in reachable else ' (state not passed by any caller)'}")
    print("\nVERDICT:", "EQUIVALENT for every state passed by the shipped callers " + str(reachable)
          if ok and refs == 0 and all(isinstance(s[2], int) for s in sites) else "NOT PROVEN")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
