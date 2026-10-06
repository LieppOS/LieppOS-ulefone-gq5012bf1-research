#!/usr/bin/env python3
"""Axis 1 evidence harvest: every per-component kernel-module inventory record.

A "claim" is one row of one inventory table inside a RE component (workspace
pack or research-repo domain scope) that names a shipped kernel module.  Nothing
is inferred here: this script only copies what a component already asserts, so
that build-kernel-modules.py can resolve ownership mechanically and every
classification can be traced back to the file that asserts it.

tiers
  inventory  column-1/module column of a TSV/CSV table inside a workspace pack
             (Reverse Engineer - {DONE,PARTIAL,BLOCKED,TODO}/<COMP>/...)
  research   same, for a research-repo domain scope (reverse-engineering/<scope>/)
  bootmap    reverse-engineering/boot/module-loading/module-classification.tsv
             (load-phase classification for the whole shipped universe)
  oemmap     Reverse Engineer - PARTIAL/OEM-KERNEL-MODULES/evidence/module-map.csv
             (per-module source-provenance classification for the universe)

Output: audit-evidence/harvested-pack-module-claims.tsv
"""
import collections
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.abspath(os.path.join(HERE, ".."))
WS = os.environ.get("RE_WORKSPACE", os.path.abspath(os.path.join(CA, "..", "..", "..")))
RE_ROOT = os.path.join(WS, "ulefone-gq5012bf1-research/reverse-engineering")
OUT = os.path.join(CA, "audit-evidence", "harvested-pack-module-claims.tsv")
STATUSES = ["DONE", "PARTIAL", "BLOCKED", "TODO"]
EXTRAS = ("partition", "role", "runtime", "class", "status", "board", "location",
          "source", "donor", "evidence", "compat", "phase", "loaded_in_capture")

MODULE_COLS = ("module", "module_name", "filename", "ko", "component", "name")

UMBRELLA = {
    "MTK-MODULE-LOADER", "VENDOR-DLKM", "SYSTEM-DLKM", "GKI-KMI-BASELINE",
    "OEM-KERNEL-MODULES", "INIT-INSMOD", "VENDOR-ALL-MODULES-READY",
    "FIRMWARE-INVENTORY", "DTB-DTBO", "BOOT-IMAGES",
}


def stem(name: str) -> str:
    name = name.strip().strip('"').split("/")[-1]
    return name[:-3] if name.endswith(".ko") else name


def harvest(root: str, scope_fn, tiers: tuple):
    acc = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith((".tsv", ".csv")):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, newline="", encoding="utf8", errors="ignore") as fh:
                    rdr = csv.reader(fh, delimiter="\t" if fn.endswith(".tsv") else ",")
                    try:
                        header = next(rdr)
                    except StopIteration:
                        continue
                    if not header:
                        continue
                    cols = [c.strip().lower() for c in header]
                    mcol = next((i for i, c in enumerate(cols)
                                 if any(k in c for k in MODULE_COLS)), None)
                    if mcol is None:
                        continue
                    keep = [i for i, c in enumerate(cols)
                            if any(k in c for k in EXTRAS) and i != mcol][:3]
                    scope, tier = scope_fn(dirpath, fn)
                    for line in rdr:
                        if len(line) <= mcol:
                            continue
                        s = stem(line[mcol])
                        if not s:
                            continue
                        extras = " | ".join(f"{cols[i]}={line[i].strip()[:90]}"
                                           for i in keep if i < len(line))
                        acc.append((scope, tier, s, os.path.relpath(path, WS), extras))
            except Exception:
                continue
    return acc


def mentions(root: str, scope_fn, stems, tiers=("mention",)):
    """Prose evidence that a component owns a module: the pack's own README or
    notes/*.md names `<stem>.ko` (or `<stem>.c`, or a backticked bare stem).
    evidence/, source/ and binary-analysis/ are deliberately excluded: those
    directories hold cross-module dumps that name every module on the device and
    therefore say nothing about ownership.  The matching line is kept so the claim
    stays checkable."""
    import re
    acc = []
    per = {}
    for dirpath, _dirs, files in os.walk(root):
        rel0 = os.path.relpath(dirpath, root).split(os.sep)[0]
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            if not (fn == "README.md" or rel0 == "notes"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                text = open(path, encoding="utf8", errors="ignore").read()
            except Exception:
                continue
            if ".ko" not in text and not any(s in text for s in ("source", "driver")):
                continue
            scope, tier = scope_fn(dirpath, fn)
            pats = {s: re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(s) + r"(?![A-Za-z0-9_-])")
                    for s in stems}
            for line in text.splitlines():
                for s, pat in pats.items():
                    if not pat.search(line):
                        continue
                    # short/word-like stems are only accepted in their explicit
                    # driver form, otherwise ordinary English prose matches them
                    permissive = len(s) >= 6 or any(ch.isdigit() for ch in s)
                    if not permissive and f"{s}.ko" not in line and f"`{s}`" not in line:
                        continue
                    key = (scope, tier, s, os.path.relpath(path, WS))
                    if per.get(key, 0) >= 2:
                        continue
                    per[key] = per.get(key, 0) + 1
                    acc.append((scope, tier, s, os.path.relpath(path, WS),
                                f"line={line.strip()[:110]}"))
    return acc


