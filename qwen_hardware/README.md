# qwen_hardware — GQ5012BF1 / Ulefone Armor 29 Pro Thermal hardware capability audit

Task spec: `~/Downloads/qwen_flash(1).md` (Ulefone Armor 29 Pro Thermal / GQ5012BF1 Full Hardware
Capability Audit). This directory is the single authoritative workspace for that audit.

Two passes have run:

| Pass | Scope | Result |
|---|---|---|
| **1 — inventory** | full subsystem survey from local artefacts + web | 20 subsystem reports, 5 final reports, 24 open unknowns |
| **2 — verification** (2026-09-08) | resolve/narrow U1–U24 without re-inventorying | 13 PROVEN, 6 STRONGLY_SUPPORTED, 1 LIKELY, 7 UNKNOWN, 5 TEARDOWN_REQUIRED; 26 finding documents |

**Start with `final/` and `verification/final/VERIFICATION-REPORT.md`.** Everything else is
working material; pass-1 subsystem reports carry supersession banners where pass 2 changed them.

## Method (three-layer model, enforced everywhere)

```text
1. CHIP CAN DO              — datasheet/register-level capability of the silicon
2. BOARD SUPPORTS           — what this board's wiring / DT config / rails allow
3. STOCK SOFTWARE USES      — what the shipping firmware + apps actually enable
```

Confidence scale: `PROVEN` > `STRONGLY_SUPPORTED` > `LIKELY` > `POSSIBLE` > `UNKNOWN`,
plus `TEARDOWN_REQUIRED` where only physical inspection can settle the question.

Two standing rules: no confidence upgrade without evidence, and a negative search is
uncertainty, never proof of absence (a *proven absence* needs a positive structural
argument — e.g. an exhaustive device-tree or HAL enumeration showing no node).

## Read this first — two cross-cutting corrections

1. **The 2026-08-31 "live-stock" capture is not stock.** It ran a **LieppOS GSI** over the stock
   vendor/kernel (`ro.lineage.display.version = LieppOS-23-...-GSI`, KernelSU-rooted, zero Ulefone
   packages installed). Kernel, driver, device-tree, bus and vendor-partition facts remain valid;
   every *framework-level* observation is relabelled "observed under GSI".
   See `verification/findings/00-snapshot-provenance-correction.md`.
2. **`vendor/etc/init/hw/init.yft.rc` is a platform-wide ODM option catalogue, not this board's
   bill of materials.** It is the root cause of the disproven wireless-charging, rich-haptics and
   similar claims. Presence of an init stanza proves the *platform* can drive the part, not that
   the part is fitted.

## Layout

```text
qwen_hardware/
├── README.md                        this file
├── findings/
│   ├── findings-log.md              chronological pass-1 discoveries (local + web)
│   ├── component-candidates.md      candidate vs installed per subsystem
│   └── contradictions.md            C1–C12 — now a closed/corrected ledger
├── subsystems/                      pass-1 per-category working reports (24 files, banner-marked)
├── evidence/
│   ├── local/                       condensed extracts from repo artefacts
│   ├── live-device/                 condensed extracts from the frozen 2026-08-31 capture
│   ├── datasheets/                  per-chip datasheet/spec digests (web-sourced)
│   └── source-extracts/             verbatim DT / module / HAL passages used as proof
├── search/                          pass-1 query, source and negative-result logs
├── progress/
│   ├── STATUS.md                    two-pass status board + 24-row verification outcome table
│   ├── TODO.md                      post-verification follow-ups (read-only / bench / physical)
│   └── unknowns.md                  pass-1 scratch list — superseded, points at final/UNKNOWN-HARDWARE.md
├── verification/                    pass 2 — the verification pass
│   ├── findings/                    26 evidence-structured documents (U1–U24 + 2 new topics)
│   ├── evidence/                     newly normalised device-tree and runtime extracts
│   ├── search/                      queries.md (Q/L ids) + sources.md (VL/VI ids, quality + scope)
│   └── final/VERIFICATION-REPORT.md authoritative counts, corrections, next safe steps
└── final/                           AUTHORITATIVE — supersedes all of the above
    ├── MASTER-HARDWARE-INVENTORY.md every part, per subsystem, with status
    ├── HARDWARE-CAPABILITY-MATRIX.md chip-can-do / board / stock per capability
    ├── UNUSED-HIDDEN-CAPABILITIES.md  fitted-but-unused, and what software can never add
    ├── UNKNOWN-HARDWARE.md            U1–U24 with current status + evidence needed to close
    └── FINAL-REPORT.md               revised executive conclusion
```

## Primary local evidence

| Evidence | Path |
|---|---|
| Frozen capture, 2026-08-31 11:56 (**LieppOS GSI**, not stock) | `../workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/` |
| Stock image extraction | `../workspace/gq5012bf1/stock/` (vendor_boot, DTB/DTBO, firmware, DLKM) |
| Partition/HAL/property inventory | `../workspace/gq5012bf1/reports/inventory/` |
| Kernel module reconstruction contracts | `../kernel/phase4-*.md` |
| Prior consolidated inventory (baseline, superseded by this workspace) | `../hardware/MASTER-HARDWARE-INVENTORY.md` |

`adb devices` returns no device in either pass, so all live-device statements come from the
frozen 2026-08-31 snapshot and are labelled with its provenance rather than re-verified.

## Source recording

Every claim in `final/` and `verification/findings/` resolves to an id in one of the two
source logs. Pass 2 ids: `VL01`–`VL26` (local) and `VI01`–`VI24` (internet) in
`verification/search/sources.md`, with publisher, access date, exact claim supported,
quality (**A** datasheet/OEM/platform vendor, **B** independent database, **C** teardown or
analogue inference) and scope (exact-device / exact-chip / family-level / generic).
