# Android 17 ↔ Ulefone vendor: first real VINTF reconciliation

> **CORRECTION (2026-10-07):** the "hwservicemanager / hidl.allocator missing" finding below applies to the
> Oct-1 collection images (system_ext.img sha256 `e72441c5…`). The system_ext_b actually flashed for the
> 2026-10-03 plain-reboot test is `4187b58a…` (hidl-fixed build), and it **does** contain `/system_ext/bin/hwservicemanager`,
> `hwservicemanager.rc` and the allocator service. The vendor inputs here are the live vendor_a files, not the
> `vendor_b` (`9f3dfe3f…`) that Slot B boots. See
> `android17-hidl-fixed-build-20261002/slot-b-logo-hang-postmortem-boundary-20261007/README.md`.


Date: 2026-10-01 · Host-only analysis · **no device was touched**: no flash, no reboot, no slot/A-B metadata change, no vbmeta/AVB change.
Slot B was not booted. Every input is either the already-committed collection
`../android17-vintf-compat-collect-20261001-010627/` or a host file whose identity to the device was verified by hash
(see `inputs-provenance.txt`).

```
CHECKVINTF_RESULT=COMPATIBLE
FATAL checkvintf incompatibilities (real device config, sku unset or dsds) : 0
Informational VINTF-level issues                                           : 140  (+161 informational neverallow diagnostics)
Runtime blocker OUTSIDE checkvintf scope (device-tree/build fix)           : 1   (hwservicemanager + HIDL allocator/memory missing from Slot-B build)
```

Model tested (as requested): **Android 17 Slot-B system + system_ext + product** against the **unmodified Ulefone
vendor + ODM** VINTF and the **real kernel `6.1.115-android14-11-g6b18f0b574ab-ab12901745`**. No vendor VINTF was
rewritten or invented.

---

## 1. Checker used

| item | value |
|---|---|
| source tree | `/mnt/SamsungSSD/android/lineage-24.0` (repo branch `lineage-24.0`, manifest `f16772cb`, AOSP default revision `refs/tags/android-17.0.0_r1`) |
| system/libvintf | `df89ad736e14ac375f61d50fa543ae7cd746a140` = tag **android-17.0.0_r1** (26Q2-release snap), 0 local modifications |
| binary | `out-android17-gsi-erofs/host/linux-x86/bin/checkvintf`, sha256 `cd1b1f52a06d0aad06c7ee7e4ce75d0f0e699910196389c2f13ce701a5421f23` |
| build action | none; the binary already existed (built 2026-09-28 17:29, newer than `check_vintf.cpp`), in the same out dir that produced the Slot-B images |
| rejected | `/mnt/SamsungSSD/LieppOS` (libvintf 25Q4-release, i.e. Android 16) |

Details: `checker-build-info.txt`.

**Defect in the Android 17 checker (reproduced):** the literal `--rootdir=<root>` command cannot work in
android-17.0.0_r1:
- `check_vintf.cpp:557` computes `dirmap` before line 583 converts `--rootdir` into a `--dirmap` argument, so line 595 aborts with `Missing --rootdir or --dirmap option` (run A, exit 64).
- `--dirmap /:<root>` also fails (run B, exit 70), because `HostFileSystem.cpp:74` matches `prefix + "/"`, i.e. `//`.

Every real run therefore uses one `--dirmap` per partition: `/system /system_ext /product /vendor /odm /apex`.

## 2. checkvintf runs (complete stdout/stderr in `checkvintf-runs/`)

