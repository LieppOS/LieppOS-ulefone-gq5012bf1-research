# Phase 4 — `aw36518_v2.ko` reconstruction (Ulefone GQ5012BF1)

Second Awinic AW36518 flash-LED instance of the Ulefone Armor 29 Pro Thermal
(`GQ5012BF1`, MediaTek MT6878).  This is a **family-delta** phase: the AW36518
reconstruction (`phase4-aw36518-reconstruction.md`) is the starting point, and
every claimed delta was re-proved against the `aw36518_v2.ko` oracle rather than
assumed from the earlier family note.

## Final classification

```
SOURCE_DELTA_RECONSTRUCTION_EXACT
```

Stronger than the AW36518 label, and justified by the fact that the *delta*
itself — not just the ABI — is proved exactly:

* the two stock modules are **19/23 functions byte-identical** to each other and
  their per-function call/string/data reference multisets are **22/23 identical**
  after normalising the `aw36518_v2` token; the single difference is
  `parse_dt` losing `CALL:is_yft_cts_board`;
* the LieppOS V2 source is the LieppOS AW36518 source with the token renamed and
  **exactly two lines removed** (`phase4-aw36518-v2-recon-source-normalised.diff`);
* the rebuilt V2 module reproduces the oracle with 23/23 functions, 45/45
  imports, **46/46 identical MODVERSION CRCs**, 63/63 identical strings, all 14
  initialised data objects byte-identical and 12/23 functions byte-identical —
  including `aw36518_v2_parse_dt`, the one function the delta touches;
* `.modinfo` matches on name, author, description, license, depends and all
  three aliases (only `vermagic` differs, as for every local build).

It is not `DIRECT_SOURCE_MATCH` (no vendor source is public) and not a
whole-module byte match (Clang scheduling residue remains in 11 functions), so
whole-module exactness is **not** claimed.

## Stock oracle

```
path        workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/aw36518_v2.ko
copies      1 (only copy in the image; 471 module paths / 458 unique hashes scanned)
size        43168 bytes
SHA-256     c7faa3ba4d8f14e4d24087f1dbd9f7c7c492e384214d571def17fb087de1458e
build-id    eb045d88ffdafb3cc03079faa1516eda2725f24d
ELF         ET_REL, EM_AARCH64, 42 sections, 178 symbols
compiler    Android (10087095, +pgo, +bolt, +lto, -mlgo, based on r487747c) clang 17.0.2
            — byte-identical toolchain string to aw36518.ko and aw36515.ko
vermagic    6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
name        aw36518_v2      author  Alec <like@awinic.com>
description Awinic AW36518_V2 LED flash driver          license GPL
depends     flashlight
aliases     i2c:aw36518_v2, of:N*T*Cmediatek,aw36518_v2, of:N*T*Cmediatek,aw36518_v2C*
parameters  none            srcversion  absent
```

Load order `… aw36515.ko, aw36518.ko, aw36518_v2.ko, flashlight.ko …`.
Live evidence: `/proc/modules` shows `aw36518_v2 24576 0 - Live`,
`flashlight 65536 4 aw36518_v2,aw36518,aw36515,imgsensor`, and — decisively —
`yft_devinfo`'s user list contains `aw36518` but **not** `aw36518_v2`.
Full record: `phase4-aw36518-v2-stock-oracle.txt`.

## AW36518 → AW36518_V2 delta ledger

Machine-readable with per-row evidence: `phase4-aw36518-v2-delta-ledger.tsv`.

### Source deltas (10)

