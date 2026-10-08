#!/usr/bin/env python3
"""Generate the final coverage handoff from synchronized tables; no migrations."""
from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from audit_policy import CANDIDATES, INTEGRATION, PROPOSALS

HERE = Path(__file__).resolve().parent
CA = HERE.parent
RE = CA.parent
DATE = "2026-10-08"

PARTIAL_MEANING = {
    "A": "Actionable static RE (whole-scope runtime acceptance may still be separate)",
    "B": "Kernel/source closed; broader proprietary boundary remains",
    "C": "Proprietary boundary",
    "D": "Hardware/runtime/teardown gated",
    "E": "Stale/duplicate/wrong scope",
    "F": "Broad umbrella/tracking scope",
}


def read(name: str) -> list[dict]:
    with (CA / name).open(newline="", encoding="utf8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def save(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf8")
    print(path.relative_to(RE.parent))


def esc(text: str) -> str:
    return (text or "-").replace("|", "\\|").replace("\n", " ").strip()


def link_from(path: str, base: Path = CA) -> str:
    return quote(os.path.relpath(RE.parent / path, base), safe="/-_.")


def metrics() -> dict:
    names = {
        "components": "components.tsv", "km": "kernel-modules.tsv", "dt": "device-tree.tsv",
        "hw": "hardware.tsv", "hs": "hals-services.tsv", "vs": "vendor-services.tsv",
        "fw": "firmware.tsv", "sw": "secure-world.tsv", "bs": "boot-storage.tsv",
        "ai": "android-integration.tsv", "ul": "userspace-libraries.tsv", "art": "artifact-map.tsv",
    }
    m = {k: read(v) for k, v in names.items()}
    m["status"] = Counter(r["status"] for r in m["components"])
    m["partial"] = Counter(r["partial_class"] for r in m["components"] if r["status"] == "PARTIAL")
    m["snapshot"] = json.loads((CA / "audit-evidence/final-snapshot.json").read_text())
    m["manifest"] = json.loads((CA / "audit-evidence/manifest-audit-2026-10-07.json").read_text())
    return m


def stamp(m: dict) -> str:
    s = m["snapshot"]
    return (f"Final snapshot: **{s['date']}**, source HEAD `{s['source_head']}`; "
            "workspace directories are authoritative. This report is reproducible from committed metadata, "
            "not a claim that later concurrent closures never occur.")


def next_targets(m: dict) -> list[dict]:
    by = {r["component"]: r for r in m["components"]}
    result = []
    for candidate in CANDIDATES:
        name = candidate["component"]
        if name in by:
            if by[name]["status"] != "PARTIAL" or by[name]["partial_class"] != "A":
                continue
            status = "PARTIAL"
        else:
            if name not in {"MALI-GPU-KERNEL", "CAMERA-ISP-KERNEL"}:
                raise ValueError(f"unregistered ranked candidate {name}")
            status = "PROPOSED"
        result.append({"rank": len(result) + 1, "status": status, **candidate})
    return result


def compact_ranking(m: dict, base: Path = CA) -> list[str]:
    return [f"{r['rank']}. **{r['component']}** ({r['status']}; {r['kind']}) — "
            f"{r['probability']}. [Evidence]({link_from(r['research_path'], base)})."
            for r in next_targets(m)]


