# Phase 4 — `yft_devinfo.ko` reconstruction

Final classification:

    STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION
      + BLOCKED_WITH_EXACT_MISSING_EVIDENCE
        scoped to one 73-character vendor enum type text
        that shifts the ten *_device_add() export CRCs

Complete, buildable source for the whole provider now exists and builds
`BUILD_RC=0` against exact Google GKI 12901745. 17 of 27 export MODVERSION
CRCs and **all 40** import CRCs reproduce from source; the remaining 10 are
reduced to a single, precisely measured missing token.

---

## Oracle

| | |
|---|---|
| path A | `$RESEARCH/workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/yft_devinfo.ko` |
| path B | `$RESEARCH/workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/yft_devinfo.ko` |
| SHA256 | `0d5e547e3e6c313c88695b2c8f9aae04398e3c8822f16d57dff6aea011f821fe` (both, re-verified) |
| size | 98048 bytes |
| build-id | `f0e674a14c253aafb0589a8305042d7922965adb` |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| compiler | Android clang 17.0.2 (r487747c, `+pgo +bolt +lto`) |
| name / description / author / license | `yft_devinfo` / `YFT DEVICE INFO` / `Jay Zhou` / `GPL` |
| depends | *(empty)* |
| srcversion / parameters / aliases | none |

Full identity dump: `workspace/phase4-yft-devinfo/stock-oracle.txt`.

## Provenance

**No donor.** `yft_devinfo` and its private header exist in no local tree and
no public repository; every ODM "devinfo"/"hardware_info" driver found was
explicitly rejected as unrelated. One *partial* donor was found and used: the
MediaTek sensor-2.0 header `hf_sensor_io.h` (from the local `nothing-mt6878`
tree) supplies `struct sensor_info`, which MODVERSION arithmetic then confirms
byte-exactly. See `workspace/phase4-yft-devinfo/yft-devinfo-source-candidates.md`.

The reconstruction is therefore driven entirely by RED of the stock binary:
`workspace/phase4-yft-devinfo/RED.md`.

## Build

```
cd $GKI_WS
tools/bazel build //lieppos/yft-devinfo-recon:yft_devinfo_gki
```

* `BUILD_RC=0`
* warnings: none from the module (only the harmless kleaf
  `sign-file: certs/signing_key.pem` BoringSSL notice)
* sources: `lieppos/yft-devinfo-recon/{yft_devinfo.c, hf_sensor_io.h,
  yft_devinfo.h, Makefile, BUILD.bazel}`
* the GKI core was not modified.

## Functions

| metric | value |
|---|---|
| stock functions | 72 |
| rebuilt functions | 72 |
| present in both | 72 / 72 |
| size-identical | 37 |
| byte-identical | 34 |
| identical external call sequence | **69 / 72** |
| unexplained | **0** |

The three call-sequence deltas are all inlining/tail-merging decisions with
identical behaviour:

| function | delta | cause |
|---|---|---|
| `c_cts_show` | 32 → 64 | clang inlined `yft_cts_dump()` into the seq `show` callback; stock kept the call |
| `yft_camera_device_add` | 664 → 620 | clang tail-merged the two identical `"cam_alloc type info failed ~~~~ \n"` `printk` sites that stock emitted twice |
| `yft_devices_probe` | 576 → 740 | clang inlined `proc_yftinfo_init()` (still emitted out-of-line, as stock) and fully unrolled the sysfs rollback loop |

The remaining size-only deltas are a uniform ±4 bytes on the small per-type
helpers (register allocation / loop rotation around the shared type-lookup
walk). Evidence: `workspace/phase4-yft-devinfo/yft-devinfo-verification.txt`
and `yft-devinfo-callseq-compare.txt`.

## Data

| object | stock | rebuilt |
|---|---|---|
| `touch_fw_version` | `char[30]`, `.data..read_mostly`, GPL | identical |
| `second_touch_fw_version` | `char[30]`, `.data..read_mostly`, GPL | identical |
| `fuelgauge_fw_version` | `char[30]`, `.data..read_mostly`, GPL | identical |
| `tinylcd_fw_version` | `char[30]`, `.data..read_mostly`, GPL | identical |
| `Cust_emmc_support` | `char[9][50]`, `.data` | identical |
| `CUSTOM_MODEM` | `char[123]`, `.data` | identical |
| `yft_device_of_match` | `struct of_device_id[2]`, 400 B | identical |
| `yft_devices_driver` | `struct platform_driver`, 248 B | identical |
| `mt_sysfs_attributes` / `mt_sysfs_class_attributes` | 40 B `.rodata` / 64 B `.data` | identical |
| `yftinfo_op`/`memoryinfo_op`/`ctsinfo_op` | 32 B each, `.rodata` | identical |
| `proc_*_operations` | 96 B each, `.rodata` | identical |
| `yft_urxdo_flag`, `yft_devices`, `yftdisp_info_list`, `yftdebug`, `yft_sar_name_buf` | `.bss` | identical sizes and sections |

