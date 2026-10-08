# Pack / manifest hygiene

Audit run: 2026-10-07

This is deliberately separate from reverse-engineering completeness.

The existing `reverse-engineering/scripts/manifest-audit.py` was run against the canonical workspace and `COPY-MANIFEST.tsv`. It exited non-zero because bookkeeping drift remains; no unrelated workspace file or manifest row was fixed.

| Measure | Result |
|---|---:|
| Manifest rows | 4153 |
| Resolved rows | 4153 |
| Missing files | 0 |
| Malformed rows | 0 |
| Hash mismatches | 19 |
| Size mismatches | 19 |
| Status-tree files | 4556 |
| Unregistered files | 408 |
| Duplicate paths | 1 |

Status-tree component counts from the independent run: BLOCKED=3, DONE=85, PARTIAL=45, TODO=0.

## Drift owners

`CAMERA-IMX989` (3 hash/3 size), `FT3680-TOUCH` (10 hash/10 size), `HAPTICS` (1 hash/1 size), `SENSOR-HUB` (1 hash/1 size), `YFT-DEVINFO` (4 hash/4 size).

## Unregistered-file owners

`CAMERA-HAL-ISP` (26), `CAMERA-IMX989` (117), `FM-KERNEL` (9), `GNSS-KERNEL-TRANSPORT` (80), `MT6637-BT-KERNEL` (45), `MT6637-WIFI-KERNEL` (9), `MTK-MBOX` (1), `SENSOR-HUB-KERNEL` (110), `YFT-DEVINFO` (11).

## Duplicate path

`Reverse Engineer - DONE/HAPTICS/notes/haptics.md`.

Full machine report: [`../audit-evidence/manifest-audit-2026-10-07.json`](../audit-evidence/manifest-audit-2026-10-07.json).