| # | Delta | Evidence |
|---|---|---|
| D1 | module name token `aw36518` → `aw36518_v2` | `.gnu.linkonce.this_module`: the *only* differing bytes are 31..33 (`\0\0\0` → `_v2`) |
| D2 | `i2c_device_id.name` (embedded `char[]`) | `.rodata+0x08`: `b'aw36518\0…'` → `b'aw36518_v2\0…'` |
| D3 | `of_device_id.compatible` (embedded `char[]`) | `.rodata+0x48+64`: `mediatek,aw36518` → `mediatek,aw36518_v2` |
| D4 | `i2c_driver.driver.name` string | `.data+0x38` ABS64 → the renamed literal |
| D5 | `MODULE_DESCRIPTION` gains `_V2` | `.modinfo`, `__UNIQUE_ID_description467` 44 → 47 B |
| D6 | three module aliases | `.modinfo`; alias objects 18/31/33 → 21/34/36 B |
| D7 | vendor log tag `"aw36518[%s] "` → `"aw36518_v2[%s] "` | 25 tagged format strings; `.rodata.str1.1` 1535 → 1667 B |
| D8 | all function identifiers (`__func__` strings) | 18 renamed `__func__` literals |
| D9 | V4L2 sub-device name `"aw36518-led0"` → `"aw36518_v2-led0"` | `.rodata.str1.1`; `flashlight.ko::fl_enable()` matches both names |
| D10 | **`if (is_yft_cts_board()) continue;` removed from `parse_dt`** | `parse_dt` 364 → 296 B (−68); reference-multiset delta is exactly `{CALL:is_yft_cts_board: 1}`; `.rela.text` −24 B |

### ABI consequences (3)

| # | Delta | Evidence |
|---|---|---|
| D11 | imports 46 → 45 (`is_yft_cts_board` gone) | import tables |
| D12 | `__versions` 47 → 46, all 46 shared CRCs identical | `__versions` 3008 → 2944 B |
| D13 | `depends` `yft_devinfo,flashlight` → `flashlight` | `.modinfo`; live `/proc/modules` user lists |

### Compiler-derived consequences, *not* separate source edits (2)

| # | Effect | Evidence |
|---|---|---|
| D14 | `strscpy()` length immediate `#13` → `#16` at `probe+0x270` | `sizeof("aw36518-led0")` vs `sizeof("aw36518_v2-led0")`; both LieppOS rebuilds emit exactly these immediates from the identical source construct |
| D15 | `__LINE__` constants shift: probe 932/986/991/993 → 930/984/988/990, suspend 1023 → 1020, resume 1033 → 1030 | MOVZ immediates; the −2 before `probe` is exactly the 2 removed guard lines (D10); one further line was removed inside probe's reset block (formatting only, unobservable) |

### Proved **non**-deltas

* Every register write, mask, current mapping, timeout code, thermal limit table
  and fault decode is unchanged: 19/23 functions are byte-identical *between the
  two stock modules*, and `.rodata.cst16`, the mode table (`.rodata+0x468 =
  {0x00,0x0C,0x08}`) and the `set_ctrl` switch table are byte-identical.
* All operation tables (`flashlight_operations`, `thermal_cooling_device_ops`,
  `v4l2_ctrl_ops`, `v4l2_subdev_ops`, `v4l2_subdev_internal_ops`), the regmap
  config, the PM ops and the `reg` sysfs attribute are byte-identical.
* `.data`, `.bss`, `.init.data`, `.exit.data` are byte-identical.
* The MediaTek flashlight device identity (`type/ct/part/channel/decouple`) is
  **not** in the code at all — it is read from the DT child (D18 in the ledger).

## Hardware / DT contract

`aw36518_v2` is the **same silicon type on a second I²C bus**, not a different
chip and not an alternate BOM of the first one:

| | AW36518 | AW36518_V2 |
|---|---|---|
| DT node | `i2c@11e03000/aw36518@63` | `i2c@11d72000/aw36518_i2c13@63` |
| compatible | `mediatek,aw36518` | `mediatek,aw36518_v2` |
| I²C address | `0x63` | `0x63` (same address, different controller) |
| live device | `8-0063` | `12-0063` |
| child | `flash@0 { type=0 ct=0 part=1 reg=2 }` | `flash@1 { type=0 ct=1 part=1 reg=3 }` |
| `#cooling-cells` | 2 | 2 |
| `flash-externel` GPIO | absent | absent |
| channels | 1 (`LED0`) | 1 (`LED0`) |
| sub-device name | `aw36518-led0` | `aw36518_v2-led0` |

Live confirmation (read-only snapshot already in the repo,
`evidence/hw-tests/build14-touch-usb/of-live-input-buses.txt`):

```
12-0063 driver=driver modalias=of:Naw36518_i2c13T(null)Cmediatek,aw36518_v2
        of=/sys/firmware/devicetree/base/soc/i2c@11d72000/aw36518_i2c13@63
 8-0063 driver=driver modalias=of:Naw36518T(null)Cmediatek,aw36518
        of=/sys/firmware/devicetree/base/soc/i2c@11e03000/aw36518@63
```

