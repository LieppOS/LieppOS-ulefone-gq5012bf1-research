#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 TrustKernel Phase 3G-R."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
checks: list[tuple[str, bool, str]] = []


def add(label: str, condition: bool, detail: str = "") -> None:
    checks.append((label, bool(condition), detail))


def text(path: str) -> str:
    p = ROOT / path
    add(f"exists: {path}", p.is_file(), str(p))
    return p.read_text(errors="replace") if p.is_file() else ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Phase 3F and superseding diagnosis.
phase3f = subprocess.run(
    [sys.executable, str(ROOT / "kernel/scripts/phase4_tkcore_island_phase3f_verify.py")],
    cwd=ROOT,
    capture_output=True,
    text=True,
    timeout=1800,
)
phase3f_output = phase3f.stdout + phase3f.stderr
add("Phase 3F verifier is 181/181 PASS", phase3f.returncode == 0 and "181/181 CHECKS PASSED" in phase3f_output)

diagnosis = text("kernel/phase4-tkcore-island-phase3g-r-diagnosis.md")
add("previous Phase-3G candidate retired", "permanently retired" in diagnosis)
add("previous candidate used stock tkcore_drv", "**stock `tkcore_drv.ko`**" in diagnosis)
for symbol in (
    "tee_core_alloc",
    "tee_core_add",
    "tee_core_del",
    "__tee_get",
    "tee_supp_cmd",
    "tee_wait_queue_sleep",
    "tee_wait_queue_wakeup",
):
    add(f"stock tkcore_drv incompatibility documented: {symbol}", f"`{symbol}`" in diagnosis)
add("diagnostic order is C0 then C1", diagnosis.find("### C0") < diagnosis.find("### C1"))

# C0 artifact and descriptor proof.
c0_json_path = ROOT / "workspace/phase4-tkcore-island/phase3g-r/c0/c0-build-validation.json"
add("C0 build validation exists", c0_json_path.is_file())
c0 = json.loads(c0_json_path.read_text()) if c0_json_path.is_file() else {}
c0_image = ROOT / "workspace/phase4-tkcore-island/phase3g-r/c0/vbmeta_b.c0.img"
add("C0 image exists", c0_image.is_file())
add("C0 image SHA exact", c0_image.is_file() and sha256(c0_image) == "46a6ec3b1572db72fb090e2fe68dbb0297a64b7dac825bf94ff488aff3640b18")
add("C0 descriptor count 27", c0.get("descriptor_count") == 27)
add("C0 descriptor semantics stock-identical", c0.get("descriptor_semantic_difference_count") == 0 and c0.get("descriptor_multiset_raw_equal") is True)
add("C0 contains zero module replacements", c0.get("changed_payload_modules") == 0)
add("C0 flags remain zero", c0.get("fixed_header", {}).get("flags") == 0)
add("C0 rollback index remains zero", c0.get("fixed_header", {}).get("rollback_index") == 0)
add("C0 top signature verified by avbtool", c0.get("top_signature_verified_by_avbtool") is True)
add("C0 traversal bounded explicitly", c0.get("bounded_traversal_expected_stop") == "odm_dlkm.img unavailable")

diff_path = ROOT / "kernel/phase4-tkcore-island-phase3g-r-c0-descriptor-diff.tsv"
diff_rows = list(csv.DictReader(diff_path.open(), delimiter="\t")) if diff_path.is_file() else []
add("C0 descriptor diff has 27 rows", len(diff_rows) == 27)
add("C0 descriptor diff has zero semantic changes", bool(diff_rows) and all(r["semantic_equal"] == "YES" and r["stock_descriptor_sha256"] == r["c0_descriptor_sha256"] for r in diff_rows))

# C0 explicit result and write/boot evidence.
c0_result = text("kernel/phase4-tkcore-island-phase3g-r-C0-result.md")
add("C0 boot result explicit FAIL", "PHASE3G_R_C0_LOCAL_VBMETA_BOOT_BLOCKED" in c0_result and "C0 B boot: **FAIL**" in c0_result)
add("C0 local key result explicit NO", "local top-level test key accepted: **NO**" in c0_result)
add("C0 one boot documented", "C0 boot attempts: `1`" in c0_result and "B retries: `0`" in c0_result)
add("C1 explicitly forbidden", "C1 is **forbidden and not attempted**" in c0_result)