def source_owned(root: str, scope_fn, stems):
    """Strongest prose-free signal: the component directory literally carries the
    module's own file (`<stem>.c`, `<stem>.h`, `<stem>.ko`)."""
    acc = []
    want = {}
    for s in stems:
        for ext in (".c", ".h", ".ko"):
            want[f"{s}{ext}".replace("-", "_")] = s
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            s = want.get(fn.replace("-", "_"))
            if s:
                acc.append((*scope_fn(dirpath, fn), s,
                            os.path.relpath(os.path.join(dirpath, fn), WS), "own-file"))
    return acc


def main() -> None:
    rows = []
    for status in STATUSES:
        root = os.path.join(WS, f"Reverse Engineer - {status}")
        if os.path.isdir(root):
            rows += harvest(
                root,
                lambda d, f: (os.path.relpath(d, root).split(os.sep)[0], "inventory"),
                ("inventory",))

    scopes = {
        "audio": "audio", "camera/eeprom": "camera/eeprom", "camera/vcm": "camera/vcm",
        "connectivity": "connectivity", "display-input": "display-input",
        "display-input/rear-display-input": "display-input/rear",
        "geniezone/transport": "geniezone", "modem": "modem", "nfc": "nfc",
        "power/rt5133": "power/rt5133", "sensors": "sensors", "storage": "storage",
        "thermal-camera/fm78100": "thermal-camera", "tinysys": "tinysys",
        "usb": "usb",
    }
    for sub, label in scopes.items():
        root = os.path.join(RE_ROOT, sub)
        if os.path.isdir(root):
            rows += harvest(root, lambda d, f, l=label: (f"research:{l}", "research"),
                            ("research",))
    boot = os.path.join(RE_ROOT, "boot", "module-loading")
    if os.path.isdir(boot):
        rows += harvest(boot, lambda d, f: ("research:boot-module-loading", "bootmap"),
                        ("bootmap",))
    oem = os.path.join(WS, "Reverse Engineer - PARTIAL/OEM-KERNEL-MODULES/evidence")
    if os.path.isdir(oem):
        rows += harvest(oem, lambda d, f: ("OEM-KERNEL-MODULES", "oemmap"), ("oemmap",))

    # mention tier: only needed to corroborate module names that no inventory row
    # claims, so restrict it to that residual set
    universe = {r[2] for r in rows if r[1] == "oemmap"}
    claimed = {r[2] for r in rows if r[1] == "inventory" and r[0] not in UMBRELLA}
    residual = sorted(universe - claimed)
    for status in STATUSES:
        root = os.path.join(WS, f"Reverse Engineer - {status}")
        if os.path.isdir(root):
            rows += mentions(root, lambda d, f: (os.path.relpath(d, root).split(os.sep)[0],
                                                "mention"), residual)
    for status in STATUSES:
        root = os.path.join(WS, f"Reverse Engineer - {status}")
        if os.path.isdir(root):
            rows += source_owned(root, lambda d, f: (os.path.relpath(d, root).split(os.sep)[0],
                                                    "ownsource"), residual)
    for sub, label in scopes.items():
        root = os.path.join(RE_ROOT, sub)
        if os.path.isdir(root):
            rows += mentions(root, lambda d, f, l=label: (f"research:{l}", "research"),
                             residual)

    fields = ["component", "status", "tier", "module", "source_file", "extras"]
    seen, out = set(), []
    status_of = {}
    for st in STATUSES:
        d = os.path.join(WS, f"Reverse Engineer - {st}")
        if os.path.isdir(d):
            for c in os.listdir(d):
                if os.path.isdir(os.path.join(d, c)):
                    status_of[c] = st
    for comp, tier, module, src, extras in rows:
        key = (comp, tier, module, src, extras)
        if key in seen:
            continue
        seen.add(key)
        out.append({"component": comp, "status": status_of.get(comp, "research"),
                    "tier": tier, "module": module, "source_file": src, "extras": extras})
    out.sort(key=lambda r: (r["module"], r["tier"], r["component"]))
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    mods = {r["module"] for r in out}
    print(f"claims={len(out)} claim-bearing-scopes={len({r['component'] for r in out})} "
          f"modules={len(mods)}")
    bytier = collections.Counter(r["tier"] for r in out)
    print("  by tier:", dict(bytier))
    strong = {r["module"] for r in out
              if r["component"] not in UMBRELLA and not r["component"].startswith("research:")
              and r["tier"] == "inventory"}
    print(f"  modules with a workspace-pack claim={len(strong)}")


if __name__ == "__main__":
    main()
