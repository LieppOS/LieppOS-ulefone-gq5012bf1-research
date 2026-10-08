#!/usr/bin/env python3
"""Fail-closed quality gate for the GQ5012BF1 coverage audit."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

from audit_policy import CANDIDATES, PROPOSALS

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
        target = unquote(target.strip().strip("<>").split("#", 1)[0])
        if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            label = path.relative_to(REPO) if path.is_relative_to(REPO) else path
            bad.append(f"{label} -> {target}")
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
    require(all(r["partial_class"] in set("ABCDEF") for r in partials),
            "every PARTIAL must have exactly one A–F class")
    require(sum(Counter(r["partial_class"] for r in partials).values()) == status_totals["PARTIAL"],
            "PARTIAL class totals do not reconcile")
    require(all(r["partial_class"] == "SCOPE-CLOSED" for r in comps if r["status"] == "DONE"),
            "a DONE row is classified as PARTIAL")
    snapshot = json.loads((CA / "audit-evidence/final-snapshot.json").read_text())
    fingerprint = hashlib.sha256("".join(f"{n}\t{workspace[n]}\n" for n in sorted(workspace)).encode()).hexdigest()
    require(snapshot["workspace_status_sha256"] == fingerprint and
            Counter(snapshot["status"]) == status_totals and snapshot["registered_components"] == len(comps),
            "workspace moved since final snapshot; reconcile once before final commit")
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
    require(rt["presence"] == "PRESENT-NOT-BOUND" and rt["component"] == "RT5133-POWER-IC" and
            "unbound" in rt["device"], "RT5133 client-name misread has returned")
    rtdt = next(r for r in dt if r["compatible"] == "richtek,rt5133")
    require(rtdt["node_state"] == "PRESENT-NOT-BOUND" and "inactive" in rtdt["physical_function"],
            "RT5133 DT state must distinguish declaration from binding")
    require(by_name["RT5133-POWER-IC"]["hardware_state"] == "PRESENT-NOT-BOUND" and
            "REJECT" in by_name["RT5133-POWER-IC"]["recommended_action"], "unsupported RT5133 rename")
    rtko = next(r for r in km if r["module"] == "rt5133-regulator.ko")
    require(rtko["in_modules_load"] == "yes" and rtko["load_phase"] == "first-stage",
            "RT5133 module loads despite unsuccessful probe")

    hs, vs = rows("hals-services.tsv"), rows("vendor-services.tsv")
    require(len(hs) == 272 and len(vs) == 253, "HAL/service universe")
    require({r["artifact"] for r in hs if r["coverage"] == "E"} == {"vendor.mediatek.hardware.gpu", "vendor.mediatek.hardware.gpuserv"}, "HAL E set")
    require({r["service"] for r in vs if r["coverage"] == "E"} == {"vendor.gpuserv-default", "vendor.mali_platform-mediatek"}, "service E set")
    require(sum(r["binary_present"] == "no" and not r["service"].startswith("[exec]") for r in vs) == 22, "absent init-service executable count")

    fw, sw, bs = rows("firmware.tsv"), rows("secure-world.tsv"), rows("boot-storage.tsv")
    require(len(fw) == 80 and not any(r["coverage"] == "E" for r in fw), "firmware accounting")
    require(len(sw) == 13 and not any(r["coverage"] == "E" for r in sw), "secure-world accounting")
    require(len(bs) == 61 and not any(r["coverage"] == "E" for r in bs), "boot/storage accounting")
    require(all(re.fullmatch(r"[0-9a-f]{64}", h) for r in fw for h in r["sha256"].split(";")),
            "invalid firmware metadata hashes")

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
        require(all(r["coverage"] in set("ABCDE") for r in data), f"bad coverage in {name}")
        bad = {r["component"] for r in data if r["component"] not in allowed}
        require(not bad, f"noncanonical component references in {name}: {bad}")
        require(all(r.get("component_status", workspace.get(r["component"])) == workspace[r["component"]]
                    for r in data if r["component"] in workspace), f"stale owner status in {name}")
        require(all((r["coverage"] == "E") == (r["component"] == "UNMAPPED") for r in data),
                f"unmapped owner/coverage contradiction in {name}")

    # Reconcile every normalized row back to an axis, not just the grand total.
    def sig(kind, artifact, source, row):
        return kind, artifact, source, row["component"], row["coverage"]
    expected = []
    for table, kind, artifact_key, source_key in (
        (km, "kernel-module", "module", "partitions"), (dt, "dt-compatible", "compatible", "dt_source"),
        (hw, "physical-hardware", "device", "inventory"), (vs, "init-service", "service", "rc_files"),
        (fw, "firmware", "artifact", "partition_or_source"), (sw, "secure-world", "area", "partition"),
        (bs, "partition", "artifact", "partition_or_source"),
        (ai, "android-integration", "artifact", "partition"), (ul, "userspace-library", "library", "partitions")):
        expected.extend(sig(kind, r[artifact_key], r[source_key], r) for r in table)
    expected.extend(sig(r["artifact_type"], r["artifact"],
                        r["declaring_docs"] if r["artifact_type"] == "hw-backend-lib" else r["partition"], r)
                    for r in hs)
    actual = [sig(r["artifact_type"], r["artifact"], r["partition_or_source"], r) for r in art]
    require(Counter(expected) == Counter(actual), "normalized map disagrees with its artifact axes")
    require({(r["artifact_type"], r["artifact"]) for r in art if r["coverage"] == "E"} ==
            {(k, a) for k, a, _, _, cov in expected if cov == "E"}, "unexplained normalized E row")

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
    require(len(index_rows) == len(comps) and dict((n.strip(), s) for n, s in index_rows) == workspace,
            "index master table status/set mismatch")
    for r in comps:
        require((REPO / r["research_path"]).is_file(), f"missing research path {r['component']} -> {r['research_path']}")
        require(not r["research_path"].endswith("coverage-audit/SUMMARY.md"), "circular research-summary fallback")
        require((WORKSPACE / r["workspace_path"] / "README.md").is_file(), f"missing workspace path {r['component']}")
        require(r["workspace_path"] == f"Reverse Engineer - {r['status']}/{r['component']}",
                f"workspace path/status disagree for {r['component']}")
    for filename, key in (("harvested-pack-module-claims.tsv", "source_file"),
                          ("harvested-pack-dt-claims.tsv", "path"),
                          ("harvested-pack-artifact-claims.tsv", "source_file")):
        sources = {r[key] for r in rows("audit-evidence/" + filename) if r[key]}
        require(all((WORKSPACE / p).exists() for p in sources), f"nonexistent evidence source in {filename}")

    ranked = rows("next-re.tsv")
    names = [r["component"] for r in ranked]
    expected_names = [r["component"] for r in CANDIDATES if
                      r["component"] in {"MALI-GPU-KERNEL", "CAMERA-ISP-KERNEL"} or
                      (r["component"] in by_name and by_name[r["component"]]["status"] == "PARTIAL" and
                       by_name[r["component"]]["partial_class"] == "A")]
    require(names == expected_names and len(names) == len(set(names)), "ranked list is stale/duplicated")
    for n, r in enumerate(ranked, 1):
        require(int(r["rank"]) == n and all(r[k] for k in
                ("scope", "difficulty", "evidence", "missing", "closure", "effort", "dependency", "phone")),
                "incomplete next-RE closure criteria")
        if r["component"] in by_name:
            require(r["status"] == "PARTIAL" and by_name[r["component"]]["status"] == "PARTIAL",
                    "an already-DONE target is recommended as PARTIAL→DONE")
        else:
            require(r["status"] == "PROPOSED", "an unapplied proposal is listed as registered")
        require((REPO / r["research_path"]).is_file(), "ranked evidence path is missing")
    readme = (CA / "README.md").read_text()
    require(f"all {status_totals['PARTIAL']} current PARTIAL components" in readme, "stale README PARTIAL count")
    for doc in (RE / "index.md", CA / "PARTIAL-TRIAGE.md"):
        text = doc.read_text()
        for s in ("DONE", "PARTIAL", "BLOCKED", "TODO") if doc == RE / "index.md" else ():
            require(f"| {s} | {status_totals[s]} |" in text, "stale index headline count")
        for c in "ABCDEF":
            require(re.search(rf"^\| {c} — [^|]+\| {class_want[c]} \|$", text, re.M),
                    f"stale A–F total in {doc.name}")

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
    proposed = (CA / "PROPOSED-CHANGES.md").read_text()
    conditional = len(comps) + sum(p[4] for p in PROPOSALS if p[3] == "ACCEPT RECOMMENDATION")
    require(f"**{conditional} canonical components**" in proposed and "not current reality" in proposed,
            "conditional taxonomy count is mistaken for an implemented migration")
    require("PC-009: RENAME — REJECT" in proposed, "RT5133 unsupported rename not retracted")
    for f in CA.rglob("*"):
        require(not (f.is_file() and f.suffix.lower() in
                     {".ko", ".so", ".img", ".bin", ".dtb", ".dtbo", ".elf", ".zip"}),
                f"payload copied into audit: {f}")

    print("PASS: axis notes regenerate from their tables with no stale numbers")
    print("PASS: userspace/integration note tables sum to their source row counts")
    print(f"PASS: component status {dict(sorted(status_totals.items()))} matches the workspace")
    print(f"PASS: {len(km)} modules, {len(dt)} compatibles/{sum(int(r['nodes']) for r in dt)} nodes, "
          f"{len(ai)} integration + {len(ul)} library rows, {len(art)} artifact rows")
    print("PASS: all normalized rows reconcile with their axes; only 10 E rows, one Mali scope")
    print("PASS: status-filtered static ranking, proposal decisions and RT5133 retraction")
    print("PASS: no firmware/module/library payloads in coverage-audit")
    print("PASS: all index/report relative links resolve")
    print("PASS: manifest hygiene recorded separately (4153 resolve, 19 stale, 408 unregistered, 1 duplicate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