write_log = text("workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-vbmeta-flash.txt")
boot_log = text("workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-single-boot.txt")
restore_log = text("workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-stock-vbmeta-restore.txt")
final_state = text("workspace/phase4-tkcore-island/phase3g-r/c0/device-write/c0-final-restoration-state.txt")
add("C0 candidate write succeeded", "RESULT=C0_VBMETA_WRITE_OKAY" in write_log)
boot_commands = [line for line in boot_log.splitlines() if re.fullmatch(r"\$ fastboot -s \S+ reboot", line)]
add("C0 has exactly one B boot command", len(boot_commands) == 1, repr(boot_commands))
add("C0 has no automatic B retry", boot_log.count("--set-active=b") == 1)
add("C0 boot timed out without ADB", "RESULT=FAIL_NO_ADB_300S" in boot_log)
add("stock vbmeta restoration write succeeded", "RESULT=STOCK_VBMETA_RESTORED_WRITE_OKAY" in restore_log)
add("final stock vbmeta hash exact", "e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93" in final_state)
add("final stock vendor_boot hash exact", "c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756" in final_state)
add("final stock vendor_dlkm hash exact", "fce7acfb64956126a03929f085050ab1b300272333e84abf27b9e708aaa40297" in final_state)
add("final A current and active", "bootctl get-current-slot: rc=0 value=0" in final_state and "bootctl get-active-boot-slot: rc=0 value=0" in final_state)
add("final A bootable and successful", "bootctl is-slot-bootable 0: rc=0 value=1" in final_state and "bootctl is-slot-marked-successful 0: rc=0 value=1" in final_state)
add("final B bootable and not successful", "bootctl is-slot-bootable 1: rc=0 value=1" in final_state and "bootctl is-slot-marked-successful 1: rc=70 value=0" in final_state)
add("snapshot merge none", "bootctl get-snapshot-merge-status: rc=0 value=none" in final_state)

# Matrix enforces the fail branch and blocks every C1 check.
results_path = ROOT / "kernel/phase4-tkcore-island-phase3g-r-results.tsv"
results = list(csv.DictReader(results_path.open(), delimiter="\t")) if results_path.is_file() else []
by_check = {r["check"]: r for r in results}
add("C0 static result PASS", by_check.get("C0 image static validation", {}).get("status") == "PASS")
add("C0 write result PASS", by_check.get("C0 write verification", {}).get("status") == "PASS")
add("C0 boot result FAIL", by_check.get("C0 B boot", {}).get("status") == "FAIL")
c1_rows = [r for r in results if r.get("check", "").startswith("C1 ")]
add("all C1 result rows blocked", len(c1_rows) == 8 and all(r["status"] == "BLOCKED" and r["blocker"] == "C0_FAIL" for r in c1_rows))
c1_workspace = ROOT / "workspace/phase4-tkcore-island/phase3g-r/c1"
add("no C1 artifact workspace created", not c1_workspace.exists())

# Ledger and command-scope safety.
ledger_path = ROOT / "kernel/phase4-tkcore-island-phase3g-r-c0-flash-ledger.tsv"
ledger = list(csv.DictReader(ledger_path.open(), delimiter="\t")) if ledger_path.is_file() else []
add("C0 ledger has only vbmeta_b", len(ledger) == 1 and ledger[0]["partition"] == "vbmeta_b")
add("C0 ledger records exact restoration", bool(ledger) and ledger[0]["status"] == "FLASHED_EXACT_BOOT_BLOCKED_RESTORED_STOCK_EXACT")
command_lines = "\n".join(line for body in (write_log, boot_log, restore_log) for line in body.splitlines() if line.startswith("$ "))
flash_targets = re.findall(r"\bflash\s+(\S+)", command_lines)
add("no Slot-A partition writes", all(not t.endswith("_a") for t in flash_targets), repr(flash_targets))
add("only vbmeta_b partition flashed", flash_targets == ["vbmeta_b", "vbmeta_b"], repr(flash_targets))
add("no super resize", " resize " not in command_lines and " super" not in command_lines)
add("verification not disabled", "--disable-verification" not in command_lines and "--disable-verity" not in command_lines)
add("bootloader not relocked", " flashing lock" not in command_lines and " oem lock" not in command_lines)
for forbidden in ("rpmb", "nvram", "nvdata", "persist", "calibration", "preloader"):
    add(f"no {forbidden} write", forbidden not in " ".join(flash_targets).lower())

# Required CURRENT status wording in all seven documents.
current_docs = (
    "kernel/zero-blob-queue.md",
    "kernel/module-replacement-plan.md",
    "kernel/phase4-remaining-module-triage.md",
    "kernel/phase4-remaining-module-dependency-graph.md",
    "kernel/phase4-slot-b-minimum-source-stack.md",
    "kernel/phase4-buildability-plan.md",
    "kernel/phase4-tkcore-island-phase3-work-queue.md",
)
required_current = (
    "**PHASE 3F:** STATIC PASS.",
    "**PHASE 3G:** FAILED BEFORE G1.",
    "**RUNTIME TRUSTKERNEL:** NOT YET TESTED.",
    "**PREVIOUS PHASE-3G CANDIDATE:** RETIRED — INVALID STATIC DEPLOYMENT UNIT.",
    "C1 was not attempted",
)
for path in current_docs:
    body = text(path)
    add(f"CURRENT status updated: {path}", all(s in body for s in required_current))

failed = [(label, detail) for label, ok, detail in checks if not ok]
for label, ok, detail in checks:
    print(f"[{'OK' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail and not ok else ""))
if failed:
    print(f"{len(checks) - len(failed)}/{len(checks)} CHECKS PASSED")
    raise SystemExit(1)
print(f"{len(checks)}/{len(checks)} CHECKS PASSED")
