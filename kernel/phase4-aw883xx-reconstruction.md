# Phase 4 — Awinic AW883xx Smart-PA reconstruction (authoritative report)

Target: `vendor_dlkm/lib/modules/aw883xx_driver.ko` on the Ulefone GQ5012BF1
(Armor 34 Pro, MT6878).

This report supersedes the `NEEDS_ULEFONE_PORT` classification carried for this
module in `kernel/stock-module-master.csv` and `kernel/phase4-buildability-plan.md`.

## Final classification

```
SOURCE_DELTA_RECONSTRUCTION_EXACT
STOCK_BEHAVIOR_RECONSTRUCTED
SYMBOL_SET_PARITY_EXACT      imports 73/73, functions 236/236, 0 extra, 0 missing
ABI_PARITY_EXACT             __versions 74/74 byte-identical, __kcrctab byte-identical
CODE_PARITY_235_OF_236_BYTE_IDENTICAL
SEMANTIC_PARITY_236_OF_236   0 functions differ in relocation/call/string multiset
DATA_PARITY_EXACT            .rodata/.bss identical, .data non-relocated bytes identical
SAFE_RUNTIME_VARIANT_AVAILABLE (calibration + factory-debug writes gateable, stock-on by default)
```

No CRC was fabricated. No register meaning, calibration constant or DSP command
was invented. No amplifier write, no calibration run and no phone/partition
modification happened at any point — the entire task was static analysis plus
host builds.

---

## 1. Oracle

```
path    workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/aw883xx_driver.ko
        (byte-identical copy also in vendor_ulefone_gq5012bf1/proprietary/…)
sha256  3bc4722c6550abb9cfd75d06602c2a1bff8d0b6af58708324479ef6a0d22c9b4
size    331808
vermagic 6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
name    aw883xx_driver     description "ASoC AW883XX Smart PA Driver"     license GPL v2
depends (none)             alias      (none)
```

The `g945dff7bc1bf` vermagic is the vendor's own 6.1.115 build hash and is
shared by every Ulefone vendor_dlkm module; the ABI it was linked against is
byte-for-byte the Google GKI `ab/12901745` KMI (all 74 `__versions` CRCs match —
see §4).

## 2. What the module actually is

`aw883xx_driver.ko` is **not** an i2c bus driver. It has:

* no `.init.text` / `.exit.text`, and NULL `.init`/`.exit` in
  `.gnu.linkonce.this_module` — i.e. no `module_init` / `module_exit`;
* no `alias=` record in `.modinfo` — i.e. no `MODULE_DEVICE_TABLE`;
* no `i2c_register_driver` / `i2c_del_driver` import;
* exactly two exports:

  | symbol | CRC | prototype |
  |---|---|---|
  | `aw883xx_i2c_probe` | `0x713728fc` | `int (struct i2c_client *, const struct i2c_device_id *)` |
  | `aw883xx_i2c_remove` | `0xb3e48038` | `int (struct i2c_client *)` |

The device is bound by MediaTek's `mtk-sp-spk-amp.ko`
(`compatible = "mediatek,speaker_amp"`), whose `mtk_spk_i2c_probe()` calls
`aw883xx_i2c_probe(client, id)` directly (`R_AARCH64_CALL26` at `+0x6f8`) and
sets `mtk_spk_type = 5` on success; `mtk_spk_i2c_remove()` calls
`aw883xx_i2c_remove(client)` at `+0x768` and discards the result. That discard
is why the stock export kept the **pre-6.1 `int` return** even on a 6.1 kernel —
the `void` form would genksyms to `0x64a36158` and break the consumer.

`mtk-sp-spk-amp.ko` is the only consumer in the whole stock image.

## 3. Hardware contract (summary)

Full detail in `phase4-aw883xx-hardware-contract.md` and
`phase4-aw883xx-dt-contract.md`.

| item | value |
|---|---|
| fitted part | **AW88394** (from the ACF `dev_name`/`chip_type` fields) |
| driver chip IDs | `0x2049`, `0x2066`, `0x2183`; the runtime path is `AW883XX_PID_2049` |
| bus / address | i2c-6 (`/soc/i2c@11e01000`), `0x34` → `/sys/bus/i2c/devices/6-0034` |
| register access | 8-bit address, 16-bit big-endian data, raw `i2c_transfer` (no regmap), 5 retries × 5 ms |
| DT node | `/soc/i2c@11e01000/speaker_amp@34`, `compatible = "mediatek,speaker_amp"` |
| reset | `reset-gpio = <&pio 193 0>` |
| IRQ | `irq-gpio = <&pio 41 0>` → `gpiod_to_irq` → `devm_request_threaded_irq` |
| Re guard rails | `re-min = 1000`, `re-max = 40000` (mOhm), straight from DT |
| amplifiers | **one**, channel 0 (no `sound-channel` property ⇒ default 0) |
| profiles | **two**: `Music` (id 0) and `Receiver` (id 10) |
| spin / phase-sync / fade / rename / sync-load / cali-check | all absent from DT ⇒ compiled-in defaults (off) |
| regulators / pinctrl | none |

