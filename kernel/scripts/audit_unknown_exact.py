#!/usr/bin/env python3
import argparse
import csv
import re
import subprocess
from collections import defaultdict
from pathlib import Path

SOURCE_GLOBS = [
    "*.c", "*.h", "*.cc", "*.cpp", "*.S",
    "*.dts", "*.dtsi", "Makefile", "Kbuild", "*.bzl",
]

def split_semicolon(s):
    return [x for x in (s or "").split(";") if x]

def compat_from_alias(alias):
    # e.g. of:N*T*Cmediatek,mt6375-chgC*
    m = re.search(r"\*C(.+?)(?:C\*)?$", alias)
    return m.group(1) if m else None

def alias_payload(alias):
    for prefix in ("i2c:", "spi:", "platform:", "usb:", "pci:", "sdio:"):
        if alias.startswith(prefix):
            val = alias[len(prefix):]
            if len(val) >= 4:
                return val
    return None

def distinctive_chip_tokens(name):
    s = name.lower().replace("-", "_")
    out = set()

    # named silicon/component tokens: aw2013, sh366003, wl2868, vtdr6115, gen4m...
    for tok in re.findall(r"[a-z][a-z0-9]*\d[a-z0-9]*", s):
        if len(tok) >= 5:
            out.add(tok)

    # Preserve compound chipset driver tokens that are useful even when split.
    for tok in s.split("_"):
        if len(tok) >= 5 and re.search(r"[a-z]", tok) and re.search(r"\d", tok):
            out.add(tok)

    return sorted(out)

def evidence_strength(kinds):
    kinds = set(kinds)
    if "COMPATIBLE" in kinds:
        return "STRONG_HARDWARE_HIT"
    if "ALIAS" in kinds:
        return "STRONG_ALIAS_HIT"
    if "EXPORT" in kinds:
        return "STRONG_API_HIT"
    if "MODULE_NAME" in kinds or "CHIP_TOKEN" in kinds:
        return "RELATED_SOURCE_HIT"
    return "NO_EXACT_HIT"

def run_self_test():
    assert compat_from_alias("of:N*T*Cmediatek,mt6375-chgC*") == "mediatek,mt6375-chg"
    assert compat_from_alias("i2c:hyn_ts") is None
    assert alias_payload("i2c:hyn_ts") == "hyn_ts"
    assert alias_payload("platform:gpio-keys") == "gpio-keys"
    toks = distinctive_chip_tokens("panel_ky_vtdr6115_dphy_cmd")
    assert "vtdr6115" in toks
    toks = distinctive_chip_tokens("custom_ldo_wl2868")
    assert "wl2868" in toks
    assert evidence_strength(["EXPORT"]) == "STRONG_API_HIT"
    assert evidence_strength(["COMPATIBLE", "EXPORT"]) == "STRONG_HARDWARE_HIT"
    assert evidence_strength([]) == "NO_EXACT_HIT"
    print("self-test: PASS")