| run | configuration | result |
|---|---|---|
| **C (primary)** | requested properties (`first_api_level=35`, `vendor.api_level=34`, `vndk.version=34`), `--kernel 6.1.115:kernel.config`. `ro.boot.product.hardware.sku` is **absent on the live device**, so it is unset here too | **COMPATIBLE** (exit 0, empty stderr) |
| D | C + the vendor APEX VINTF (`com.google.android.widevine` → `IDrmFactory/widevine`) | COMPATIBLE |
| E | D + `sku=dsds`, which also loads `odm/etc/vintf/manifest_dsds.xml` | COMPATIBLE |
| F | E + the full GKI release string, so the kernel level (8) comes from `android14` | COMPATIBLE |
| F_ss | F, sku=ss | COMPATIBLE |
| F_tsts / F_qsqs | F, triple/quad-SIM ODM manifests (not this hardware) | INCOMPATIBLE: `slot3/slot4/imsSlot3/se3…` not in the device FCM |
| G | F with the **stock** `fingerprint-example.xml` (`IFingerprint/virtual`) instead of the live stub | COMPATIBLE |
| N1 (control) | F with `CONFIG_ANDROID_BINDER_IPC` removed | INCOMPATIBLE: `Missing config CONFIG_ANDROID_BINDER_IPC`, which proves the kernel check is live |
| N2 (control) | F without `system/etc/vintf/compatibility_matrix.device.xml` | INCOMPATIBLE: 90 unused vendor instances + `Sepolicy version 34.0 doesn't satisify the requirements` |

The checker consulted only these properties: `apex.all.ready`, `ro.boot.product.hardware.sku` and
`ro.boot.product.vendor.sku`. The supplied `first_api_level`, `vendor.api_level` and `vndk.version` are never read
by checkvintf 17. No additional properties are needed.

**Actual checkvintf errors for this device's real configuration: none.** The only errors the real checker can be
made to emit come from configurations that are not this phone or that are deliberately broken. Each one is mapped
to the exact Ulefone component responsible:

| checker error (verbatim class) | when | responsible Ulefone component |
|---|---|---|
| `instances are in the device manifest but not specified in framework compatibility matrix` (90 instances) | only if the LieppOS device FCM is removed (N2) | `vendor/etc/vintf/manifest.xml`: 12 nonstandard `android.hardware.radio.*` instances (`imsSlotN`, `seN`), MTK `mtkradioex.*` (18), aee (3), log (5), nvram, pq_aidl, videotelephony, mdmonitor, mmagent, dmc, apmonitor, atci, audio, bluetooth.audio, camera.atms/bgservice, composer_ext.<br>Fragments: `mtk_lbs_service.xml` (22 ILbs), `gnss-mtk.xml`, `mtkgnss-batching.xml`, `power-mediatek.xml`, `mtkpower_applist-mtk-default.xml`, `manifest_isphal.xml`, `manifest_mmlpq.xml`, `manifest_apuware_*`, `em_hal_service.xml`, `CommandService.xml` (netdagent), `arm.mali.platform-mediatek.xml`, and the Ulefone `vendor.yft.*` set (`manifest_changenode.xml`, `manifest_gesturewake.xml`, `manifest_obtain_vendor.xml`, `manifest_tinylcd.xml`, `sensorcali_manifest_v1/v2.xml`).<br>The ODM `manifest_dsds.xml` duplicates the radio entries. Full per-instance list: `hal-vintf-reconciliation.txt` (VENDOR-ONLY); it is set-identical to N2's output. |
| `Sepolicy version 34.0 doesn't satisify the requirements` | only if the device FCM is removed (N2) | Ulefone vendor `<sepolicy><version>34.0`. It is accepted because the A17 build writes the `PLATFORM_SEPOLICY_COMPAT_VERSIONS` list into `compatibility_matrix.device.xml` |
| `IRadio*/slot3|slot4|imsSlot3|se3…` unused | sku=tsts / qsqs | `odm/etc/vintf/manifest_tsts.xml` / `manifest_qsqs.xml`. These are the wrong SKU for this DSDS phone and are never selected |
| `Missing config CONFIG_ANDROID_BINDER_IPC` | N1 (synthetic) | n/a, control only |

## 3. Answers

**1. Does Android 17 FCM 8 accept the Ulefone 6.1.115 kernel family?** Yes.
- `compatibility_matrix.8.xml` has **11** `<kernel version="6.1.0" level="8">` blocks: 1 unconditional and 10 conditional.
- 7 of them apply to this kernel: the unconditional block plus ARM64, ACPI=n, EXT4, F2FS, VMAP_STACK/!KASAN_SW_TAGS and AUTO_VAR_INIT_ZERO.
- That gives **282 applicable CONFIG requirements, 282 PASS, 0 FAIL**.
- The kernel FCM level is 8 from both the GKI release (`android14`) and the vendor `target-level`. The minimum LTS is 6.1.0 ≤ 6.1.115.
- The real checker agrees (runs C–G) and genuinely evaluates configs (N1).
- Per-config table: `kernel-vintf-config-reconciliation.txt`.

