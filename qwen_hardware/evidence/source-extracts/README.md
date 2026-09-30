> **Pass-2 pointer (2026-09-08).** First-pass working material. Where anything here conflicts with `../../final/` or `../../verification/findings/`, the verification pass wins. Two blanket corrections apply: the 2026-08-31 capture ran a **LieppOS GSI**, so its framework-level observations are not stock Ulefone behaviour; and `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this board's bill of materials.

# Source-extracts

The exact local proof files are intentionally kept in their original repository locations to avoid duplicating large binaries/text:

* Live ADB snapshot: `../../workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/`
* DT and module contracts: `../../kernel/phase4-*.md`
* Merged DT: `../../workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`
* Baseline inventory: `../../hardware/MASTER-HARDWARE-INVENTORY.md`

Condensed/filtered extracts are in `../local/`, `../live-device/` and `../datasheets/`. The most important verbatim/filtered files are `../local/buses-live.txt`, `../local/sensors-live.txt`, `../live-device/camera-hal-live.txt` and `../datasheets/chip-capabilities.md`.