Both are bound and live.  Because the two drivers are the same code, the entire
AW36518 hardware/register/electrical contract applies verbatim to V2:
flash `0x03[7:0] = (µA−2940)/5870` (max 1 499 790 µA), torch
`0x05[7:0] = (µA−750)/1510` (max 385 800 µA), timeout `0x08[3:0] = ms/40` with a
400 ms init default, mode/enable in `0x01` (`0x03`/`0x0C`/`0x2C` masks), fault
bits from `0x0A`, cooling table `{150000,100000,50000,25000} µA` with
`max_state = 4`, chip-ID read of `0x00` (logged only) and the `0x07 |= 0x80`
software reset.  See `phase4-aw36518-register-map.tsv` and
`phase4-aw36518-electrical-contract.md`; no electrical difference exists and
none was invented.

The two instances differ **only** in the DT-provided colour-temperature index
(`ct = 0` vs `ct = 1`) within the same `part = 1` assembly — i.e. they are the
warm/cool pair of the secondary flash module, mirroring the AW36515 pair
(`part = 0`, `ct = 0/1`) that serves the main camera.

## Framework / userspace contract

Identical to AW36518 (`phase4-aw36518-framework-contract.md`), with the two
name-dependent hooks re-verified on the V2 side:

* **flashlight core**: `flashlight.ko::fl_enable()` contains
  `strncmp(name, "aw36518-led0", 12)` **and**
  `strncmp(name, "aw36518_v2-led0", 15)`; both matches take the branch that
  bypasses the low-battery / over-current disable.  Verified directly by
  disassembly of `fl_enable` and by the two string references it owns — so the
  V2 sub-device name is ABI on the V2 side too and must stay exactly
  `aw36518_v2-led0`.
* **camera HAL**: `libcam.hal3a.v3.strobe.so` addresses devices through
  `/dev/flashlight` by `(type, ct, part)`; V2 answers as `(0, 1, 1)`.  No stock
  userspace file mentions the module or chip name.
* **CTS-board behaviour**: `aw36518.ko` skips flashlight registration when
  `is_yft_cts_board()` is true; **`aw36518_v2.ko` has no such guard and always
  registers**.  This is a real behavioural difference between the siblings, and
  it is reproduced exactly (it is the whole of delta D10).
* The vendor debug sysfs `reg` attribute (0644, 14-register dump / raw
  `regmap_write`) exists on the V2 device as well
  (`/sys/bus/i2c/devices/12-0063/reg`) and is reproduced byte-identically
  (`dev_attr_reg`).

## ABI: providers and consumers

* Imports 45: 43 from GKI `vmlinux`, plus `flashlight_dev_register_by_device_id`
  (`0xe8fd8896`) and `flashlight_kicker_pbm` (`0x8287fd03`) from `flashlight.ko`.
  `is_yft_cts_board` is **absent** — so `yft_devinfo.ko` is *not* a provider for
  V2 and the already-built `yft_devinfo` reconstruction is deliberately **not**
  linked into this target.
* Both vendor CRCs come from the really built
  `//lieppos/aw36518-recon/providers/flashlight:flashlight_provider`
  `Module.symvers`; no CRC was written or patched by hand.
* 45/45 rows `MATCH` across stock CRC / exact-GKI CRC / reconstructed-provider
  CRC / rebuilt-consumer CRC: `phase4-aw36518-v2-provider-boundary.tsv`.
* Exports: 0.  No stock module imports an `aw36518_v2` symbol, and live
  `/proc/modules` shows refcount 0: `phase4-aw36518-v2-consumer-boundary.tsv`.


> Provider note (added by the AW36515 phase): the shared
> `//lieppos/aw36518-recon/providers/flashlight` target is now built with
> `CONFIG_MTK_FLASHLIGHT_PT=1` (plus the two throttling surfaces stock's own
> `flashlight.ko` imports) so that it really exports `flashlight_pt_is_low`
> for AW36515.  The two CRCs consumed here, `0xe8fd8896` and `0x8287fd03`,
> are **unchanged**, so nothing in this report is affected.

```
missing provider symbols = 0
manually fabricated CRCs = 0
```

## Exact-GKI build