Everything optional is at its default, so the reconstruction's behaviour on this
board is fully determined by the code plus `aw883xx_acf.bin`.

## 4. ABI boundary

`phase4-aw883xx-provider-boundary.tsv`, `phase4-aw883xx-consumer-boundary.tsv`,
`phase4-aw883xx-modversions.tsv`.

* **Providers.** All 74 `__versions` records (73 imports + `module_layout`)
  resolve against `bazel-bin/common/kernel_aarch64/Module.symvers` of the exact
  GKI `ab/12901745` build, with **identical CRCs** — 74/74 `MATCH`, 0 mismatch,
  0 missing. There is **no vendor provider**: this module depends on nothing but
  vmlinux, which is why `depends=` is empty.
* **Consumers.** `mtk-sp-spk-amp.ko` imports `aw883xx_i2c_probe` @
  `0x713728fc` and `aw883xx_i2c_remove` @ `0xb3e48038`. The reconstruction
  exports exactly those two names with exactly those CRCs, and `__kcrctab` /
  `__ksymtab_strings` are byte-identical to stock.

Consequence: **the reconstruction is a drop-in binary-ABI substitute** for the
stock module.

## 5. Source provenance

`phase4-aw883xx-source-candidates.md`.

Local trees first (exact GKI, the three MiCode vendor references, the NothingOSS
MT6878 tree, the stock image itself) — none contained AW883xx source. The
NothingOSS tree contributed only the MTK speaker-amp glue contract
(`mtk-sp-spk-amp.c`) and carries the *different* `aw882xx` family.

Donor selected:

```
github.com/awinic-driver/aw883xx @ 4f52a10   AW883XX_DRIVER_VERSION "v1.6.0"
```

Match strength before any edit: **233 of the 236** stock function names present;
of the 991 stock strings only three were genuinely absent (`v1.7.1`,
`aw_dev_parse_scene_v_1_0_0_0`, `no valid device scenario resolved`).
Classification `SAME_VENDOR_DIFFERENT_REVISION`.

A public `v1.7.1` drop does not exist (searched via web search, GitHub, grep.app,
searchcode; the only other Awinic repo, `aw883xx_patch`, is v1.3.0, and the
LineageOS `ayn_cq8725s` copy is v1.5.0). Every v1.6.0 → v1.7.1 difference was
therefore recovered from the stock binary.

## 6. RED and the delta ledger

`phase4-aw883xx-RED.md` (full evidence), `phase4-aw883xx-donor-to-recon.diff`
(the applicable patch — 736 lines, 14 files).