Objects: **42 stock / 42 rebuilt**, all matching in size and section. The only
two object-level differences are pure build provenance:
`__UNIQUE_ID_vermagic333` (87 vs 85 bytes — the vermagic string differs
because the rebuild is not the vendor CI build) and the lockdep-key counter
suffix `yft_devices_probe.__key.119` vs `.113`.

State objects and per-instance layouts (`struct yft_device_type_info`,
`yft_device_info`, `yft_camera_dev_info`, `yft_sensor_dev_info`) are documented
in `RED.md` §2 and reproduced field-for-field.

## ABI

### Imports

| | |
|---|---|
| stock imports | 40 |
| rebuilt imports | 40 |
| symbol-set difference | **none** |
| import CRC mismatches | **0** |

All 40 resolve against `//common:kernel_aarch64` with matching CRCs — the
module has no vendor-module dependencies (`depends=`), confirmed by
`workspace/phase4-yft-devinfo/yft-devinfo-providers.tsv`.

### Exports

| | |
|---|---|
| stock exports | 27 (23 `EXPORT_SYMBOL`, 4 `EXPORT_SYMBOL_GPL`) |
| rebuilt exports | 27, same names, same licences, same kinds, same sizes for all 17 CRC-matching entries |
| export CRC matches | **17** |
| export CRC gaps | 10 (all `*_device_add`) |

Reproduced from source, never patched:

```
touch_fw_version                 0xd0815107  ✔
second_touch_fw_version          0x7198d58d  ✔
tinylcd_fw_version               0x36887f32  ✔
fuelgauge_fw_version             0x8c280260  ✔
yft_set_touch_device_used        0x0a0f3b69  ✔
yft_set_camera_device_used       0x8a60f3de  ✔
yft_set_accsensor_device_used    0x306523b3  ✔
yft_set_msensor_device_used      0x8f1e4776  ✔
yft_set_alspssensor_device_used  0x1d2717e5  ✔
yft_set_sarsensor_device_used    0xbc6d2dd0  ✔
yft_set_barosensor_device_used   0x4af62c4f  ✔
yft_set_fuelgauge_device_used    0x82093a2e  ✔
yft_set_tinylcd_device_used      0x25e94db4  ✔
yft_device_dump                  0xe1138f49  ✔
yft_memory_dump                  0xe3ba6000  ✔
yft_cts_dump                     0x9afec595  ✔
is_yft_cts_board                 0xad70697b  ✔
```

Remaining gaps (`yft_camera_device_add`, `yft_touchpanel_device_add`,
`yft_spitouchpanel_device_add`, `yft_accsensor_device_add`,
`yft_msensor_device_add`, `yft_alspssensor_device_add`,
`yft_sarsensor_device_add`, `yft_barosensor_device_add`,
`yft_fuelgauge_device_add`, `yft_tinylcd_device_add`) — see *Remaining
differences*. Per-symbol table:
`workspace/phase4-yft-devinfo/yft-devinfo-abi-comparison.tsv`.

Note `yft_spitouchpanel_device_add` was on the task's required list and is
**not** reproduced; the exact missing evidence is stated below.

## Consumers

Complete list, from re-scanning all **471** stock module paths
(`workspace/phase4-yft-devinfo/yft-devinfo-consumers.tsv`, 25 import edges):

| consumer | symbols |
|---|---|
| `focaltech_touch_spi_ft3680.ko` | `touch_fw_version`, `yft_spitouchpanel_device_add`, `yft_set_touch_device_used` |
| `hynitron.ko` | `second_touch_fw_version`, `yft_touchpanel_device_add`, `yft_set_touch_device_used` |
| `hf_manager.ko` | `yft_{acc,m,alsps,sar,baro}sensor_device_add` + `yft_set_{acc,m,alsps,sar,baro}sensor_device_used` |
| `imgsensor.ko` | `yft_camera_device_add`, `yft_set_camera_device_used`, `is_yft_cts_board` |
| `sh366003_fg.ko` | `fuelgauge_fw_version`, `yft_fuelgauge_device_add`, `yft_set_fuelgauge_device_used` |
| `spi_tiny_co5300_lcd.ko` | `yft_tinylcd_device_add`, `yft_set_tinylcd_device_used` |
| `aw36518.ko` | `is_yft_cts_board` |