def rg_exact(root, terms, max_hits):
    if not terms:
        return []

    cmd = ["rg", "-n", "-F", "--no-heading", "--color", "never"]
    for g in SOURCE_GLOBS:
        cmd += ["-g", g]
    for term in terms:
        cmd += ["-e", term]
    cmd.append(str(root))

    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode not in (0, 1):
        raise RuntimeError(f"rg failed under {root}: {p.stderr.strip()}")

    rows = []
    for line in p.stdout.splitlines():
        if len(rows) >= max_hits:
            break
        # rg -n format: file:line:text
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        file_s, lineno, text = parts
        matched = [t for t in terms if t in text]
        rows.append((Path(file_s), lineno, text.strip(), matched))
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", type=Path)
    ap.add_argument("--nothing", type=Path)
    ap.add_argument("--max-hits", type=int, default=60)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        run_self_test()
        return

    if not args.research or not args.nothing:
        ap.error("--research and --nothing are required unless --self-test is used")

    research = args.research.resolve()
    nothing = args.nothing.resolve()
    kernel = research / "kernel"

    with (kernel / "stock-module-master.csv").open(newline="", encoding="utf-8") as f:
        master = list(csv.DictReader(f))

    exports = defaultdict(list)
    with (kernel / "stock-module-exports.tsv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            exports[r["sha256"]].append(r["symbol"])

    unknowns = [r for r in master if r["classification"] == "UNKNOWN"]

    roots = [
        ("kernel", nothing / "kernel"),
        ("device_modules", nothing / "device_modules"),
        ("kernel_modules", nothing / "kernel_modules"),
    ]
    for name, root in roots:
        if not root.is_dir():
            raise SystemExit(f"missing Nothing source root: {root}")

    # Build one path list for exact filename/path-token hits.
    all_files = []
    for root_name, root in roots:
        p = subprocess.run(
            ["rg", "--files", str(root)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if p.returncode != 0:
            raise RuntimeError(p.stderr.strip())
        for s in p.stdout.splitlines():
            all_files.append((root_name, Path(s)))

    evidence_rows = []
    summary_rows = []
    md = [
        "# UNKNOWN exact-source reconnaissance",
        "",
        f"- stock UNKNOWN binaries: {len(unknowns)}",
        "- method: exact module/chip/alias/compatible/export searches only",
        "- no fuzzy candidate ranking is used",
        "",
    ]

    for stock in unknowns:
        name = stock["module_name"]
        sha = stock["sha256"]

        term_kinds = defaultdict(set)

        # Exact module identifiers.
        for term in {name, name.replace("_", "-"), name.replace("-", "_")}:
            if len(term) >= 4:
                term_kinds[term].add("MODULE_NAME")

        # Exact modinfo aliases/OF compatibles.
        for alias in split_semicolon(stock.get("aliases")):
            comp = compat_from_alias(alias)
            if comp:
                term_kinds[comp].add("COMPATIBLE")
            payload = alias_payload(alias)
            if payload:
                term_kinds[payload].add("ALIAS")

        # Distinctive component/chip identifiers.
        for term in distinctive_chip_tokens(name):
            term_kinds[term].add("CHIP_TOKEN")

        # Exported API names are powerful for renamed source modules.
        for sym in exports.get(sha, []):
            if len(sym) >= 5:
                term_kinds[sym].add("EXPORT")

        terms = sorted(term_kinds)
        seen_kinds = set()
        local_rows = []

        # Text hits.
        for root_name, root in roots:
            for fpath, lineno, text, matched_terms in rg_exact(root, terms, args.max_hits):
                rel = fpath.relative_to(root).as_posix()
                for term in matched_terms:
                    kinds = sorted(term_kinds[term])
                    seen_kinds.update(kinds)
                    rec = {
                        "stock_sha256": sha,
                        "stock_module": name,
                        "evidence_kind": ";".join(kinds),
                        "term": term,
                        "nothing_root": root_name,
                        "path": rel,
                        "line": lineno,
                        "text": text[:500],
                    }
                    evidence_rows.append(rec)
                    local_rows.append(rec)

        # Filename/path hits for exact module/chip tokens.
        path_terms = [
            t for t, ks in term_kinds.items()
            if "MODULE_NAME" in ks or "CHIP_TOKEN" in ks
        ]
        for root_name, fpath in all_files:
            low = fpath.as_posix().lower()
            root = dict(roots)[root_name]
            for term in path_terms:
                if term.lower() in low:
                    kinds = sorted(term_kinds[term])
                    seen_kinds.update(kinds)
                    rec = {
                        "stock_sha256": sha,
                        "stock_module": name,
                        "evidence_kind": ";".join(kinds) + ";PATH",
                        "term": term,
                        "nothing_root": root_name,
                        "path": fpath.relative_to(root).as_posix(),
                        "line": "",
                        "text": "<path hit>",
                    }
                    evidence_rows.append(rec)
                    local_rows.append(rec)

        strength = evidence_strength(seen_kinds)
        summary_rows.append({
            "stock_sha256": sha,
            "stock_module": name,
            "locations": stock["locations"],
            "strength": strength,
            "evidence_kinds": ";".join(sorted(seen_kinds)),
            "exact_hit_count": len(local_rows),
            "aliases": stock.get("aliases", ""),
            "description": stock.get("description", ""),
        })

        md += [
            f"## {name}",
            "",
            f"- locations: `{stock['locations']}`",
            f"- result: **{strength}**",
            f"- evidence kinds: `{';'.join(sorted(seen_kinds))}`",
            f"- exact hit records: {len(local_rows)}",
            f"- description: `{stock.get('description','')}`",
            f"- aliases: `{stock.get('aliases','')}`",
            "",
        ]

        for rec in local_rows[:20]:
            md.append(
                f"- `{rec['evidence_kind']}` `{rec['term']}` → "
                f"`{rec['nothing_root']}:{rec['path']}"
                + (f":{rec['line']}" if rec["line"] else "")
            )
        if len(local_rows) > 20:
            md.append(f"- ... {len(local_rows) - 20} more exact-hit records in CSV")
        if not local_rows:
            md.append("- No exact source hit found.")
        md.append("")

    summary_fields = [
        "stock_sha256","stock_module","locations","strength",
        "evidence_kinds","exact_hit_count","aliases","description",
    ]
    with (kernel / "unknown-exact-summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_fields)
        w.writeheader()
        w.writerows(summary_rows)

    evidence_fields = [
        "stock_sha256","stock_module","evidence_kind","term",
        "nothing_root","path","line","text",
    ]
    with (kernel / "unknown-exact-evidence.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=evidence_fields)
        w.writeheader()
        w.writerows(evidence_rows)

    (kernel / "unknown-exact-audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"UNKNOWN modules: {len(summary_rows)}")
    print(f"exact evidence records: {len(evidence_rows)}")
    print()
    print("===== EXACT AUDIT SUMMARY =====")
    for r in summary_rows:
        print(
            f"{r['stock_module']:35s} "
            f"{r['strength']:22s} "
            f"hits={int(r['exact_hit_count']):3d} "
            f"kinds={r['evidence_kinds'] or '-'}"
        )

if __name__ == "__main__":
    main()