**2. Which kernel CONFIG requirements fail?** **None.** Only conditional blocks that don't apply would fail:
- ARM32 `CONFIG_AEABI`
- x86 `CONFIG_PAGE_TABLE_ISOLATION` and `CONFIG_RETPOLINE`
- the `CONFIG_OF=n` block's `CONFIG_ACPI`

libvintf correctly does not enforce these.

**3. Which HAL requirements fail?** **None.**
- All **151** device-manifest instances (vendor + fragments + ODM dsds + vendor APEX) match a framework matrix: **61** via AOSP FCMs and **90** only via `device/ulefone/gq5012bf1/vintf/framework_compatibility_matrix.xml`.
- Results: 0 EXTRA VENDOR HAL, 0 vendor-side VERSION/INSTANCE MISMATCH, 0 TRANSPORT MISMATCH, 0 deprecated.

**4. Fatal vs informational.** These rules come from the libvintf 17 source:
- **Fatal:** vendor instances that no FCM declares (`checkUnusedHals`), deprecated vendor HAL versions (`checkDeprecation`), sepolicy/vendor-ndk/system-sdk/kernel mismatch. **Count: 0.**
- **Informational:** FCM HALs the vendor lacks. libvintf 17 doesn't even parse `optional=`, so no FCM HAL is required.
  - 88 FRAMEWORK-ONLY (e.g. AIDL `audio.core`, `authsecret`, `weaver`, `secretkeeper`, `security.see.*`)
  - 19 MISSING FROM VENDOR (e.g. `keymint/strongbox`, `IRemotelyProvisionedComponent/widevine`, `face/virtual`, `media.c2 IComponentStore/software`, radio `slot3`)
  - 22 VERSION MISMATCH: only newer FCM levels (202404–202604) want newer versions of `composer3`(v2), `health`(v2), `power`(v4), `radio.*`(v1/v2), `thermal`(v1) and `wifi`/`hostapd`/`supplicant`. All are accepted by FCM 8.
- **Also informational:** the framework HALs that the vendor DCM asks for are not checked by libvintf. `android.hidl.allocator@1.0` is *not* in the A17 framework manifest; MTK `mtksf_ext` and `mbrainj` are `optional=true` and absent.

**5. Does vendor target-level=8 remain usable with Android 17?** Yes.
- A17 still installs FCM 7 and 8 (`SYSTEM_MATRIX_DEPS_A17`).
- `max-level="8"` framework HALs (`hidl.manager`, `hidl.token`, `hidl.memory`, `sensorservice@1.0`, `media.c2@1.2` software) remain advertised for a level-8 device.

**6. Does vendor API level 34 remain usable?** Yes.
- `<vendor-ndk>34` is satisfied by the A17 `system_ext` manifest.
- `com.android.vndk.v34.apex` is shipped (`PRODUCT_EXTRA_VNDK_VERSIONS := 34`).
- Sepolicy 34.0 is accepted.
- No libvintf 17 code reads `ro.vendor.api_level`. See `vndk-vendor-api-reconciliation.txt`.

**7. Does the old VNDK/vendor interface cause any actual checkvintf failure?** **No.** `checkVendorNdkCompatibility` gets version 34 == 34 and the DCM lists no libraries.

