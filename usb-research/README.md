# GQ5012BF1 USB subsystem research

Device: Ulefone Armor 29 Pro Thermal (`GQ5012BF1`, project `armol`, MT6878T/mt6878, Linux 6.1 Android GKI).

## Scope and evidence discipline

This directory reconstructs five paths separately:

1. external Type-C data;
2. Android gadget/UDC;
3. host/OTG;
4. internal ThermoVue thermal-camera USB;
5. Type-C CC/PD and charging/power.

SoC capability, DT enablement, runtime operation and PCB routing are independent claims. In particular, charging-protocol policy and a USB-C receptacle do **not** prove SuperSpeed data routing. A 480 Mbit/s observation does **not** prove that SuperSpeed lanes are electrically absent.

Finding labels are: `PROVEN`, `STRONGLY_SUPPORTED`, `LIKELY`, `POSSIBLE`, `UNKNOWN`, and `DISPROVEN`.

## Report map

- `FINAL-USB-REPORT.md` — numbered answers to all 25 completion questions.
- `USB-ARCHITECTURE.md` — end-to-end diagrams and shared-resource model.
- `USB-EVIDENCE-MATRIX.md` — conclusion/evidence/confidence/missing-evidence matrix.
- `USB-DEVICE-TREE.md` — merged base-DTB + DTBO graph.
- `USB-CONTROLLER.md` — MTU3/xHCI identity and controller count.
- `USB-PHY.md` — XS-PHY and absent production U3 path.
- `USB-TYPEC-PD.md` — MT6375 CC, orientation, VCONN, PD/PPS/UFCS and DP status.
- `USB-CHARGING-INTEGRATION.md` — 120-W sink and 10-W reverse-power architecture.
- `USB-INTERNAL-THERMAL-CAMERA.md` — direct `3474:4321` UVC runtime proof.
- `USB-STOCK-RUNTIME.md` — external gadget and internal-host captures.
- `USB-KERNEL-DRIVERS.md` — stock module/source/ABI inventory.
- `USB-ANDROID-STACK.md` — AIDL HAL, init/configfs, VINTF and SELinux.
- `USB3-HARDWARE-ROUTING.md` — daughterboard/FCC research and physical test plan.
- `USB3-FEASIBILITY.md` — independent A–I verdict and five-case analysis.
- `MT6878-DONOR-COMPARISON.md` — NothingOSS and sibling-SoC comparison.
- `CUSTOM-KERNEL-USB-PLAN.md` — complete function-preserving implementation plan.
- `USB-WEB-SOURCE-LEDGER.md` — external source provenance and caveats.
- `USB-RESEARCH-COVERAGE-AUDIT.md` — honest phase-by-phase completeness and remaining tests.

## Provenance baseline

- Research repository starting HEAD for this investigation: `dd125403d0cd7c42e5aabeaabd7b191237c3b9a7` (`master`).
- Stock DT source: `workspace/gq5012bf1/stock/vendor_boot-unpacked/dtb`.
- Stock DT-table SHA-256: `bc156c29c33d8226230f07888df0a3d7a1e9c4b85c5fd550a4c4bd1a3134c0d4`.
- First FDT payload SHA-256: `9ee54c6c02a3b6d8a3c47e1a43e2cefa0953944ebaee6acb858f97437322fd53`.
- Live captures began only after `ro.boot.slot_suffix=_a` and `sys.boot_completed=1` were verified.
- The initial live phase was read-only. No partition, RPMB, calibration, NVRAM, persist, GPIO, I2C or sysfs control write was performed.

## Reused pre-existing research

The following are prior evidence, not duplicated work:

- `kernel/phase4-extcon-mtk-usb-*`: frozen stock-module oracle and clean-room behavior/ABI analysis.
- `kernel/phase4-yft-tiny2c-usb-*`: thermal rail, FM78100 companion, userspace ABI and USB-boundary analysis.
- `kernel/usmart-post-audit-usb-topology-consistency.md`: earlier correction of stale `11211000.usb1` claims.
- `kernel/usmart/**` and `kernel/usmart-full-contract.md`: uSmart/accessory power and USB routing evidence.
- `qwen_hardware/qwen-thermal/**`: APK/native-library analysis of AC020/UVC/libusb transport and calibration.
- `docs/camera-thermal.md` and `docs/hardware-map.md`: concise pre-existing hardware summaries.
- `workspace/gq5012bf1/stock/**`: extracted stock partitions, vendor ramdisk, DT and modules.

Earlier reports that say PCB routing is known are not accepted without PCB/schematic/continuity evidence. Existing software evidence can prove controller/PHY/DT topology, but not copper routing through the mainboard, board-to-board connector, daughterboard or receptacle.

## New evidence

