# CAMERA-ISP-KERNEL — completed reconstruction plan

The 2026-10-08 PARTIAL plan is complete for its registered nineteen-module normal-world
kernel scope.

1. **Inventory and ownership** — complete (`module-ownership.tsv`).
2. **Pinned public donor selection** — complete (NothingOSS kmod/kdm + exact GKI/clang).
3. **GQ5012BF1 source recovery** — complete (three explicit patches; fixed tree ids).
4. **All module builds** — complete (19/19).
5. **Whole-module acceptance** — complete: functions, data, ABI/CRC/KCFI, sections,
   relocations, symbols, strings and `.modinfo`; zero unresolved.
6. **Independent B1/B2** — complete, including 225 intermediate objects.
7. **DT/firmware/userspace boundaries** — documented; runtime remains NOT TESTED.

See [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md). Future work is on-device
acceptance or the separate proprietary `CAMERA-HAL-ISP` scope; neither reopens this static
kernel closure.
