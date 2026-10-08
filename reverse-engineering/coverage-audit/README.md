# GQ5012BF1 coverage database — accelerator ownership synchronized

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

[PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md): all 42 current PARTIAL components. Six authorized PARTIAL additions and singleton module/DT ownership are applied; no source parity is fabricated. [Accelerator roadmap](../accelerator-re-roadmap.md).

## Reports

- [SUMMARY.md](SUMMARY.md)
- [PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md)
- [NEXT-RE.md](NEXT-RE.md)
- [MISSING-COVERAGE.md](MISSING-COVERAGE.md)
- [PROPOSED-CHANGES.md](PROPOSED-CHANGES.md)
- [PORT-READINESS.md](PORT-READINESS.md)

## Reproduce committed metadata

```sh
python3 reverse-engineering/coverage-audit/scripts/build-kernel-modules.py
python3 reverse-engineering/coverage-audit/scripts/build-devicetree.py
python3 reverse-engineering/coverage-audit/scripts/build-hardware.py
python3 reverse-engineering/coverage-audit/scripts/build-services.py
python3 reverse-engineering/coverage-audit/scripts/build-integration.py
python3 reverse-engineering/coverage-audit/scripts/build-components.py
python3 reverse-engineering/coverage-audit/scripts/build-reports.py
python3 reverse-engineering/coverage-audit/scripts/check-audit.py
python3 reverse-engineering/coverage-audit/scripts/test-final-audit.py
```

No fresh full module investigation or payload harvest. Changed pack identity/claims were refreshed with existing harvesters. [Current snapshot](audit-evidence/final-snapshot.json). [Historical final-audit validation](notes/FINAL-VALIDATION.md) is not the new accelerator snapshot; current preparation has its own validation record. No proprietary payload enters Git.