RED = the untouched donor built against exact GKI 12901745
(`//lieppos/aw883xx-recon/donor-build:aw883xx_driver_donor`, `BUILD_RC 0`,
three unresolved VFS symbols coming from the donor's calibration-file block).

RED vs oracle: +8 functions, +7 imports, −2 exports, 16/236 shared functions
with a differing relocation sequence, `sizeof(struct aw_device)` `0x748` vs
`0x750`.

Eleven deltas closed that gap:

| # | delta | key evidence |
|---|---|---|
| D1 | version string `v1.6.0` → `v1.7.1` | `drv_ver_show` string pool |
| D2 | `AW_CALI_STORE_EXAMPLE` **off** | no `filp_open`/`kernel_read`/`kernel_write`/`skip_spaces` imports, no `/mnt/vendor/persist/factory/audio/aw_cali.bin` string, no `aw_cali_write_re_to_nvram` symbol |
| D3 | `g_cali_re_time` default **1000 ms** (donor 3000) | `.data+0x1e8` initialiser `0x3e8` vs `0xbb8`; fixing it makes `.data` bit-exact |
| D4 | `struct aw_sysst_desc` drops `st_sws_check` | `profctrl_desc` at `+0xe8` vs `+0xec`; PID 2066/2183 write `0x311` (`SWS_CHECK`) into `st_check` and nothing at `+0xe8` |
| D5 | `struct aw_noise_gate_en` → 2-entry `{reg, mask, st_and_mask}` SYSST gate table | stock `aw883xx_device_start` `0x5d30..0x5dc8` (two `cmp #0xff` / `reg_read` / `bics` / `and check_value` blocks at `+0x318..+0x32c`) |
| D6 | `aw_dev_sysint_check()` removed | symbol absent; `aw883xx_device_stop` never references `get int status fail ret:%d` / `int check fail:0x%04x` |
| D7 | ACF v1.0.0.0 dev/default parsers merged into `aw_dev_parse_scene_v_1_0_0_0`, with an ascending-`dev_profile` insertion sort over a 32-entry index array | `aw883xx_dev_cfg_load` `0x21ec` (single call site, bool selector), `0x241c`–`0x252c` (sort), `0x2648`–`0x2700` (dispatch) |
| D8 | i2c_driver + `module_init/exit` + `MODULE_DEVICE_TABLE` removed, probe/remove `EXPORT_SYMBOL`ed | NULL module init/exit, no `alias=`, `__ksymtab_strings`, consumer relocations, `modules.dep` |
| D9 | `aw883xx_i2c_remove` keeps `int` return | export CRC `0xb3e48038` (void form = `0x64a36158`), 260 vs 256 bytes |
| D10 | index array bound returns `-EINVAL` instead of trapping (LieppOS hardening) | behaviour-neutral for ≤ 32 matching DDEs; the shipped ACF has 3 |
| D11 | two build-time safety gates, default = stock | see §9 |

D4 + D5 together account exactly for the `+8` growth of `struct aw_device` and
were cross-checked against three independent anchors: `cali_desc` `0x384→0x390`
(`sub x0, x0, #0x390` container_of in `aw883xx_cali_get_ra`), `monitor_desc`
`0x460→0x468` (`add x23, x20, #0x468` in the ACF monitor dispatch) and `ops`
`0x660→0x668`.

**A hypothesis was withdrawn during this work:** the 8 `import_ns` records in
`.modinfo` initially looked like a vendor addition. They are not — the
`MODULE_IMPORT_NS` sits in `aw883xx.h`, exactly 8 of the 10 translation units
include that header, and their `.modinfo` positions (five, then
`description`+`license`, then three) fall out automatically once the object
order matches the stock link order recovered from `.text`.

## 7. Firmware / config contract

`phase4-aw883xx-firmware-config-contract.md`.

The kernel loads exactly two firmware names — `aw883xx_acf.bin` (present,
asynchronous, 5 retries) and `aw883xx_monitor.bin` (**not shipped**, only
requested when userspace writes the `monitor_update` sysfs node).

```
/vendor/firmware/aw883xx_acf.bin
  36141 bytes  sha256 cc246bae1ca600908d88fd77309054e1e73bf92f73bbecf758dca581b34071a0
  a_id 0x0a15f908  project "M190"  custom "DZ"  version 0.0.0.2  author 320
  a_hdr_version 0x00000001  (AW_CFG_HDR_VER_0_0_0_1 -> 64-byte aw_cfg_dde)
  3 DDEs, all AW_DEV_DEFAULT_TYPE_ID / dev_index 0:
    [0] MONITOR  192 B  @0x00110   (software-monitor table)
    [1] MUTLBIN  17594 B @0x001d0  profile 0  (Music)
    [2] MUTLBIN  18083 B @0x0468a  profile 10 (Receiver)
```

Each MULTLBIN decomposes into `DATA_TYPE_REGISTER` (188 B, 46 register words),
`DATA_TYPE_DSP_REG` (→ DSP RAM `0x9c80`), `DATA_TYPE_SOC_APP` (DSP firmware →
`0x8c00`, app_ver `0xffff0001` / `0xfffe0001`) and one sub-bin of type `0x12`
that is in neither binary's `data_type_enum` and is silently skipped by both.

Because the header is v0.0.0.1, the runtime path is
`aw_dev_load_cfg_by_hdr → aw_dev_parse_dev_type → aw_dev_parse_dev_default_type`;
the v1.7.1-only scene parser (D7) is reconstructed for completeness but is not
exercised on this device.

Other Awinic blobs (`AW_DSP.bin`, `awinic_params.bin`,
`awinic_sinwave_params.bin`, `libawinicsmartpaparse.so`,
`awinic.audio.effect.so`) belong to the audio HAL/SKTune effect and are never
touched by this driver. A whole-image scan shows `aw883xx_acf`, `aw_smartpa` and
`re25_calib` occur in exactly one file: the `.ko` itself.

## 8. Calibration and protection contract

`phase4-aw883xx-calibration-contract.md`.

Interfaces: `/dev/aw_smartpa` (misc, ioctl magic `'a'`, nrs 5, 6, 17–21, plus an
ASCII command `write()`), 13 + 2 + 5 sysfs attributes on `6-0034`, and the
`/sys/class/smartpa/` class with `cali_time re25_calib f0_calib f0_q_calib
re_range`.

Key behavioural facts recovered:

* **The kernel does not persist calibration.** `AW_CALI_STORE_EXAMPLE` is
  compiled out (D2), so Re lives only in `aw_cali_desc` and is re-applied to the
  chip on every `aw883xx_device_start()` via `aw_dev_init_re_update()`.
  Persistence is MTK NVRAM in userspace:
  `/mnt/vendor/nvdata/APCFG/APRDCL/smartpa_calib`
  (`iAP_CFG_CUSTOM_FILE_SMARTPA_CALIB_LID`, written by `vendor/bin/smartpa_nvtest`
  + `libcustom_nvram.so`).
* **Re calibration** mutes the amp, swaps four DSP calibration words, dwells
  `g_cali_re_time` (**1000 ms** on stock, D3, scaled by `v*32/48`), samples 8
  times, drops the 2 extremes, averages, and range-checks against the DT
  `re-min`/`re-max`.
* **F0/Q calibration drives white noise into the speaker** for
  `AW_CALI_F0_TIME = 5000 ms` via the DSP noise generator
  (`CFG_MBMEC_GLBCFG` + `NOISE_MASK`) plus a DSP volume ramp.
* Protection: hardware monitor, software monitor (temperature/voltage →
  ipeak/gain/vmax stepping from the ACF monitor table), DSP monitor
  (`dsp_monitor_delay` default 1000 ms), CRC32 checks on the downloaded DSP
  firmware/config, and PLL/SYSST/DSP-status gating of `device_start`
  (`AW_DEV_SYSST_CHECK_MAX = 10` × 2 ms).
* v1.7.1 changed the SYSST gating itself (D4/D5). On the fitted PID 2049 both
  gate entries are `AW_REG_NONE`, so the new path is inert here; on PID 2066 it
  is behaviourally identical to v1.6.0; on PID 2183 it adds a second condition
  (register `0x69` bit 2 drops the boost-finished requirement). Bit 2 of `0x69`
  has no published name and is deliberately carried by address as
  `AW_PID_2183_REG_0X69_BIT2_MASK` — its numeric effect is asserted, its meaning
  is not.

## 9. Deliberate deviations from stock

Two `#ifndef`-guarded macros in `aw883xx_calib.h`, **both defaulting to 1
(= stock)**. With the defaults the produced code is byte-identical to stock;
they exist only for bring-up on hardware whose speaker/boost state is unknown.

| macro | at 0 |
|---|---|
| `AW_ALLOW_CALIBRATION_WRITES` | `aw_cali_svc_cali_re()` and `aw_cali_svc_cali_f0_q()` return `-EPERM` |
| `AW_ALLOW_FACTORY_MODE` | `reg_store`, `rw_store`, `dsp_rw_store`, `awrw_store` return `-EPERM` |

Playback initialisation, profile/firmware download, power sequencing and monitor
protection are **not** gated — the stock evidence proves they are required for
normal operation.

Plus D10 (bounded index array returns `-EINVAL` instead of relying on the
compiler's array-bounds trap). That is the complete deviation list.

## 10. Build

```
workspace : ~/kernel-work/gki-12901745-workspace
kernel    : //common:kernel_aarch64   (Google GKI ab/12901745,
                                       6.1.115-android14-11-g6b18f0b574ab)
RED       : tools/bazel build //lieppos/aw883xx-recon/donor-build:aw883xx_driver_donor
recon     : tools/bazel build //lieppos/aw883xx-recon/recon:aw883xx_driver_gki

BUILD_RC (both, after `bazel clean`)   : 0
compiler warnings (recon)              : none (-Werror clean)
modpost warnings (KBUILD_MODPOST_WARN=1): none — zero unresolved symbols
```

Object order in the recon `Makefile` reproduces the stock link order recovered
from the `.text` layout:

```
aw883xx_monitor.o  aw883xx_bin_parse.o  aw883xx_device.o  aw883xx_init.o
aw883xx_calib.o    aw883xx_spin.o       aw883xx.o
aw883xx_pid_2049_init.o  aw883xx_pid_2066_init.o  aw883xx_pid_2183_init.o
```

## 11. Verification against the oracle

`phase4-aw883xx-verify-byte-identity.txt`,
`phase4-aw883xx-verify-recon-vs-stock.txt`,
`phase4-aw883xx-verify-function-sequence-diff.txt`.

| check | result |
|---|---|
| imported symbols | **73 / 73**, exact set, 0 extra, 0 missing |
| `__versions` (74 records, 4736 B) | **byte-identical** |
| `__ksymtab_strings` (38 B), `__kcrctab` (8 B) | **byte-identical** |
| defined `.text` functions | **236 / 236**, 0 extra, 0 missing |
| byte-identical functions | **235 / 236** |
| functions with a differing relocation/call/string multiset | **0 / 236** |
| `.rodata.str1.1` strings | 991 / 991, 0 extra, 0 missing |
| `.rodata` (3353 B) | **byte-identical** |
| `.bss` (50 B) | **byte-identical** |
| `.data` non-relocated bytes | **identical** |
| `.data` relocation (offset, target symbol) list | **identical** |
| `OBJECT` symbols | 81 / 81; only `__UNIQUE_ID_vermagic` differs (string length) |
| `.modinfo` records | identical apart from `vermagic` |

### The single residual

`aw883xx_dev_cfg_load` is 3564 bytes versus 3560. Its relocation, call-target
and string multisets are **identical** to stock; the difference is one
register-allocation swap (`x24`↔`x28`) and one spill slot moved, inside the
inlined `aw_dev_parse_scene_v_1_0_0_0` body. Compiler scheduling was not chased
once semantic equality was proven. That 4-byte shift is also the only reason the
`.text` addends inside `.data` relocations differ.

**Zero unexplained hardware-affecting differences remain.**

## 12. Open items

* No public `v1.7.1` Awinic drop exists to cross-check the D4–D7 deltas against;
  they rest entirely on the stock disassembly. Every one is cited to a concrete
  instruction range in `phase4-aw883xx-RED.md`.
* Bit 2 of AW88399 (`PID 2183`) register `0x69` is proven-but-unnamed.
* `aw883xx_monitor.bin` is referenced by the driver but absent from the stock
  image, so the `monitor_update` sysfs path cannot succeed on a stock filesystem.
  This is stock behaviour, faithfully reproduced.
* Runtime validation on the device has **not** been performed. Everything in
  this report is static; loading the reconstruction on hardware is a separate,
  later step.

## 13. Artifacts

Tracked in this repository:

```
kernel/phase4-aw883xx-reconstruction.md            this report
kernel/phase4-aw883xx-RED.md                       RED baseline + delta ledger D1..D11
kernel/phase4-aw883xx-source-candidates.md         local-then-public donor search
kernel/phase4-aw883xx-stock-inventory.md           full stock ELF inventory
kernel/phase4-aw883xx-hardware-contract.md         chip/bus/GPIO/IRQ/protection contract
kernel/phase4-aw883xx-dt-contract.md               device-tree contract
kernel/phase4-aw883xx-firmware-config-contract.md  ACF + blob contract
kernel/phase4-aw883xx-calibration-contract.md      calibration + safety classification
kernel/phase4-aw883xx-donor-to-recon.diff          applicable patch, donor 4f52a10 -> recon
kernel/phase4-aw883xx-register-map.tsv             proven register/descriptor operations
kernel/phase4-aw883xx-provider-boundary.tsv        74 imports vs exact GKI 12901745
kernel/phase4-aw883xx-consumer-boundary.tsv        mtk-sp-spk-amp expected CRCs
kernel/phase4-aw883xx-modversions.tsv              stock __versions dump
kernel/phase4-aw883xx-exports.tsv                  stock exports + CRCs
kernel/phase4-aw883xx-verify-byte-identity.txt     oracle comparison summary
kernel/phase4-aw883xx-verify-recon-vs-stock.txt    full section/symbol/string comparison
kernel/phase4-aw883xx-verify-function-sequence-diff.txt
```

Build tree (outside this repository):

```
~/kernel-work/gki-12901745-workspace/lieppos/aw883xx-recon/donor-pristine/  donor @ 4f52a10
~/kernel-work/gki-12901745-workspace/lieppos/aw883xx-recon/donor-build/     RED target
~/kernel-work/gki-12901745-workspace/lieppos/aw883xx-recon/recon/           reconstruction
```

The reconstruction source is fully recoverable from the tracked repository:
clone `github.com/awinic-driver/aw883xx` at `4f52a10` and apply
`kernel/phase4-aw883xx-donor-to-recon.diff`.
