# Pack / manifest hygiene — historical baseline

Run: **2026-10-07**, before the final audit correction. These are frozen historical measurements, not current status totals or a rerun against Claude's concurrent component batch.

The read-only manifest auditor exited nonzero because bookkeeping drift remained. The audit did not edit COPY-MANIFEST.tsv, REVERSE-ENGINEERING-STATUS.md or component evidence. Coverage database consistency is checked independently.

| Measure | Historical result |
|---|---:|
| Manifest rows | 4153 |
| Resolved | 4153 |
| Missing | 0 |
| Malformed | 0 |
| Hash mismatches | 19 |
| Size mismatches | 19 |
| Unregistered files | 408 |
| Duplicate paths | 1 |

Historical drift owners: `CAMERA-IMX989`, `FT3680-TOUCH`, `HAPTICS`, `SENSOR-HUB`, `YFT-DEVINFO`.

Do not replace the synchronized component totals with this old run's status-tree counts. Future manifest repair must preserve evidence and be performed by its owner, outside this audit.

[Full historical machine result](../audit-evidence/manifest-audit-2026-10-07.json).
