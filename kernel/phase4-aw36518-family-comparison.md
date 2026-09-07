# GQ5012BF1 — AW36518 / AW36518_V2 / AW36515 family comparison (Phase 15)

Purpose: make the two sibling reconstructions cheap.  Nothing here was
reconstructed; these are measurements on the stock modules.

| | `aw36518.ko` | `aw36518_v2.ko` | `aw36515.ko` |
|---|---|---|---|
| size | 43 128 B | 43 168 B | 34 768 B |
| SHA-256 | `7dcf64a7…76247` | `c7faa3ba…1458e` | `85e5a860…f643e8` |
| author | `Alec <like@awinic.com>` | `Alec <like@awinic.com>` | `Alec <like@awinic.com>` |
| FUNC symbols | 23 | 23 | 23 |
| imports | 46 | 45 | 46 |
| exports | 0 | 0 | 0 |
| compatible | `mediatek,aw36518` | `mediatek,aw36518_v2` | `mediatek,aw36515` |
| I²C | `8-0063` | `12-0063` | separate bus, `0x63` |
| LED channels | 1 (`aw36518-led0`) | 1 (`aw36518_v2-led0`) | 2 (`led0`, `led1`) |
| DT ids (type,ct,part) | 0,0,1 | 0,1,1 | 0,0,0 and 0,1,0 |
| media endpoints | none | none | yes (`mtk-composite-v4l2-1` ports 0/1) |
| `flash-externel` GPIO in DT | absent | absent | `<0x89 0x74 0x00>` |

## `aw36518_v2.ko` — same source, one `#define` apart

> **Status: reconstructed and verified.** The hypothesis below was re-proved
> against the V2 oracle in `phase4-aw36518-v2-reconstruction.md`
> (`SOURCE_DELTA_RECONSTRUCTION_EXACT`).  Confirmed additions from that phase:
> the two stock modules are **19/23 functions byte-identical to each other**,
> their per-function reference multisets are 22/23 identical (only
> `CALL:is_yft_cts_board` differs), `MODULE_DESCRIPTION` also changes
> (`AW36518` → `AW36518_V2`), and the LieppOS source delta is literally two
> removed lines plus the token rename.

After normalising the `aw36518_v2_` prefix to `aw36518_`:

* **function-name sets are identical** (23/23);
* **function sizes are identical for 22/23** functions;
* the only size difference is `parse_dt`: 364 B (v1) vs 296 B (v2);
* the **string multisets are identical** after the same normalisation;
* the import sets differ by exactly one symbol: `aw36518.ko` imports
  `is_yft_cts_board` (`yft_devinfo`), `aw36518_v2.ko` does not;
* `MODULE_DEPENDS` differ accordingly (`yft_devinfo,flashlight` vs `flashlight`).

`364 − 296 = 68` bytes is precisely the `bl is_yft_cts_board` + branch +
register-shuffling block observed at `aw36518_parse_dt+0x128…0x148`.

**Conclusion (verified):** `aw36518_v2.ko` is the *same vendor source file* built
with the name macro changed to `aw36518_v2` and the `is_yft_cts_board()` CTS skip
compiled out.  The complete ledger — 10 source deltas, 3 ABI consequences and 2
compiler-derived effects (`strscpy` length immediate, `__LINE__` shifts), with
everything else proved identical — is `phase4-aw36518-v2-delta-ledger.tsv`.

Behavioural note worth carrying forward: because the CTS guard exists only in
AW36518, a CTS board registers **only** the V2 device with the MediaTek
flashlight core; the AW36518 instance is then V4L2-only.

## `aw36515.ko` — related but genuinely different driver

> **Status: reconstructed and verified.** The hypothesis below was carried
> through its own mandatory RED and full reconstruction in
> `phase4-aw36515-reconstruction.md` (`SOURCE_DELTA_RECONSTRUCTION_EXACT`:
> 23/23 functions, 23/23 size-identical, 22/23 byte-identical, 46/46 imports,
> 47/47 identical CRCs).  Everything that phase *disproved* about the naive
> family assumption is summarised at the end of this section.

* Function-name overlap with `aw36518.ko` is only the 4 framework-generic names
  (`init_module`, `cleanup_module`, `aw36515_flash_open`,
  `aw36515_flash_release` counterparts); everything else is prefixed
  `aw36515_`.
* It has **two** LED channels: `aw36515_led0_get_ctrl/led0_set_ctrl` **and**
  `aw36515_led1_get_ctrl/led1_set_ctrl`, plus an out-of-line
  `aw36515_set_ctrl` and `aw36515_subdev_init`.
* It has **no** `aw36515_init`, `aw36515_parse_dt`, `aw36515_suspend`,
  `aw36515_resume`, `aw36515_ioctl`-adjacent PM pair identical to AW36518:
  imports show it lacks `pm_runtime_force_suspend/resume`.
* Import delta vs `aw36518.ko`: it *adds* `flashlight_pt_is_low`,
  `fortify_panic`, `strnlen`; it *lacks* `is_yft_cts_board`,
  `pm_runtime_force_suspend`, `pm_runtime_force_resume`.
* It is the only one of the three whose DT node carries `flash-externel` and
  media-graph endpoints, i.e. it is the primary camera flash.