- `evidence/stock-safe-state.txt`: slot and boot-complete gate.
- `evidence/stock-usb-dt-nodes.txt`: reproducible base-DTB + slot-A-DTBO extraction of selected USB/Type-C/thermal nodes.
- `evidence/live-usb-dt-nodes.txt`: matching selected-node extraction from the running kernel's `/sys/firmware/fdt`.
- `evidence/stock-module-metadata.txt`: hashes and `modinfo` metadata for the stock USB/TCPC/charging modules.
- `evidence/stock-module-symbols.tsv`: initial central-module import/export inventory.
- `evidence/stock-usb-module-inventory.tsv`: expanded 42-module hash/location/vermagic/dependency inventory selected from all 471 extracted modules.
- `evidence/stock-usb-module-symbols.tsv`: expanded complete imports/exports for the 42 modules.
- `evidence/stock-usb-module-strings.tsv`: reproducibly filtered USB/Type-C/charging strings.
- `evidence/stock-charger-ufcs-analysis.txt`: all-module/GKI/DT provider audit and charger-framework state disassembly.
- `evidence/stock-android-usb-services.txt`: live AIDL service and USB property state.
- `evidence/stock-udc-gadget.txt`: live UDC, configfs and negotiated gadget state.
- `evidence/stock-platform-bindings.txt`: live platform-device/driver bindings.
- `evidence/stock-usb-device-topology-idle.txt`: idle `/sys/bus/usb/devices` capture.
- `evidence/stock-typec-state.txt`: live Type-C role and revision state.
- `evidence/stock-power-usb-state.txt`: selected power-supply state.
- `evidence/stock-usb-modules.txt`: live USB/Type-C/charging module set.
- `evidence/stock-usb-dmesg-filtered.txt`: bounded USB-related kernel log capture.
- `evidence/host-external-usb-enumeration.txt`: Linux-host topology while the phone exposes ADB.
- `evidence/host-external-usb-descriptor.txt`: bounded host-side device descriptor fields.
- `evidence/thermal-camera-enumeration-log.txt`: exact High-Speed/UVC `3474:4321` enumeration lines.
- `evidence/thermal-camera-active-sysfs.txt`: active root-hub, interface and binding state.
- `evidence/thermal-camera-transition-sysfs.txt`: pre/active/Home/restored snapshots.
- `evidence/thermal-camera-capture-manifest.txt`: hashes of the deliberately uncommitted multi-megabyte raw logs.
- `evidence/stock-runtime-lowlevel.txt`: live role/extcon, interrupt and I/O-memory evidence.
- `evidence/nothing-mt6878-usb-nodes.txt`: frozen NothingOSS MT6878 controller/PHY/extcon donor excerpts and provenance.

## Reproduction

Run:

```sh
python3 usb-research/scripts/extract_stock_usb_dt.py \
  workspace/gq5012bf1/stock/vendor_boot-unpacked/dtb \
  usb-research/evidence/stock-usb-dt-nodes.txt \
  --overlay slot-b-investigation/device-dumps/dtbo_a.img
```

The extractor understands a raw FDT or the first entry of an Android DT table and emits only selected nodes, hashes and container metadata. Expanded binary inventories are reproduced with:

```sh
python3 usb-research/scripts/extract_stock_usb_module_inventory.py \
  workspace/gq5012bf1/stock \
  usb-research/evidence/stock-usb-module-inventory.tsv \
  usb-research/evidence/stock-usb-module-symbols.tsv \
  usb-research/evidence/stock-usb-module-strings.tsv

python3 usb-research/scripts/analyze_stock_ufcs.py \
  workspace/gq5012bf1/stock \
  workspace/gq5012bf1/stock/boot-unpacked/kernel \
  workspace/gq5012bf1/stock/vendor_boot-unpacked/dtb \
  usb-research/evidence/stock-charger-ufcs-analysis.txt
```

## Current checkpoint

The stock DT and live runtime already prove that `11201000.usb0` is the MTU3 dual-role controller bound by `mtu3`; its child is `11200000.xhci0`, and its sole referenced instantiated PHY is the MT6878 XS-PHY USB2 child at `11f40000`. The stock DT explicitly sets `maximum-speed = "high-speed"`; the live UDC reports both `current_speed=high-speed` and `maximum_speed=high-speed`; the connected Linux host sees the phone at `480M`.

Those facts prove the **stock configured external data path is High-Speed**. A controlled stock-app test additionally proved that the internal ThermoVue camera is direct root-port device `1-1`, USB `3474:4321`, UVC 1.10, negotiated at 480 Mbit/s through `11200000.xhci0`; external gadget/ADB disconnects while that shared path is active.

NothingOSS MT6878 source independently confirms the shipped production topology but does not prove the absence of dormant silicon IP. Whether MT6878T has package-accessible U3 hardware and whether GQ5012BF1 routes SuperSpeed pairs remain open pending primary silicon/package documentation and physical-board evidence.