```
kernel      android14-6.1-2024-12_r4, common commit 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09, CI ab/12901745
target      //common:kernel_aarch64
module      //lieppos/aw36518-v2-recon:aw36518_v2_recon
source      $GKI_WS/lieppos/aw36518-v2-recon/aw36518_v2.c   (1016 lines)
BUILD_RC              0
compiler warnings     0
modpost warnings      0
unresolved symbols    0
KBUILD_MODPOST_WARN   not used
output      aw36518_v2.ko, 43008 bytes,
            SHA-256 f417845ff67947bfd22e8edbee722f7f4783e10b784dbdc3badcbacf0b1d3a52
```

(The `flashlight.ko` provider is still built with `KBUILD_MODPOST_WARN=1` for
its own tertiary `mtk_pbm`/`mtk_peak_power_budget` symbols; that relaxation
never applies to `aw36518_v2.ko`.)

## Structural verification (stock V2 vs rebuilt V2)

| Metric | Result |
|---|---|
| Functions | stock 23 / rebuilt 23 / shared 23 / stock-only 0 / rebuilt-only 0 |
| Size-identical | 19 / 23 |
| Byte-identical | **13 / 23** — `close`, `cooling_get_cur_state`, `cooling_get_max_state`, `flash_open`, `flash_release`, `ioctl`, `open`, **`parse_dt`**, `remove`, `torch_brt_ctrl`, `reg_store`, `init_module`, `cleanup_module` |
| KCFI type ids | 20 present, 20/20 identical |
| Imports | 45 / 45, 0 missing, 0 extra |
| Exports | 0 / 0 |
| MODVERSIONS | 46 / 46 common, **46 CRC-identical**, 0 mismatch |
| Data objects | 32/32 names; all 14 initialised `.data`/`.rodata` objects byte-identical (incl. the renamed `id_table`/`of_table` and the thermal table) |
| Strings | 63 / 63 identical |
| Reference multisets | 21 / 23 identical |
| `.modinfo` | name, author, description, license, **depends=`flashlight`**, all 3 aliases identical; parameters 0/0 |

Raw output: `phase4-aw36518-v2-verify-recon-vs-stock.txt`.

That `aw36518_v2_parse_dt` is byte-identical is the direct proof that delta D10
is exactly right: the one function the V2 delta touches reproduces the oracle
bit for bit.

### Shared fidelity fix found during this phase

The V2 comparison exposed a struct-layout error inherited from the AW36518
phase: stock allocates `sizeof(struct aw36518_flash) = 0x308` with
`dnode[0] @ +0x278`, `flash_dev_id[0] @ +0x298` and `cdev @ +0x2d0`, i.e. the
vendor struct carries **24 bytes (three pointer-sized members) between `dnode[]`
and `flash_dev_id[]`** that the reconstruction lacked, shifting every following
field by −24.  No stock instruction ever touches that range, so the members'
identity is unrecoverable; they are now reproduced as an explicitly unused,
documented reserved gap in **both** reconstructions.  Effect: byte-identical
functions rose from 6 → 12 for AW36518 **and** V2, and
`parse_dt`/`remove`/`ioctl`/`torch_brt_ctrl` became exact.  The AW36518 report
and its verification artifact were refreshed accordingly.

A second shared fidelity fix arrived from the later AW36515 phase: the vendor's
`reg_store()` keeps its two `sscanf` outputs in **one 2-element `u32` array**,
not two scalars (stock computes the second output pointer as `orr xN, sp, #0x4`
from a single frame base).  Applying that form here made `reg_store`
byte-identical as well, so the counts in this report are **13/23 byte-identical
and 19/23 size-identical**.

### Residual differences (11 functions, all explained, none hardware-affecting)

1. **Clang scheduling** — `init`, `led0_set_ctrl`, `suspend`, `reg_show`,
   `cooling_set_cur_state` are size-identical and differ only by reordered
   instructions or by an intra-section `bl` displacement (1–7 words each).
2. **Size-differing five** — `probe` (1588 vs 1584), `led0_get_ctrl` (208 vs
   196), `set_driver` (184 vs 188), `strobe_store` (604 vs 608).
   Reference multisets, calls, constants and strings are equal;
   the deltas are register allocation and branch-form choices under
   `+pgo/+bolt/+lto` vendor flags that Kleaf does not reproduce.
3. **`__LINE__` values** (D15) — the vendor file's absolute line numbering is not
   reproduced; the format strings and argument lists are identical.