def build_next(m: dict) -> None:
    targets = next_targets(m)
    with (CA / "next-re.tsv").open("w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, delimiter="\t", lineterminator="\n", fieldnames=list(targets[0]))
        w.writeheader(); w.writerows(targets)
    out = ["# Final next-RE priority list", "", stamp(m), "",
           "Ranked by qualitative probability of defensible closure of the entire named **static** scope, "
           "not document-writing speed. Effort is an estimate, not a guarantee. No reconstruction is performed "
           "by this audit. A matched source donor is not assumed where none is proved.", "",
           "Only remaining registered PARTIAL static targets and the two proposed kernel scopes appear below. "
           "A newly DONE target is automatically omitted. Static DTS contract closure is distinct from module "
           "parity; init/policy assembly, boot, SELinux, HAL registration and hardware acceptance are separate integration work.", ""]
    for r in targets:
        out += [f"## {r['rank']}. {r['component']} — {r['status']}", "",
                f"- **Work type:** {r['kind']}", f"- **Scope:** {r['scope']}",
                f"- **Difficulty / closure outlook:** {r['difficulty']}; {r['probability']}",
                f"- **Existing evidence:** {r['evidence']}. [Canonical report]({link_from(r['research_path'])}).",
                f"- **Missing source/behavior:** {r['missing']}",
                f"- **Closure criterion:** {r['closure']}", f"- **Expected effort:** {r['effort']}",
                f"- **Dependency:** {r['dependency']}", f"- **Phone necessary:** {r['phone']}", ""]
    out += ["## Separate ROM integration queue (not ranked RE)", "",
            "DONE here means named-scope static closure, not a finished LieppOS feature.", "",
            "| Component | Current status | Remaining ROM/acceptance action |", "|---|---|---|"]
    by = {r["component"]: r for r in m["components"]}
    for n, action in INTEGRATION.items():
        if n in by:
            out.append(f"| {n} | {by[n]['status']} | {esc(action)} |")
    for title, classes in (("Proprietary or runtime-only boundaries", "BCD"),
                           ("Umbrella/tracking scopes", "F")):
        rows = [r for r in m["components"] if r["status"] == "PARTIAL" and r["partial_class"] in classes]
        out += ["", f"## {title}", "", ", ".join(f"`{r['component']}`" for r in rows) or "None.", "",
                "Do not convert these into kernel-module parity targets or claim whole-scope closure by updating documentation."]
    save(CA / "NEXT-RE.md", "\n".join(out))


def build_partial(m: dict) -> None:
    rows = [r for r in m["components"] if r["status"] == "PARTIAL"]
    out = ["# PARTIAL triage", "", stamp(m), "",
           f"All **{len(rows)}** current PARTIAL directories have exactly one A–F class. "
           "A denotes actionable static work, not permission to claim untested end-to-end acceptance. "
           "OTA and recovery acceptance are D, not source-parity shortcuts. DONE rows are excluded.", "",
           "| Component | Class | Remaining boundary | Next action | Difficulty | Dependencies |",
           "|---|:---:|---|---|---|---|"]
    for r in rows:
        out.append("| " + " | ".join(esc(r[k]) for k in
                    ("component", "partial_class", "blocker", "recommended_action", "difficulty", "dependencies")) + " |")
    out += ["", "## Classification totals", "", "| Classification | Count |", "|---|---:|"]
    out += [f"| {c} — {PARTIAL_MEANING[c]} | {m['partial'][c]} |" for c in "ABCDEF"]
    out += [f"| **Total PARTIAL** | **{len(rows)}** |", "", "## Ranked static targets", ""] + compact_ranking(m)
    out += ["", "See [NEXT-RE.md](NEXT-RE.md) for exact closure criteria, source residuals, effort, dependencies, "
            "phone requirements and separate integration/proprietary/tracking queues."]
    save(CA / "PARTIAL-TRIAGE.md", "\n".join(out))


def build_missing(m: dict) -> None:
    e = [r for r in m["art"] if r["coverage"] == "E"]
    out = ["# Final missing-coverage verdict", "", stamp(m), "",
           "## CONFIRMED MISSING: MALI-GPU-KERNEL", "",
           "**One** genuinely missing registered ownership scope. Its ADD is recommended but **not applied**.", "",
           "- **Owns:** `mali_kbase_mt6878_r44.ko`, `mali_mgm_mt6878_r44.ko`, "
           "`mali_prot_alloc_mt6878_r44.ko`; enabled `arm,mali-valhall`, `mediatek,mali`, "
           "`mediatek,g3d_brisket`; normal-world GPU kernel/platform ABI and the kernel-facing GPU/gpuserv services.",
           "- **Not owned by:** TMEM-FFA's secure-memory transport or VENDOR-BLOB-HAL-INVENTORY's userspace/CSF payload inventory.",
           "- **Boundary:** proprietary userspace/CSF firmware stays retained; source availability and matched r44/MT6878 build are not assumed.",
           "- **Initial proposed status:** PARTIAL/A, HARD. Exact closure plan is in [NEXT-RE.md](NEXT-RE.md).", "",
           f"All **{len(e)}** normalized E rows converge on that one scope:", ""]
    out += [f"- `{r['artifact_type']}` `{r['artifact']}` — {r['notes']}" for r in e]
    out += ["", "## CAMERA-ISP-KERNEL — covered mixed scope, proposed SPLIT", "",
            "ISP kernel modules/source donors and near-exact imgsensor reconstruction already belong to CAMERA-HAL-ISP. "
            "This is **not a second coverage hole**. Accept the split recommendation to isolate kernel parity from "
            "HAL/3A/tuning/CCU, with an explicit transfer ledger and no duplicate primary owners.", "",
            "## POSSIBLE MISSING", "",
            "None is supported by unexplained artifacts. Generic MTK/APUSYS/media infrastructure, SCP-owned sensor "
            "register drivers, modem/RIL/IMS, TEE TAs, DSP/CSF firmware and per-unit calibration have explicit "
            "generic or proprietary boundaries; do not invent source-actionable components for them.", "",
            "## Not missing / negative findings", "",
            "Physical sensors belong to SENSOR-HUB/SCP firmware plus their registered sensor scopes; transport is "
            "SENSOR-HUB-KERNEL. Camera sensors/VCM/OIS/EEPROM have named child owners. Thermal-camera USB/power, "
            "command/viewer and radiometry are separate scopes. eSIM/eUICC and wireless charging are preserved "
            "not-fitted findings. RT5133 is a declared, unbound reference client, not a new active camera-LDO gap; "
            "see [correction](notes/RT5133-CORRECTION.md).", "",
            "Generic/dead artifacts stay enumerated in the TSVs with per-row evidence. Coverage is not source openness."]
    save(CA / "MISSING-COVERAGE.md", "\n".join(out))


def build_changes(m: dict) -> None:
    count = len(m["components"])
    delta = sum(p[4] for p in PROPOSALS if p[3] == "ACCEPT RECOMMENDATION")
    out = ["# Final taxonomy decision document", "", stamp(m), "",
           f"**Current registered total: {count}.** Recommendations only: no ADD/SPLIT/MERGE/REMOVE/RENAME "
           "has been applied by this audit. ACCEPT RECOMMENDATION is not migration approval or evidence of implementation.", "",
           "| Proposal | Operation | Decision | Conditional component-count change |", "|---|---|---|---:|"]
    out += [f"| {p[0]} | {p[1]} | {p[3]} | {p[4]:+d} |" for p in PROPOSALS]
    for cid, kind, names, decision, change, reason, consequences in PROPOSALS:
        out += ["", f"## {cid}: {kind} — {decision}", "", f"- **Components:** {names}",
                f"- **Evidence / rationale:** {reason}", f"- **Consequences and preservation:** {consequences}",
                f"- **Count change if approved and executed:** {change:+d}"]
        if cid == "PC-002":
            out += ["- [ISP module/source and proprietary-boundary evidence](../camera-stack/notes/isp-stack.md)."]
        if cid == "PC-009":
            out += ["- [Exact capture chronology and retraction](notes/RT5133-CORRECTION.md). "
                    "Physical population is NEEDS EVIDENCE; the specific unsupported rename is REJECT, not silently deferred."]
    out += ["", "## Conditional count, not current reality", "",
            f"If all **accepted recommendations** are approved and executed: {count} {delta:+d} = "
            f"**{count + delta} canonical components**. This conditional number is not the component database total. "
            "One ADD and one split-created child are offset by seven merged-away children/findings and two "
            "archived absence findings. Rejected RT5133 rename changes nothing.", "",
            "## Future migration prerequisites", "",
            "Archive originals first; write old→new path/owner redirects; preserve parity operands, source provenance, "
            "negative findings and manifests. Update every affected module/DT/service owner, registered directory, "
            "COPY-MANIFEST and status index together **after approval**, outside this final audit. No evidence is to be deleted."]
    save(CA / "PROPOSED-CHANGES.md", "\n".join(out))


def build_readiness(m: dict) -> None:
    rows = [
        ("1. Custom GKI/kernel", "STATIC BASELINE STRONG; custom boot unvalidated", "SYSTEM-DLKM 60/60 stock ELF bodies; exact BOOT-IMAGES containers and module-loader/KMI baseline. Custom kernel ABI/signatures, remaining DT/driver work and Mali KMD still require integration/acceptance."),
        ("2. Full custom ROM", "ARCHITECTURE MAPPED; integration incomplete", "External 24afa6b installs vendor.prop and includes bluetooth_audio.xml; preserve both. Verify correct emitted-image properties/precedence, assemble/check VINTF, init and enforcing SELinux, then validate actual HAL behavior."),
        ("3. Daily-driver readiness", "NOT PROVEN", "Actual boot, enforcing SELinux, calls/data/IMS, camera/audio, Wi-Fi/BT/GNSS, sensors, fingerprint/NFC, suspend, charging/thermal, OTA and recovery acceptance are required. Static DONE is not a runtime test."),
        ("4. Hardware feature parity", "PROPRIETARY / PHYSICAL / RUNTIME GATED", "Retain camera 3A/tuning/CCU, DSP/SCP/modem/CSF firmware, RIL/IMS, secure TAs, calibration and radiometry. USB/thermal kernel integration closures do not prove feature or high-power safety parity."),
        ("5. Google-free LieppOS", "NO NEW HARDWARE COVERAGE GAP; product work remains", "Remove/replace Google framework services while retaining vendor HAL/blob contracts; explicitly decide DRM/attestation/app compatibility. Policy, properties and HAL integration actions still apply."),
        ("6. Stock-integrity secondary slot", "STOCK B BASELINE VERIFIED; shared-state safety open", "BOOT-IMAGES proves Slot B stock while Slot A is modified. Preserve B as the anchor; do not boot-test experimental payloads by overwriting it. Shared userdata/FBE/metadata, rollback, OTA/snapshot and recovery behavior still need safe validation."),
        ("7. Future Linux slot", "RECONSTRUCTABLE BASELINE; feature parity uncertain", "GPU KMD/DT, camera ISP and retained firmware plus Linux modem userspace, SCP sensors, audio/DSP, display/input and charging policy remain porting constraints. Android HAL closure does not imply a Linux replacement."),
    ]
    out = ["# Final LieppOS development readiness", "", stamp(m), "",
           "Assessment only: no property, VINTF, ROM, kernel, slot or component changes are performed here.", "",
           "| Target | Assessment | Remaining work |", "|---|---|---|"]
    out += [f"| {a} | **{b}** | {c} |" for a, b, c in rows]
    out += ["", "## Verified closures used, not reopened", ""]
    by = {r["component"]: r for r in m["components"]}
    for n in ("SYSTEM-DLKM", "BOOT-IMAGES", "VENDOR-PROPERTIES", "VINTF-HAL-MANIFEST", "PARTITION-OWNERSHIP", "USB-CHARGER-INTEGRATION", "INTERNAL-THERMAL-USB"):
        r = by[n]
        out.append(f"- **{n} ({r['status']})**: {r['notes']}. [Research]({link_from(r['research_path'])}).")
    out += ["", "## Non-negotiable outstanding integration actions", "",
            "1. The missing vendor definitions were installed externally: 327 keys, 16 documented exclusions, one EGL rewrite. Preserve the fix and verify correct generated/inherited and emitted-image values plus SELinux context; runtime installation is not proven by a makefile alone.",
            "2. `bluetooth_audio.xml` is now included rather than `EXTRACT_ONLY`, with a vendor prebuilt module. Preserve it, run build-time VINTF checks and validate actual service registration.",
            "3. Validate real boot, SELinux and HAL behavior before claiming daily-driver readiness.",
            "4. Preserve the stock-integrity B slot and per-unit secure/calibration/shared metadata.",
            "5. Do not force RT5133 binding: the observed failure releases GPIO1 for the working WL2864C camera LDO. "
            "[Correction](notes/RT5133-CORRECTION.md)."]
    save(CA / "PORT-READINESS.md", "\n".join(out))


def build_summary(m: dict) -> None:
    s, p = m["status"], m["partial"]
    active = [r for r in m["dt"] if int(r["nodes_enabled"]) > 0]
    meaningful = [r for r in m["hs"] + m["vs"] if r["coverage"] != "C"]
    mapped = lambda rows: sum(r["coverage"] != "E" for r in rows)
    out = ["# Coverage verdict: NEAR-COMPLETE", "", stamp(m), "",
           "**Global audit finalized for this stock build.** All registered components and artifact axes are inventoried. "
           "One source-actionable ownership hole remains: proposed MALI-GPU-KERNEL. Camera ISP is a split of an "
           "already represented scope. NEAR-COMPLETE describes ownership, not open source or daily-driver readiness.", "",
           "## Measured headline", "",
           f"- Registered components: **{len(m['components'])}**; DONE **{s['DONE']}**, PARTIAL **{s['PARTIAL']}**, BLOCKED **{s['BLOCKED']}**, TODO **{s['TODO']}**.",
           f"- Shipped modules: **{len(m['km'])}** unique names; all accounted, including three explicit GPU E rows.",
           f"- DT compatibles: **{len(m['dt'])}**, across **{sum(int(r['nodes']) for r in m['dt'])}** nodes; active mapped **{mapped(active)}/{len(active)}** (three GPU E rows).",
           f"- HAL/service rows: **{len(m['hs']) + len(m['vs'])}**; non-generic mapped **{mapped(meaningful)}/{len(meaningful)}** (four GPU E rows).",
           f"- Physical inventory: **{len(m['hw'])}**; firmware **{len(m['fw'])}**; secure-world boundaries **{len(m['sw'])}**; partition families **{len(m['bs'])}**.",
           f"- Android integration **{len(m['ai'])}**; significant native libraries **{len(m['ul'])}**; normalized artifact rows **{len(m['art'])}**.",
           f"- Unexplained E rows: **0**. All **{sum(r['coverage']=='E' for r in m['art'])}** E rows are the one documented Mali scope, not registered owners.", "",
           "## PARTIAL A–F", ""]
    out += [f"- {c}={p[c]} — {PARTIAL_MEANING[c]}" for c in "ABCDEF"]
    out += [f"- Sum: **{sum(p.values())}**, exactly the current PARTIAL directory count.", "",
            "## Final decisions", "",
            "- **Mali:** ACCEPT RECOMMENDATION for one ADD. Source/parity remains work; userspace/CSF stays proprietary.",
            "- **ISP:** ACCEPT RECOMMENDATION for CAMERA-ISP-KERNEL SPLIT from CAMERA-HAL-ISP; not another missing component.",
            "- **RT5133:** bound-device claim RETRACTED; rename REJECTED. Declared client is unbound, zero registered/consumed RT5133 rails, WL2864C supplies camera rails. Static DONE remains. [Evidence](notes/RT5133-CORRECTION.md).",
            "- **Taxonomy:** ADD/SPLIT/MERGE/REMOVE/metadata recommendations only; current component set remains unchanged. "
            "[Decisions and conditional count](PROPOSED-CHANGES.md).",
            "- **Readiness:** custom GKI/container baseline is strong, but custom boot/ROM/daily-driver acceptance is not proven. "
            "Property definitions and bluetooth_audio.xml were installed externally in 24afa6b; preserve and verify them in the built image, and validate boot, SELinux and HALs. Preserve stock B.", "",
            "## Corrected next-RE ranking", ""] + compact_ranking(m)
    out += ["", "[Full criteria and separate integration/proprietary/tracking queues](NEXT-RE.md). "
            "VINTF-HAL-MANIFEST, VENDOR-PROPERTIES and BOOT-IMAGES are not unfinished RE targets when DONE.", "",
            "## Manifest hygiene — separate historical result", "",
            "The 2026-10-07 baseline records 19 stale hash/size entries, 408 unregistered files and one duplicate "
            "path; it is not a new current-workspace measurement. No COPY-MANIFEST repair was performed. "
            "[Historical details](notes/MANIFEST-HYGIENE.md). This drift does not invalidate the synchronized coverage database.", "",
            "## Handoff", "",
            "Use [the master index](../index.md), [PARTIAL triage](PARTIAL-TRIAGE.md), "
            "[missing coverage](MISSING-COVERAGE.md), [taxonomy decisions](PROPOSED-CHANGES.md) and "
            "[port readiness](PORT-READINESS.md). No further global coverage investigation is needed for this stock build. "
            "Remaining work is component RE, ROM integration and physical/runtime validation."]
    save(CA / "SUMMARY.md", "\n".join(out))


def build_index(m: dict) -> None:
    c = m["components"]
    out = ["# GQ5012BF1 Reverse-Engineering Index — final handoff", "", stamp(m), "",
           "**Single starting point** for subsequent component RE and LieppOS integration. Phone: Ulefone Armor 29 Pro Thermal, "
           "GQ5012BF1, MT6878T/Dimensity 7400 family. Workspace directory status is authoritative; no taxonomy migrations "
           "or status moves were made by this audit.", "",
           "- **DONE:** the named static/source/parity or inventory contract only; not proprietary HAL/firmware openness or runtime acceptance.",
           "- **PARTIAL:** exactly one A–F class with a real static, proprietary, physical/runtime or tracking boundary.",
           "- **BLOCKED:** evidence/source/access explicitly unavailable. **TODO:** untriaged accepted scope.",
           "- Artifact coverage: A dedicated owner; B broader owner; C generic; D dead/reference; E explained ownership gap.",
           "- `component` is the single assigned owner per artifact. Module `co_owners` and `umbrella_records` are "
           "cross-citations/tracking witnesses, not additional primary ownership. Proposed splits require a transfer ledger.",
           "- Evidence priority is capture provenance/actual observations, corrected research, exact parity, current trees, older/donor assumptions. "
           "A later-written summary without a newer capture does not override runtime evidence.", "",
           "## Current totals", "", "| Status | Count |", "|---|---:|"]
    out += [f"| {s} | {m['status'][s]} |" for s in ("DONE", "PARTIAL", "BLOCKED", "TODO")]
    out += [f"| **TOTAL** | **{len(c)}** |", "", "## PARTIAL classification", "", "| Classification | Count |", "|---|---:|"]
    out += [f"| {k} — {PARTIAL_MEANING[k]} | {m['partial'][k]} |" for k in "ABCDEF"]
    out += ["", "## Master component table", "",
            "Every registered scope appears once. Research links may be a shared canonical subsystem report; the "
            "workspace README provides the specific scope/closure operands. Neither is replaced by a circular audit-summary link.", "",
            "| Component | Status | Subsystem | Scope | Classification | Kernel | Userspace/HAL | Firmware | Hardware | Remaining boundary / DONE limitations | Research | Workspace |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in c:
        ws_path = RE.parent.parent / r["workspace_path"] / "README.md"
        workspace_link = quote(os.path.relpath(ws_path, RE), safe="/-_.")
        fields = [r[k] for k in ("component", "status", "subsystem", "scope", "partial_class", "kernel_state", "userspace_state", "firmware_state", "hardware_state")]
        fields += [r["blocker"] or r["notes"]]
        out.append("| " + " | ".join(esc(x) for x in fields) +
                   f" | [report]({link_from(r['research_path'], RE)}) | [scope]({workspace_link}) |")
    out += ["", "## Current artifact axes", ""]
    for name, key in (("kernel-modules", "km"), ("device-tree", "dt"), ("hardware", "hw"), ("hals-services", "hs"), ("vendor-services", "vs"),
                      ("firmware", "fw"), ("secure-world", "sw"), ("boot-storage", "bs"), ("android-integration", "ai"), ("userspace-libraries", "ul"), ("artifact-map", "art")):
        out.append(f"- [{name}.tsv](coverage-audit/{name}.tsv): {len(m[key])} rows, coverage {dict(sorted(Counter(r['coverage'] for r in m[key]).items()))}.")
    out += ["", "## Ranked actionable RE targets", ""] + compact_ranking(m, RE)
    out += ["", "[Exact scope, source residual, criteria, effort, dependency and phone requirement](coverage-audit/NEXT-RE.md).", "",
            "## Missing / proposed scopes and taxonomy", "",
            "**MALI-GPU-KERNEL** is the sole genuinely missing owner: proposed ADD. **CAMERA-ISP-KERNEL** is a proposed "
            "SPLIT from covered CAMERA-HAL-ISP, not another orphan. Neither is registered yet. "
            "GZ/AW36518/USB3/module-readiness merges and negative-absence retirements are recommendations only. "
            "RT5133 rename is rejected; [capture retraction](coverage-audit/notes/RT5133-CORRECTION.md). "
            "[Full decision/count consequences](coverage-audit/PROPOSED-CHANGES.md).", "",
            "## ROM integration is not unfinished component RE", "",
            "SYSTEM-DLKM's 60-module baseline, BOOT-IMAGES containers, vendor-property/VINTF ledgers and "
            "partition ownership are closed named static scopes. External 24afa6b has installed vendor.prop and "
            "bluetooth_audio.xml; preserve the changes and verify the emitted image, assemble/check policy/VINTF and "
            "validate actual boot/SELinux/HAL behavior. USB/thermal "
            "kernel closures do not establish charging safety, radiometry or runtime feature parity. "
            "[Separate queues](coverage-audit/NEXT-RE.md) and [seven readiness targets](coverage-audit/PORT-READINESS.md).", "",
            "## Proprietary, physical/runtime and umbrella limits", "",
            "SCP sensor algorithms/register drivers, modem/RIL/IMS, camera HAL/3A/tuning/CCU, DSP/CSF, TAs/keys, "
            "per-unit calibration and radiometry remain proprietary boundaries. RF/battery/cooling/microphone/runtime "
            "evidence cannot be closed by static documentation. Only current F-class PARTIALs are tracking scopes: " +
            ", ".join(f"`{r['component']}`" for r in c if r['status'] == 'PARTIAL' and r['partial_class'] == 'F') + ".", "",
            "## Reports and validation", "",
            "[Summary](coverage-audit/SUMMARY.md), [all PARTIAL A–F decisions](coverage-audit/PARTIAL-TRIAGE.md), "
            "[missing coverage](coverage-audit/MISSING-COVERAGE.md), [rebuild/check instructions](coverage-audit/README.md), "
            "[final corrections](coverage-audit/notes/FINAL-CORRECTIONS.md) and [validation](coverage-audit/notes/FINAL-VALIDATION.md). "
            "[Historical manifest hygiene](coverage-audit/notes/MANIFEST-HYGIENE.md) is separate from coverage completeness.", "",
            "**Final audit boundary:** stop global subsystem discovery for this stock build; proceed with component RE, "
            "ROM integration and physical/runtime validation. No new component research was started by this audit."]
    save(RE / "index.md", "\n".join(out))


def build_manifest_note(m: dict) -> None:
    a = m["manifest"]
    out = ["# Pack / manifest hygiene — historical baseline", "",
           "Run: **2026-10-07**, before the final audit correction. These are frozen historical measurements, "
           "not current status totals or a rerun against Claude's concurrent component batch.", "",
           "The read-only manifest auditor exited nonzero because bookkeeping drift remained. The audit did not "
           "edit COPY-MANIFEST.tsv, REVERSE-ENGINEERING-STATUS.md or component evidence. Coverage database "
           "consistency is checked independently.", "", "| Measure | Historical result |", "|---|---:|"]
    for label, key in (("Manifest rows", "rows_total"), ("Resolved", "rows_resolved"), ("Missing", "rows_missing_file"),
                       ("Malformed", "rows_wrong_field_count"), ("Hash mismatches", "rows_hash_mismatch"),
                       ("Size mismatches", "rows_size_mismatch"), ("Unregistered files", "unregistered_files_total")):
        out.append(f"| {label} | {a[key]} |")
    out += [f"| Duplicate paths | {len(a['duplicate_paths'])} |", "",
            "Historical drift owners: " + ", ".join(f"`{n}`" for n in a["components_with_drift"]) + ".", "",
            "Do not replace the synchronized component totals with this old run's status-tree counts. "
            "Future manifest repair must preserve evidence and be performed by its owner, outside this audit.", "",
            "[Full historical machine result](../audit-evidence/manifest-audit-2026-10-07.json)."]
    save(CA / "notes/MANIFEST-HYGIENE.md", "\n".join(out))


def build_readme(m: dict) -> None:
    out = ["# GQ5012BF1 reverse-engineering coverage audit — FINAL", "", stamp(m), "",
           "Reproducible database behind [the authoritative index](../index.md). **NEAR-COMPLETE ownership**: "
           "one confirmed missing scope (MALI-GPU-KERNEL), no unexplained artifact gap. No taxonomy changes applied.", "",
           "## Reports", "",
           "- [SUMMARY.md](SUMMARY.md) — final measured verdict",
           f"- [PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md) — all {m['status']['PARTIAL']} current PARTIAL components, A–F",
           "- [NEXT-RE.md](NEXT-RE.md) / [next-re.tsv](next-re.tsv) — status-filtered static ranking and separate work queues",
           "- [MISSING-COVERAGE.md](MISSING-COVERAGE.md) — one Mali gap; camera ISP already covered, proposed split",
           "- [PROPOSED-CHANGES.md](PROPOSED-CHANGES.md) — decisions and conditional count, not an implemented migration",
           "- [PORT-READINESS.md](PORT-READINESS.md) — seven readiness assessments and remaining integration actions",
           "- [RT5133 correction](notes/RT5133-CORRECTION.md) — capture chronology and bound-device retraction",
           "- [Final corrections](notes/FINAL-CORRECTIONS.md) and [validation](notes/FINAL-VALIDATION.md)",
           "- [Historical manifest hygiene](notes/MANIFEST-HYGIENE.md) — separate unresolved baseline drift", "",
           "## Machine tables", ""]
    for name, key in (("components", "components"), ("kernel-modules", "km"), ("device-tree", "dt"), ("hardware", "hw"), ("hals-services", "hs"),
                      ("vendor-services", "vs"), ("firmware", "fw"), ("secure-world", "sw"), ("boot-storage", "bs"), ("android-integration", "ai"),
                      ("userspace-libraries", "ul"), ("artifact-map", "art")):
        out.append(f"- [{name}.tsv]({name}.tsv): {len(m[key])} rows")
    out += ["", "## Reproduce from committed evidence", "",
            "From the research repository root (builders locate their files relative to themselves):", "", "```sh",
            "python3 reverse-engineering/coverage-audit/scripts/build-kernel-modules.py",
            "python3 reverse-engineering/coverage-audit/scripts/build-devicetree.py",
            "python3 reverse-engineering/coverage-audit/scripts/build-hardware.py",
            "python3 reverse-engineering/coverage-audit/scripts/build-services.py",
            "python3 reverse-engineering/coverage-audit/scripts/build-integration.py",
            "python3 reverse-engineering/coverage-audit/scripts/build-components.py",
            "python3 reverse-engineering/coverage-audit/scripts/build-reports.py",
            "python3 reverse-engineering/coverage-audit/scripts/check-audit.py",
            "python3 reverse-engineering/coverage-audit/scripts/test-final-audit.py -v", "```", "",
            "Do not redo the 457-module investigation. For a legitimate new workspace snapshot, refresh only changed "
            "pack identity/claims with the existing harvesters and rebuild the dependent axes. Do not reharvest unchanged "
            "stock firmware/integration payloads. The final snapshot record is metadata, not permission to modify component packs.", "",
            "`check-audit.py` checks current workspace membership/status, all A–F assignments and displayed totals, "
            "source/workspace paths, relative Markdown links, axis/normalized joins and the explicit GPU orphan sets. "
            "Determinism is verified by hashing generated outputs across a second build. "
            "Committed audit evidence contains metadata/claims only, no proprietary firmware/library/module payloads.", "",
            "The final report's snapshot date/source HEAD is explicit in [final-snapshot.json](audit-evidence/final-snapshot.json). "
            "All corrections are committed in the final audit commit; no push is required. Further work is component RE, "
            "ROM integration and physical/runtime validation, not another global coverage investigation."]
    save(CA / "README.md", "\n".join(out))


def main() -> int:
    m = metrics()
    build_next(m)
    build_partial(m)
    build_missing(m)
    build_changes(m)
    build_readiness(m)
    build_summary(m)
    build_index(m)
    build_manifest_note(m)
    build_readme(m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