**8. Does SELinux create an actual incompatibility?** **No.** This is backed by a real compile, not just the matrix list:
- Vendor `plat_sepolicy_vers.txt` is 34.0. `plat_pub_versioned.cil` uses only the `_34_0` suffix (17,899 occurrences).
- A17 ships `mapping/34.0.cil` + `34.0.compat.cil` in system, system_ext and product, plus 31.0–33.0 and 202404/202504/202604.
- The vendor precompiled-policy hashes ≠ the A17 hashes, so init compiles the split policy. **I replicated `LoadSplitPolicy` exactly with the A17 host `secilc`: exit 0** (compiled policy sha256 in `selinux-compile/`).
- Genfs: there is no vendor `genfs_labels_version.txt`, so the version defaults to 202404. A missing `plat_sepolicy_genfs_202404.cil` is legal (only ≥202504 is fatal).
- Without `-N`, which init never uses, secilc reports 161 neverallow violations. They are informational CTS-level diagnostics. The four groups below sum to 161:
  - 113: frozen Android 14 neverallows in the vendor `plat_pub_versioned.cil`, tripped by new A17 platform/system_ext rules
  - 39: A17 platform neverallows tripped by MTK `vendor_sepolicy.cil` rules
  - 5: A17-internal rules (`virtual_face`/`virtual_fingerprint`/`overlay_remounter`/`crosvm`) colliding with vendor-assigned attributes
  - 4: vendor `vendor_sepolicy.cil` neverallows tripped by A17 rules

  20 of the 161 involve userdebug `su`. See `selinux-vintf-reconciliation.txt`.

**9. Exact changes required in the LieppOS device tree (`device/ulefone/gq5012bf1`)**
1. **Keep** `vintf/framework_compatibility_matrix.xml` (sha256 `f2a6e50c…`, 47 HAL groups / 90 instances) and the `DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE +=` line. It is *mandatory*: without it, checkvintf is INCOMPATIBLE (N2). No change to it is needed.
2. **Add to `device.mk`** (this is NOT a checkvintf error, but it is the only actionable defect found):
   ```make
   # Ulefone vendor is HIDL-based (target-level 8). base_system_ext.mk installs these only when
   # PRODUCT_SHIPPING_API_LEVEL <= 34; we ship 35, so they were silently dropped.
   PRODUCT_PACKAGES += \
       hwservicemanager \
       android.hidl.allocator@1.0-service \
       android.hidl.memory@1.0-impl
   ```
   Evidence (exact flashed images, `fsck.erofs` extraction):
   - `/system/bin/hwservicemanager` is a symlink to `/system/system_ext/bin/hwservicemanager`, which **does not exist**.
   - There is no `hwservicemanager.rc`, no allocator service and no `hw/android.hidl.memory@1.0-impl.so`.
   - libhwbinder `Utils.cpp:31` (`access()` follows the dangling link) then reports HIDL as *unsupported*, so libhidl takes the `NoHwServiceManager` path. All **13** vendor hwbinder HALs fail to register:
     - `audio@7.1` and `audio.effect@7.0`: the only audio HAL
     - `bluetooth@1.1`
     - `media.c2@1.2`: the MTK HW codecs
     - `mtk aee@1.1` ×2 and `mtk bluetooth.audio@2.2`
     - `yft changenode`, `gesturewake`, `obtainvendor`, `sensorcali@1.0/2.0`, `tinylcd`
   - libaudiohal's HIDL effect path also needs `IAllocator/ashmem`.
   - checkvintf cannot see any of this, because the static `system_ext` manifest still advertises `hidl.manager@1.2` and `hidl.token`.

   Keep `PRODUCT_SHIPPING_API_LEVEL := 35`; it matches the stock vendor `ro.product.first_api_level=35`.
3. No other device-tree change is needed for VINTF. `PRODUCT_EXTRA_VNDK_VERSIONS := 34` stays.

**10. Problems that require vendor blobs:** none for Android 17 at target-level 8. The following become vendor-blob problems *only if* the device target-level were raised above 8:
- the HIDL HALs: audio 7.1, bluetooth 1.1, media.c2 1.2 and the yft/MTK HIDL
- `composer3` v2, `health` v2, `power` v4, `thermal` v1, `radio` v1/v2, `wifi`
- missing strongbox and AIDL `audio.core`

The 39 vendor-side neverallow violations can only be fixed in vendor policy, and they are not boot-relevant.

**11. Problems that require kernel changes:** none. All 282 applicable FCM 8 / 6.1 requirements pass.

**12. Problems that need only framework/device-tree changes:**
- (a) the missing `hwservicemanager` / `android.hidl.allocator@1.0-service` / `android.hidl.memory@1.0-impl`
- (b) the 90 nonstandard vendor instances. Already solved by the device FCM; keep it.
- (c) the checker invocation must use per-partition `--dirmap`. This is tooling only.