4. **`.data` object placement** — `aw36518_v2_flash_ops` and `dev_attr_reg` land
   at different offsets inside `.data`; contents byte-identical.  This is the
   only cause of the 2 non-identical reference multisets.
5. **`vermagic`** — `…-g945dff7bc1bf` (Ulefone) vs `…-maybe-dirty` (local Kleaf
   build of the same `6.1.115-android14-11` tree).
6. **`parse_dt` no-`of_node` early return** — stock leaves a stale value in `w0`;
   the reconstruction returns 0.  Unreachable for an I²C-of device and ignored
   by `probe`.

No residual touches a register write, a current, a timing value, a device
identity, an ABI symbol or a CRC.

## Electrical behaviour

Unchanged from AW36518 and **not** re-derived from any donor: proved unchanged
by the 19/23 stock-vs-stock byte-identical functions plus the byte-identical
`.rodata.cst16` thermal table, mode table and switch table.  In particular V2
uses the same 400 ms init timeout, the same 250 000 µA `FLASH_IOC_SET_ONOFF`
torch point, the same `level × 25 000 µA` strobe scaling, and the same
`{150000,100000,50000,25000} µA` cooling ladder.  No electrical difference was
invented.

## Runtime-validation status

```
STATIC RECONSTRUCTION      DONE   (relocation-aware disassembly of both stock oracles)
BUILD VERIFICATION         DONE   (exact GKI ab/12901745, BUILD_RC=0, 0 warnings, 0 unresolved)
ABI VERIFICATION           DONE   (45/45 imports, 46/46 CRCs, 0 exports, real provider symvers)
PASSIVE RUNTIME EVIDENCE   DONE   (pre-existing read-only /proc/modules + sysfs snapshots)
LIVE HARDWARE VALIDATION   NOT DONE - intentionally
```

## Safety statement

Offline only.  During this phase no torch was enabled, no flash was fired, no
I²C register was written, no GPIO was driven, no module was inserted or removed,
no DT/DTBO was changed, no partition was flashed and no slot was switched.  The
only runtime data used are read-only snapshots already committed to this
repository.  The reconstruction adds no flash/torch gate and no clamp: it is
behaviourally identical to stock, including the debug `reg` sysfs write path,
which must remain root-only in LieppOS policy.

## Evidence index

| Artifact | Content |
|---|---|
| `phase4-aw36518-v2-stock-oracle.txt` | frozen V2 oracle identity |
| `phase4-aw36518-v2-delta-ledger.tsv` | AW36518 → V2 delta ledger with per-row evidence |
| `phase4-aw36518-v2-functions.tsv` / `-objects.tsv` / `-imports.tsv` / `-modversions.tsv` | stock V2 symbol tables (KCFI ids, CRCs) |
| `phase4-aw36518-v2-provider-boundary.tsv` / `-consumer-boundary.tsv` | V2 ABI boundary |
| `phase4-aw36518-v2-verify-recon-vs-stock.txt` | structural verification output |
| `phase4-aw36518-v2-recon-source-normalised.diff` | the entire source delta: 2 removed lines |
| `phase4-aw36518-v2-recon-source.diff` | raw (un-normalised) diff incl. the rename |
| `phase4-aw36518-reconstruction.md` + its contract documents | shared hardware / register / electrical / framework contracts |
| `phase4-aw36518-family-comparison.md` | family evidence, incl. AW36515 preparation |
| `$GKI_WS/lieppos/aw36518-v2-recon/` | reconstruction source + Kleaf target |
| `$GKI_WS/lieppos/aw36518-recon/providers/flashlight/` | real provider used for CRC generation |
| `workspace/phase4-aw36518-v2/` (gitignored) | V2 disassembly, section blobs, rebuilt module |

## Final verdict

`aw36518_v2.ko` is **frozen and ready for integration**.  The AW36518 → V2
transformation is fully characterised (10 source deltas, 3 ABI consequences, 2
compiler-derived effects, everything else proved identical), the LieppOS source
delta is literally two removed lines plus a token rename, the module builds
clean against exact GKI `ab/12901745` with real provider CRCs, and it is
ABI-identical to the stock oracle with a fully explained, hardware-neutral
residue.  Live validation on Slot B remains, deliberately, out of scope.