**Conclusion (verified):** AW36515 is a *sibling Awinic driver from the same
code family* (same author, same MediaTek flashlight + V4L2 skeleton, same
regmap config — the 328-byte `regmap_config` blob is byte-identical across all
three) but a dual-channel implementation that calls `flashlight_pt_is_low()`
directly.  It got its own RED and reconstruction pass, and that pass confirmed
the warning above was justified: **almost none of the AW36518 electrical
constants carry over.**

| quantity | AW36518 / V2 | AW36515 |
|---|---|---|
| channels | 1 | 2 |
| flash current | 2940 µA + 5870 µA/LSB, max 1 499 790 µA, reg `0x03` | 3910 µA + 7830 µA/LSB, max 2 000 560 µA, regs `0x03`/`0x04` |
| torch current | 750 µA + 1510 µA/LSB, max 385 800 µA, reg `0x05` | 980 µA + 1960 µA/LSB, max 500 780 µA, regs `0x05`/`0x06` |
| enable mask | `0x03` (both bits at once) | `0x01` / `0x02` (per channel) |
| timeout | `0x08[3:0] = ms/40`, init 400 ms | identical encoding, init 400 ms |
| cooling | max_state 4, `{150000,100000,50000,25000}` µA | max_state 5, `{200000,150000,100000,50000,25000}` µA |
| `FLASH_IOC_SET_ONOFF` on | 250 000 µA | 80 000 µA |
| strobe source values | `0x0C` sw / `0x20` hw (mask `0x2C`) | identical |
| fault decode of `0x0A` | bit0/bit2/bit4|bit5 | identical |
| external strobe GPIO | none on the node | `flash-externel = <&pio 116 0>`, driven by `STROBE` |
| PM | `dev_pm_ops` + suspend/resume | none at all |
| low-battery path | relies on `fl_enable()` name bypass in `flashlight.ko` | calls `flashlight_pt_is_low()` itself *and* has no name bypass |
| logging | `printk(KERN_ERR "aw36518[%s] " …)` on nearly every path, 63 strings | almost none: 5 log sites, 24 strings |

Only the timeout encoding, the strobe-source values, the fault decode and the
`regmap_config` survived unchanged — every current, every maximum, the cooling
ladder and the ioctl operating point are different.

## Reusable results for the sibling passes

* Log-string ABI (`printk(KERN_ERR "aw365xx[%s] " fmt, __func__, …)` plus the
  plain `pr_info`/`printk` exceptions) — identical string layout in all three.
* Register semantics 0x01/0x03/0x05/0x07/0x08/0x0A and the µA↔code linear maps.
* MediaTek flashlight `flashlight_operations` shape and ioctl handling.
* Thermal cooling device structure (AW36518/V2 use a 4-entry µA limit table,
  AW36515 a 5-entry one).
* The build harness: `//lieppos/aw36518-recon/providers/flashlight` produces the
  real `flashlight.ko` `Module.symvers` needed by all three modules.  It is now
  built with `CONFIG_MTK_FLASHLIGHT_PT=1` as well, so it really exports
  `flashlight_pt_is_low` (`0xe39abd31`) for AW36515; the two CRCs the AW36518
  pair consumes are unchanged.
* The `reg` sysfs store uses **one 2-element `u32` array**, not two scalars —
  recovered on AW36515 from the `orr xN, sp, #0x4` addressing form and then
  applied to AW36518/V2, where it also produced a byte-identical `reg_store`.

### What the AW36515 pass added back to the family record

1. **Struct layout.** All three modules share a vendor `struct aw365xx_flash`
   with 24 bytes (three pointer-sized members) between `dnode[]` and
   `flash_dev_id[]` that no instruction ever touches.  AW36518/V2:
   `sizeof = 0x308`, `dnode[0] @ +0x278`, `flash_dev_id[0] @ +0x298`,
   `cdev @ +0x2d0`.  AW36515 (two-element arrays): `sizeof = 0x568`,
   `dnode[0] @ +0x4a0`, `flash_dev_id[0] @ +0x4c8`, `cdev @ +0x530`.
   Reproducing the gap is what unlocked byte-identity in all three.
2. **A public donor exists for AW36515 too**, in the same repository and the
   same commit as the AW36518 donor:
   `MotorolaMobilityLLC/kernel-mtk@ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de`,
   `drivers/misc/mediatek/flashlight/v4l2/aw36515.c`.  It is a *different file*,
   not a copy of the AW36518 one.
3. **`fl_enable()` in stock `flashlight.ko` names only the AW36518 pair.**
   The string `aw36515` does not occur anywhere in `flashlight.ko`, so the
   Ulefone low-battery bypass applies to AW36518/AW36518_V2 only.
4. **DT indexing crosses on AW36515**: `subdev_init()` binds children by `reg`
   while the flashlight registration loop assigns `channel`/name by DT order,
   and this DTB lists `flash@1` before `flash@0`.  See
   `phase4-aw36515-dt-contract.md`.
5. **Toolchain** is the identical `clang 17.0.2 (+pgo, +bolt, +lto)` string in
   all three stock modules, so Kleaf rebuilds keep a small scheduling residue.