The task's assumption that only FT3680 and Hynitron consume this module was
wrong: it is a nine-class device registry shared by touch, camera, sensors,
fuel gauge, secondary LCD and the flash LED driver.

## Interfaces / behavior

* **Device-info behaviour** — a platform driver bound to
  `mediatek,yft_devices` maintaining a registry of nine device *types*
  (ids 12..20), each with a list of instances and a pair of
  `info_print`/`set_used` callbacks; instances are added by the consumers at
  their own `module_init`/probe time.
* **Touch selection behaviour** — `yft_touchpanel_info_print()` compares the
  registered instance name against `"hyn_ts"`; a match reports
  `second_touch_fw_version`, everything else reports `touch_fw_version`. This
  is exactly how the FocalTech and Hynitron panels are distinguished.
  `yft_set_*_device_used()` dispatches through the registered callback pointer
  (KCFI type id `0x4d9b0091`), walks the whole type list and always returns 0.
* **Userspace/kernel ABI** —
  `/proc/yftinfo`, `/proc/yftmeminfo`, `/proc/yftctsinfo` (all 0666, one
  seq record each);
  platform-device sysfs `yft_cts_flag`, `yft_sar_name`, `secure_boot`,
  `ufs_lifetime` (0444);
  class `yft_device` with `yft_fm_switch` (0444);
  `/chosen` bootargs consumed: `lcmname=`, `yft_ext_lcmname=`,
  `lpddr_used_name=`, `lpddr_used_index=`, `flash_type=`,
  `yft_boot_secureboot=`, `PreEOLInfo =`;
  DT GPIO `urxdo_gpio_select` → `is_yft_cts_board()`.
* **Faithfully reproduced stock defects** — the duplicate-name path in every
  `*_device_add()` `kfree()`s a still-linked instance; `yft_camera_device_add()`
  null-checks the *type* pointer instead of the newly allocated instance; both
  mutexes are created and never locked (`mutex_lock` is not even imported);
  `yft_devices_remove()` frees nothing.

## Remaining differences

Exact, bounded list.

1. **`ABI_PROVENANCE_GAP` — the ten `*_device_add()` export CRCs.**
   The second parameter of every one of them is a vendor enum from the
   never-shipped `yft_devinfo.h`. Proven by CRC-32 zero-shift analysis
   (`lieppos/yft-devinfo-recon/tools/crcshift.py`): the stock parameter tail is
   exactly **70 characters longer** than the reconstruction's `" , int ) "` in
   the i2c family *and* in the spi family, i.e. the type text is exactly
   **73 characters**. Substituting one 73-character string into the
   reconstruction's own genksyms expansions reproduces **all ten** stock CRCs
   at once — which simultaneously proves that the return types (`int`), the
   first-parameter types (`char *`, `struct i2c_driver *`, `struct spi_driver *`,
   `struct sensor_info *`) and the 194-character `struct sensor_info` body are
   already byte-exact.
   *Missing evidence, stated exactly*: the 73-character spelling
   `enum <tag> { <A> = <v> , <B> = <v> }`. Identifier spellings survive in no
   shipped artifact. Excluded by exhaustion: 409,061,884 semantically
   plausible spellings (`tools/yft-t2-semantic.py`) and 56,495 real enum
   definitions harvested from every available kernel/vendor tree
   (`tools/yft-t2-treescan.py`). Closing this needs the vendor header (or any
   Ulefone/YFT BSP drop containing it) — nothing else.
   No CRC was patched and no fabricated declaration was committed.
2. **`COMPILER_CODEGEN_ONLY`** — the three inlining/tail-merging deltas listed
   under *Functions*, plus a uniform ±4-byte drift on the small per-type
   helpers. Call sequences and behaviour are identical.
3. **`BUILD_PROVENANCE`** — `vermagic` (and hence
   `__UNIQUE_ID_vermagic333` size), build-id, `.comment`, and the
   `__UNIQUE_ID`/`__key` counter suffixes. `.llvm_addrsig` is present in stock
   and absent in the rebuild (LTO/bolt pipeline difference).
4. **`BEHAVIORAL_DIFFERENCE`** — none.
5. **`UNKNOWN`** — none. All 72 functions, 42 objects, 40 imports and 27
   exports are accounted for.

## Downstream: FT3680 rebuild

`//lieppos/focaltech-ft3680-recon/recon:focaltech_touch_spi_ft3680_gki`
rebuilt with the generated provider `Module.symvers` wired in — `BUILD_RC=0`.

While doing so a **pre-existing defect** in the FT3680 harness was found and
fixed: its `Makefile` computed `KBUILD_EXTRA_SYMBOLS` inside the
`ifneq ($(KERNELRELEASE),)` branch but forwarded it from the outer branch, so
it was always empty. As a result *no* vendor provider had ever actually been
resolved for FT3680.

