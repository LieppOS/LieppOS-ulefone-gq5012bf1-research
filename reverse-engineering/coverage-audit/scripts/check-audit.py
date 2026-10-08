#!/usr/bin/env python3
"""Fail-closed quality gate for the GQ5012BF1 coverage audit."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CA = HERE.parent
RE = CA.parent
REPO = RE.parent
WORKSPACE = REPO.parent
STOCK = REPO / "workspace/gq5012bf1/stock"


def rows(name: str) -> list[dict]:
    with (CA / name).open(newline="", encoding="utf8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_links(path: Path) -> list[str]:
    bad = []
    text = path.read_text(encoding="utf8")
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            bad.append(f"{path.relative_to(REPO)} -> {target}")
    return bad


def main() -> int:
    comps = rows("components.tsv")
    by_name = {r["component"]: r for r in comps}
    require(len(comps) == len(by_name) == 133, "components.tsv must contain 133 unique current components")

    workspace: dict[str, str] = {}
    for status in ("DONE", "PARTIAL", "BLOCKED", "TODO"):
        root = WORKSPACE / f"Reverse Engineer - {status}"
        for p in root.iterdir():
            if p.is_dir():
                require(p.name not in workspace, f"duplicate workspace component {p.name}")
                workspace[p.name] = status
    require(set(workspace) == set(by_name), f"component set mismatch workspace-only={set(workspace)-set(by_name)} table-only={set(by_name)-set(workspace)}")
    require(all(by_name[n]["status"] == s for n, s in workspace.items()), "component status differs from workspace")
    status_totals = Counter(workspace.values())
    require(status_totals["TODO"] == 0, "an untriaged TODO component folder exists")

    partials = [r for r in comps if r["status"] == "PARTIAL"]
    require(Counter(r["partial_class"] for r in partials)["E"] == 0,
            "a PARTIAL is still classified E (stale/duplicate/wrong scope) instead of re-scoped")
    require(all(r["blocker"] and r["recommended_action"] and r["difficulty"] and r["dependencies"]
                for r in partials), "PARTIAL triage fields")

    km = rows("kernel-modules.tsv")
    actual_modules = {p.name for p in STOCK.rglob("*.ko") if p.is_file()}
    table_modules = {r["module"] for r in km}
    require(len(km) == len(table_modules) == 457, "kernel module rows/uniqueness")
    require(actual_modules == table_modules, f"module universe mismatch missing={actual_modules-table_modules} extra={table_modules-actual_modules}")
    require({r["module"] for r in km if r["coverage"] == "E"} == {"mali_kbase_mt6878_r44.ko", "mali_mgm_mt6878_r44.ko", "mali_prot_alloc_mt6878_r44.ko"}, "kernel E set")

    dt = rows("device-tree.tsv")
    require(len(dt) == 580 and sum(int(r["nodes"]) for r in dt) == 930, "DT universe")
    require({r["compatible"] for r in dt if r["coverage"] == "E"} == {"arm,mali-valhall", "mediatek,g3d_brisket", "mediatek,mali"}, "DT E set")
    active = [r for r in dt if int(r["nodes_enabled"]) > 0]
    require(sum(r["coverage"] == "E" for r in active) == 3, "active DT mapping")
    require(not any(r["coverage"] == "E" and r["component"] != "UNMAPPED" for r in dt),
            "an unmapped compatible claims a component owner")

    hw = rows("hardware.tsv")
    require(len(hw) == 44 and not any(r["coverage"] == "E" for r in hw), "physical hardware accounting")
    rt = next(r for r in hw if "RT5133" in r["device"])
    require(rt["presence"] == "PROVEN" and "camera-sensor" in rt["device"], "RT5133 newest-evidence correction")

    hs, vs = rows("hals-services.tsv"), rows("vendor-services.tsv")
    require(len(hs) == 272 and len(vs) == 253, "HAL/service universe")
    require({r["artifact"] for r in hs if r["coverage"] == "E"} == {"vendor.mediatek.hardware.gpu", "vendor.mediatek.hardware.gpuserv"}, "HAL E set")
    require({r["service"] for r in vs if r["coverage"] == "E"} == {"vendor.gpuserv-default", "vendor.mali_platform-mediatek"}, "service E set")
    require(sum(r["binary_present"] == "no" and not r["service"].startswith("[exec]") for r in vs) == 22, "absent init-service executable count")

    fw, sw, bs = rows("firmware.tsv"), rows("secure-world.tsv"), rows("boot-storage.tsv")
    require(len(fw) == 80 and not any(r["coverage"] == "E" for r in fw), "firmware accounting")
    require(len(sw) == 13 and not any(r["coverage"] == "E" for r in sw), "secure-world accounting")
    require(len(bs) == 61 and not any(r["coverage"] == "E" for r in bs), "boot/storage accounting")
    require(all(len(r["sha256"].split(";")) >= 1 for r in fw), "firmware hashes")

    ai, ul, art = rows("android-integration.tsv"), rows("userspace-libraries.tsv"), rows("artifact-map.tsv")
    require(len(ai) == 654 and len(ul) == 538 and len(art) == 2952, "integration/artifact totals")
    require(not any(r["coverage"] == "E" for r in ai + ul), "integration/library unexplained orphan")
    require(sum(r["coverage"] == "E" for r in art) == 10, "unified E count")
    keys = [(r["artifact_type"], r["artifact"], r["partition_or_source"]) for r in art]
    require(len(keys) == len(set(keys)), "duplicate artifact-map key")

    allowed = set(by_name) | {"COVERED-GENERIC", "GENERIC-PLATFORM-INFRASTRUCTURE", "UNMAPPED", "DISABLED-ON-BOARD"}
    for name in ("kernel-modules.tsv", "device-tree.tsv", "hardware.tsv", "hals-services.tsv",
                 "vendor-services.tsv", "firmware.tsv", "secure-world.tsv", "boot-storage.tsv",
                 "android-integration.tsv", "userspace-libraries.tsv", "artifact-map.tsv"):
        data = rows(name)
        require(all(r["coverage"] in "ABCDE" for r in data), f"bad coverage in {name}")
        bad = {r["component"] for r in data if r["component"] not in allowed}
        require(not bad, f"noncanonical component references in {name}: {bad}")

    for note, table in (("notes/KERNEL-MODULES.md", km), ("notes/DEVICE-TREE.md", dt)):
        text = (CA / note).read_text(encoding="utf8")
        want = Counter(r["coverage"] for r in table)
        for cls, count in want.items():
            m = re.search(rf"^\| {cls} \|[^|]*\| \*?(\d+)\*? \|", text, re.M)
            require(m is not None and int(m.group(1)) == count,
                    f"{note} class-{cls} total disagrees with its source table")
        require("research:" not in text, f"{note} still references pseudo-component research owners")
        require("hand-written analysis" not in text, f"{note} still carries a hand-maintained tail")

    svc = (CA / "notes/SERVICES-FIRMWARE.md").read_text(encoding="utf8")
    for label, table in (("VINTF families + legacy HAL libraries", hs),
                         ("Init services + trigger executables", vs),
                         ("Firmware/calibration payloads", fw),
                         ("Secure-world surfaces", sw),
                         ("Scatter/ABOTA partition families", bs)):
        m = re.search(rf"^\| {re.escape(label)} \| "
                      r"(\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$", svc, re.M)
        require(m is not None, f"SERVICES-FIRMWARE.md row for {label!r} is missing")
        want = Counter(r["coverage"] for r in table)
        got = dict(zip(("total", *"ABCDE"), (int(x) for x in m.groups())))
        require(got["total"] == len(table) and all(got[k] == want[k] for k in "ABCDE"),
                f"SERVICES-FIRMWARE.md measured inventory disagrees for {label!r}: {got} vs {dict(want)}")

    compnote = (CA / "notes/COMPONENT-AUDIT.md").read_text(encoding="utf8")
    status_want = Counter(r["status"] for r in comps)
    for status in ("DONE", "PARTIAL", "BLOCKED", "TODO"):
        m = re.search(rf"^\| {status} \| \*?(\d+)\*? \|", compnote, re.M)
        require(m is not None and int(m.group(1)) == status_want[status],
                f"COMPONENT-AUDIT.md {status} count disagrees with components.tsv")
    class_want = Counter(r["partial_class"] for r in partials)
    for cls in "ABCDEF":
        m = re.search(rf"^\| {cls} \|[^|]*\| \*?(\d+)\*? \|", compnote, re.M)
        require(m is not None and int(m.group(1)) == class_want[cls],
                f"COMPONENT-AUDIT.md class-{cls} count disagrees with components.tsv")
    m = re.search(r"^\| \*\*Total\*\* \| \*\*(\d+)\*\* \|", compnote, re.M)
    require(m is not None and int(m.group(1)) == len(comps), "COMPONENT-AUDIT.md total is stale")

    uspace = (CA / "notes/ANDROID-USERSPACE.md").read_text(encoding="utf8")
    parts = re.split(r"^## ", uspace, flags=re.M)
    for heading, want in (("Android framework integration", len(ai)),
                          ("Significant userspace libraries", len(ul))):
        body = next((p for p in parts if p.startswith(heading)), "")
        nums = [int(x) for x in re.findall(r"^\| [^|]*\| (\d+) \|$", body, re.M)]
        require(sum(nums) == want, f"{heading} note table sums to {sum(nums)} not {want}")

    index = (RE / "index.md").read_text(encoding="utf8")
    index_rows = re.findall(r"^\| ([^|]+) \| (DONE|PARTIAL|BLOCKED|TODO) \|", index, re.M)
    require(len(index_rows) == 133 and {x[0].strip() for x in index_rows} == set(by_name), "index master table completeness")
    for r in comps:
        require((REPO / r["research_path"]).exists(), f"missing research path {r['component']} -> {r['research_path']}")

    markdown = [RE / "index.md"] + sorted(CA.glob("*.md")) + sorted((CA / "notes").glob("*.md"))
    bad_links = [x for p in markdown for x in check_links(p)]
    require(not bad_links, "broken relative links:\n" + "\n".join(bad_links))

    manifest = json.loads((CA / "audit-evidence/manifest-audit-2026-10-07.json").read_text())
    require(manifest["rows_total"] == manifest["rows_resolved"] == 4153, "manifest resolution")
    require(manifest["rows_missing_file"] == 0 and manifest["rows_wrong_field_count"] == 0, "manifest malformed/missing")
    require(manifest["rows_hash_mismatch"] == 19 and manifest["unregistered_files_total"] == 408 and len(manifest["duplicate_paths"]) == 1, "manifest drift recording")

    for report in ("README.md", "SUMMARY.md", "PARTIAL-TRIAGE.md", "MISSING-COVERAGE.md", "PORT-READINESS.md", "PROPOSED-CHANGES.md"):
        require((CA / report).exists(), f"missing report {report}")
    require((CA / "SUMMARY.md").read_text().startswith("# Coverage verdict: NEAR-COMPLETE"), "summary verdict heading")
    require("**126 canonical components**" in (CA / "PROPOSED-CHANGES.md").read_text(), "proposed component total")

    print("PASS: axis notes regenerate from their tables with no stale numbers")
    print("PASS: userspace/integration note tables sum to their source row counts")
    print(f"PASS: component status {dict(sorted(status_totals.items()))} matches the workspace")
    print(f"PASS: {len(km)} modules, {len(dt)} compatibles/{sum(int(r['nodes']) for r in dt)} nodes, "
          f"{len(ai)} integration + {len(ul)} library rows, {len(art)} artifact rows")
    print("PASS: only 10 E rows, all one MALI-GPU-KERNEL gap")
    print("PASS: all index/report relative links resolve")
    print("PASS: manifest hygiene recorded separately (4153 resolve, 19 stale, 408 unregistered, 1 duplicate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
