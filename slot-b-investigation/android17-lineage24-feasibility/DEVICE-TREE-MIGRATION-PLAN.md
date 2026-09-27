# From generic Android 17 proof to `gq5012bf1`

The GSI is a proof vehicle, not the final LieppOS product.

## Phase 1 — generic userspace proof

Build official `lineage_gsi_arm64` with EROFS and validate it through isolated
DSU userdata. Use it only to identify framework/vendor/kernel incompatibilities.
Do not carry the SDK35 property, DB, insecure-ADB or Google-removal hacks.

## Phase 2 — proper product tree

### `device/ulefone/gq5012bf1`

Own:

- `AndroidProducts.mk`, `lineage_gq5012bf1.mk`, BoardConfig and release config;
- exact existing logical extents, EROFS settings and dynamic-partition groups;
- shipping API **35** (stock fact), vendor API/FCM 8 compatibility and sepolicy;
- fstab/init/uevent/property contexts, resource overlays and permissions;
- VINTF assembly, audio/media/camera/sensor/power/thermal/NFC configurations;
- AVB algorithms, public-key references and descriptor ownership (never private
  keys in source);
- independent system/system_ext/product output, not the folded GSI layout.

### `vendor/ulefone/gq5012bf1`

Generate from the evidence-selected stock recipe. Existing research already has:

- 1,891 reviewed paths; 1,891/1,891 offline extraction;
- about 1 GB source payload, 1,583 exact copies and 21 presigned APK imports;
- 205 AOSP-produced replacement paths and 38 owning AOSP modules;
- zero unresolved required first-order/transitive ELF dependencies;
- vendor/odm VINTF, init, firmware, configs and vendor-DLKM inventory.

Port the extraction scripts to current Lineage 24 extract-utils and re-run all
path/module/ELF audits. Do not copy stock odex/vdex/art or build properties.
Redistribution remains a separate legal decision.

### `kernel/ulefone/...`

Initial device builds should retain the proven stock 6.1 boot/vendor_boot and
DLKM stack. The repository already records exact GKI source identity, KMI/CRC
maps, module load order, DT matching and reconstructed missing modules. A later
production kernel track should move the exact GKI/device modules into a clean
kernel/device-modules build without changing ABI blindly.

### `hardware/mediatek/...` and MTK sepolicy

Add official Lineage `lineage-24.0` MediaTek common hardware and
`device/mediatek/sepolicy_vndr` only where the Ulefone contracts require them.
Use the Galaxian MT6878 tree as source-layout/reference for common MTK services,
IMS and compatibility components; do not import Nothing blobs, DT, tuning or
partition values.

### framework/system compatibility layers

Keep compatibility code minimal and evidence-driven: source-built shim libraries
for proven missing symbols, MTK framework/IMS clients required by vendor AIDL,
correct system-server/bootclasspath declarations and release-native overlays.
Every shim needs a captured failure and an owner/removal plan.

## Existing research inputs

| Input | Use in source tree |
|---|---|
| `docs/partition-map.md` | BoardConfig extents/groups/filesystems |
| `docs/hal-map.md`, `docs/service-map.md` | VINTF, packages and init services |
| `docs/blob-map.md`, `docs/elf-closure.md` | proprietary recipe and dependency gates |
| `docs/module-map.md`, `docs/dt-module-matching.md` | boot/vendor/system DLKM and load order |
| audio/camera/thermal/connectivity/sensors/NFC docs | configs, overlays and test matrix |
| `kernel/exact-*`, KMI/CRC reports | kernel identity and module ABI |
| stock manifest/matrix and trusted snapshots | FCM 8, sepolicy 34, runtime topology |
| current B parity reports | exact EROFS/AVB construction controls |

## Shortest path

1. Add storage and build/measure the official GSI.
2. Validate Android17 via DSU isolated userdata.
3. Fork a clean Lineage24 device/vendor tree from the existing generated
   evidence, not from old diagnostic images.
4. Build independent EROFS partitions and reduce by measured package ownership.
5. Produce a coherent flags-0 AVB chain and host `checkvintf` result.
6. Only then seek authorization for a B-only first boot.

**BLOCKER:** no Lineage24 `gq5012bf1` product exists yet. **TEST TO CONFIRM:**
full target-files build, VINTF/SELinux/ELF audits and hardware boot.
