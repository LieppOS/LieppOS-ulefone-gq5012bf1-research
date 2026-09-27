#!/usr/bin/env python3
import hashlib
import os
import stat
import sys
from pathlib import Path

if len(sys.argv) != 4:
    raise SystemExit(f"usage: {sys.argv[0]} OLD_ROOT NEW_ROOT REPORT_DIR")
old_root, new_root, report_dir = map(Path, sys.argv[1:])
report_dir.mkdir(parents=True, exist_ok=True)

def inventory(root):
    paths = {"."}
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs.sort(); files.sort()
        relbase = Path(base).relative_to(root)
        for name in dirs + files:
            paths.add((relbase / name).as_posix())
    return paths

def at(root, rel):
    return root if rel == "." else root / rel

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def attrs(path):
    values = {}
    for name in sorted(os.listxattr(path, follow_symlinks=False)):
        values[name] = os.getxattr(path, name, follow_symlinks=False).hex()
    return values

old_paths, new_paths = inventory(old_root), inventory(new_root)
added, removed = sorted(new_paths-old_paths), sorted(old_paths-new_paths)
common = sorted(old_paths & new_paths)
results = {name: [] for name in [
    "content", "type", "mode", "owner", "mtime", "nlink", "rdev",
    "regular-size", "directory-size", "xattr", "symlink"
]}
regular_count = 0
for rel in common:
    op, np = at(old_root, rel), at(new_root, rel)
    os_, ns = os.lstat(op), os.lstat(np)
    ot, nt = stat.S_IFMT(os_.st_mode), stat.S_IFMT(ns.st_mode)
    if ot != nt:
        results["type"].append(f"{rel}|{ot:o}|{nt:o}")
        continue
    if stat.S_IMODE(os_.st_mode) != stat.S_IMODE(ns.st_mode):
        results["mode"].append(f"{rel}|{stat.S_IMODE(os_.st_mode):04o}|{stat.S_IMODE(ns.st_mode):04o}")
    if (os_.st_uid, os_.st_gid) != (ns.st_uid, ns.st_gid):
        results["owner"].append(f"{rel}|{os_.st_uid}:{os_.st_gid}|{ns.st_uid}:{ns.st_gid}")
    if os_.st_mtime_ns != ns.st_mtime_ns:
        results["mtime"].append(f"{rel}|{os_.st_mtime_ns}|{ns.st_mtime_ns}")
    if os_.st_nlink != ns.st_nlink:
        results["nlink"].append(f"{rel}|{os_.st_nlink}|{ns.st_nlink}")
    if os_.st_rdev != ns.st_rdev:
        results["rdev"].append(f"{rel}|{os_.st_rdev}|{ns.st_rdev}")
    if attrs(op) != attrs(np):
        results["xattr"].append(f"{rel}|OLD={attrs(op)}|NEW={attrs(np)}")
    if stat.S_ISREG(ot):
        regular_count += 1
        if os_.st_size != ns.st_size:
            results["regular-size"].append(f"{rel}|{os_.st_size}|{ns.st_size}")
        oh, nh = digest(op), digest(np)
        if oh != nh:
            results["content"].append(f"{rel}|{oh}|{nh}")
    elif stat.S_ISDIR(ot) and os_.st_size != ns.st_size:
        results["directory-size"].append(f"{rel}|{os_.st_size}|{ns.st_size}")
    elif stat.S_ISLNK(ot):
        ol, nl = os.readlink(op), os.readlink(np)
        if ol != nl:
            results["symlink"].append(f"{rel}|{ol}|{nl}")

(report_dir/"paths-added.txt").write_text("\n".join(added)+(bool(added)*"\n"))
(report_dir/"paths-removed.txt").write_text("\n".join(removed)+(bool(removed)*"\n"))
for name, rows in results.items():
    (report_dir/f"{name}-differences.txt").write_text("\n".join(rows)+(bool(rows)*"\n"))
summary = [
    f"OLD_PATH_COUNT={len(old_paths)}", f"NEW_PATH_COUNT={len(new_paths)}",
    f"COMMON_PATH_COUNT={len(common)}", f"COMMON_REGULAR_FILE_COUNT={regular_count}",
    f"ADDED_COUNT={len(added)}", f"REMOVED_COUNT={len(removed)}",
] + [f"{name.upper().replace('-', '_')}_DIFF_COUNT={len(rows)}" for name, rows in results.items()]
(report_dir/"summary.txt").write_text("\n".join(summary)+"\n")
print("\n".join(summary))
print("REMOVED="+(";".join(removed) if removed else "<none>"))
print("ADDED="+(";".join(added) if added else "<none>"))
for name, rows in results.items():
    if rows:
        print(f"{name.upper()}="+";".join(rows))
