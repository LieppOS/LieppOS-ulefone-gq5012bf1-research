#!/usr/bin/env python3
"""Locate / extract / replace one C function definition by name.

A definition is found as: a line starting (column 0) with a declaration whose
identifier before '(' is <name>, followed by a body '{' ... matching '}' at
column 0.  Good enough for kernel-style sources (one function per top-level).

usage:
  cfunc.py get  <file.c> <name>                 print definition
  cfunc.py put  <dst.c> <name> <src.c> [srcname] replace dst definition with src's
  cfunc.py where <file.c> <name>                print start/end line numbers
"""
import re
import sys


def find(src, name):
    pat = re.compile(r"^(?:[A-Za-z_][\w \t\*]*?[\s\*])?" + re.escape(name) + r"\s*\(", re.M)
    for m in pat.finditer(src):
        start = m.start()
        # skip prototypes: next of ';' / '{' after the param list
        depth = 0
        i = m.end() - 1
        while i < len(src):
            c = src[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        j = i + 1
        while j < len(src) and src[j] in " \t\n":
            j += 1
        if j >= len(src) or src[j] != "{":
            continue
        # include a preceding 'static'/type line(s) already on match line; find body end
        end = src.find("\n}\n", j)
        if end < 0:
            end = len(src) - 2
        return start, end + 3
    return None


def main():
    op = sys.argv[1]
    if op == "get":
        s = open(sys.argv[2]).read()
        r = find(s, sys.argv[3])
        if not r:
            sys.exit(f"{sys.argv[3]}: not found")
        sys.stdout.write(s[r[0]:r[1]])
    elif op == "where":
        s = open(sys.argv[2]).read()
        r = find(s, sys.argv[3])
        if not r:
            sys.exit(1)
        print(s.count("\n", 0, r[0]) + 1, s.count("\n", 0, r[1]))
    elif op == "put":
        dst, name, srcf = sys.argv[2], sys.argv[3], sys.argv[4]
        sname = sys.argv[5] if len(sys.argv) > 5 else name
        d = open(dst).read()
        s = open(srcf).read()
        rd, rs = find(d, name), find(s, sname)
        if not rd or not rs:
            sys.exit(f"not found: dst={bool(rd)} src={bool(rs)}")
        d = d[:rd[0]] + s[rs[0]:rs[1]] + d[rd[1]:]
        open(dst, "w").write(d)
        print(f"{name}: replaced ({rd[1]-rd[0]} -> {rs[1]-rs[0]} bytes)")


if __name__ == "__main__":
    main()