**13. Impossible without replacing vendor components:** nothing is impossible for Android 17 at FCM 8. Out of reach with this vendor:
- moving the device to FCM ≥ 202404
- AIDL audio (`audio.core`)
- strongbox KeyMint
- clearing the vendor-side neverallow/CTS violations

## 4. Other observations
- The live `/vendor/etc/vintf/manifest/fingerprint-example.xml` is an empty `<manifest/>`, while stock declares `IFingerprint/virtual`. Both are COMPATIBLE (C vs G).
- The vendor manifest declares no real fingerprint HAL instance.
- The A17 `system_ext` ships `com.android.hardware.biometrics.fingerprint.virtual.apex` with no VINTF fragment.
- `ro.boot.product.hardware.sku` is absent live, so libvintf never loads `odm/etc/vintf/manifest_*.xml`. The vendor manifest itself already carries the DSDS radio instances (built from `manifest_dsds.xml`), so both choices are COMPATIBLE.
- Not checked on host by design:
  - AVB (`CheckFlags::DEFAULT` disables it). Live `ro.boot.avb_version=1.2` satisfies `<vbmeta-version>1.0`.
  - kernel-sepolicy-version ≥ 30 (Linux 6.1 max is 33; live `/sys/fs/selinux/policyvers` was not collected).
- Provenance limitation: live `/vendor/etc/selinux` was not collected. The stock extraction's vendor fingerprint is identical to the live one.

## 5. Exact next engineering steps
1. `device/ulefone/gq5012bf1/device.mk`: add the three `PRODUCT_PACKAGES` from §3.9, plus the same lines in the research `device-tree/` copy.
2. Host build only (`m systemimage systemextimage productimage` in `lineage-24.0`, out dir `out-android17-gsi-erofs`). No flashing.
3. Verify the new images with `fsck.erofs --extract`:
   - `/system_ext/bin/hwservicemanager`
   - `/system_ext/etc/init/hwservicemanager.rc`
   - `android.hidl.allocator@1.0-service` + its rc + VINTF fragment (`max-level=8`)
   - `system_ext/lib64/hw/android.hidl.memory@1.0-impl.so`
4. Re-run `scripts/run.sh` with the per-partition `--dirmap` set on the new images (expect COMPATIBLE; the framework manifest gains `hidl.allocator`). Re-run the `secilc` split-policy compile (expect exit 0).
5. Read-only device collection to close the gaps: `/vendor/etc/selinux/*` sha256, `/sys/fs/selinux/policyvers`, and the mount source of the stubbed `fingerprint-example.xml`.
6. Only after that, re-stage Slot B under the existing staging/readback procedure (separate, explicitly authorized step). Plan first-boot log capture for `hwservicemanager`, `servicemanager: ... not declared in VINTF`, and `avc: denied` against MTK domains.

## Files
| file | content |
|---|---|
| `CHECKVINTF-RESULT.txt` | verdict, primary command, all runs, complete primary stdout/stderr |
| `kernel-vintf-config-reconciliation.txt` | every CONFIG of all 11 `6.1.0 level=8` blocks: required / actual / PASS-FAIL |
| `hal-vintf-reconciliation.txt` | 151 vendor instances + framework-side inventory, classified; focus areas; DCM vs framework manifest |
| `selinux-vintf-reconciliation.txt` | versions, mappings, precompiled-hash logic, real split-policy compile, neverallow classification |
| `vndk-vendor-api-reconciliation.txt` | vendor-ndk/system-sdk, VNDK v34 apex, target-level 8, HIDL runtime gap |
| `vintf-xml-requirements.txt` | step 2: verbatim XML blocks (all kernel blocks, sepolicy, vendor-ndk, system-sdk, Lineage FCM) |
| `checker-build-info.txt` | source tree, tags, binary path/sha256, `--help` |
| `inputs-provenance.txt` | sha256 of every input; image ↔ Slot-B readback identity |
| `checkvintf-runs/` | stdout/stderr/exit of runs A–N2, exact commands, vendor-APEX VINTF used |
| `selinux-compile/` | secilc command lines, outputs, neverallow classification |
| `scripts/` | `analyze.py` (libvintf-semantics itemizer), `run.sh`, `env.sh` |
| `TERMINAL.txt` | session log |