The FT3680 placeholder declarations were also wrong and are now replaced by the
recovered API (`yft_devinfo.h`), matching the stock call sites
(`yft_spitouchpanel_device_add(&fts_ts_spi_driver, 0)`,
`yft_set_touch_device_used("fts_ts", 1)`).

Unresolved provider symbols that disappeared (were "undefined!" with no
MODVERSION, now fully resolved):

```
yft_spitouchpanel_device_add     <- yft_devinfo      (this work)
yft_set_touch_device_used        <- yft_devinfo      (this work)
mtk_disp_notifier_register       <- mtk_disp_notify  (fixed by the Makefile fix)
mtk_disp_notifier_unregister     <- mtk_disp_notify  (fixed by the Makefile fix)
```

FT3680 now has **0** undefined symbols without a MODVERSION (was 4), and its
`.modinfo` records `depends=mtk_disp_notify,yft_devinfo`.

Import CRCs in the rebuilt FT3680 vs stock:

| symbol | stock | rebuilt | |
|---|---|---|---|
| `yft_set_touch_device_used` | `0x0a0f3b69` | `0x0a0f3b69` | ✔ |
| `mtk_disp_notifier_register` | `0x4c353ac0` | `0x4c353ac0` | ✔ |
| `mtk_disp_notifier_unregister` | `0xa11ab00a` | `0xa11ab00a` | ✔ |
| `yft_spitouchpanel_device_add` | `0xea3d7f0d` | `0x0776e449` | gap #1 above |
| `touch_fw_version` | `0xd0815107` | not referenced | FT3680-side gap (see below) |

Two FT3680-side items remain and are **not** provider problems:

* `touch_fw_version` is not yet referenced because the FT3680 reconstruction
  does not implement `fts_fwupg_work()` (stock does
  `sprintf(touch_fw_version, "Vno:0x%02x\n", fw_ver)` there). The provider
  exports it with the exact stock CRC `0xd0815107`, so it will resolve
  correctly the moment FT3680 grows that call site.
* stock FT3680 depends on `yft_tpd_gesture` as well; the reconstruction does
  not yet reference it.

Therefore: **FT3680's `yft_devinfo` dependencies are not all solved** — 2 of
the 3 expected symbols are now resolved and CRC-exact for one of them, the
third is blocked on gap #1, and `touch_fw_version` is blocked on FT3680's own
firmware-upgrade path.

### Hynitron

No Hynitron source or reconstruction exists in the workspace
(`lieppos/` contains no `hynitron` target and no source was found in any
searched tree), so it could not be rebuilt against the provider. Its ABI
expectations were still verified statically from the stock binary: it imports
`second_touch_fw_version` (`0x7198d58d`, reproduced ✔),
`yft_set_touch_device_used` (`0x0a0f3b69`, reproduced ✔) and
`yft_touchpanel_device_add` (`0xf5ba4446`, gap #1), and registers under the
name `hyn_ts`, which is exactly the literal the provider's
`yft_touchpanel_info_print()` tests for.

## Artifacts

Under `workspace/phase4-yft-devinfo/`:

`stock-oracle.txt`, `RED.md`, `yft-devinfo-stock-inventory.md`,
`yft-devinfo-source-candidates.md`, `yft-devinfo-sections.tsv`,
`yft-devinfo-functions.tsv`, `yft-devinfo-objects.tsv`,
`yft-devinfo-imports.tsv`, `yft-devinfo-exports.tsv`,
`yft-devinfo-relocs.tsv`, `yft-devinfo-strings.txt`,
`yft-devinfo-disasm.txt`, `yft-devinfo-disasm-annotated.txt`,
`yft-devinfo-consumers.tsv`, `yft-devinfo-providers.tsv`,
`yft-devinfo-abi-comparison.tsv`, `yft-devinfo-verification.txt`,
`yft-devinfo-callseq-compare.txt`, plus a copy of the reconstruction sources.

Under `$GKI_WS/lieppos/yft-devinfo-recon/`: `yft_devinfo.c`, `yft_devinfo.h`,
`hf_sensor_io.h`, `Makefile`, `BUILD.bazel` and `tools/` (`elfmini.py`,
`yft-analyze-stock.py`, `yft-compare.py`, `yft-callseq.py`, `crcshift.py`,
`yft-genksyms.sh`, `yft-t2-search.py`, `yft-t2-semantic.py`,
`yft-t2-treescan.py`).

## Safety

Offline binary/source analysis only. Nothing was flashed, inserted, bound or
modified on the phone; no DT/DTBO, partition or slot was touched.
