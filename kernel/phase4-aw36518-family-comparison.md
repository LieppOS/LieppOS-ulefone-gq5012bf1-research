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

**Conclusion:** AW36515 is a *sibling Awinic driver from the same code family*
(same author, same MediaTek flashlight + V4L2 skeleton, same regmap style) but a
dual-channel implementation that still calls `flashlight_pt_is_low()` directly.
It needs its own RED/reconstruction pass; the register/level/timeout semantics
recovered here are a strong starting hypothesis but **must be re-proved against
its own binary** (different chip, different channel count).

## Reusable results for the sibling passes

* Log-string ABI (`printk(KERN_ERR "aw365xx[%s] " fmt, __func__, …)` plus the
  plain `pr_info`/`printk` exceptions) — identical string layout in all three.
* Register semantics 0x01/0x03/0x05/0x07/0x08/0x0A and the µA↔code linear maps.
* MediaTek flashlight `flashlight_operations` shape and ioctl handling.
* Thermal cooling device structure and the 4-entry µA limit table.
* The build harness: `//lieppos/aw36518-recon/providers/flashlight` produces the
  real `flashlight.ko` `Module.symvers` needed by all three modules.

### Specifically for the upcoming `aw36515.ko` pass

Evidence gathered while doing V2 that should shorten the AW36515 work:

1. **Struct layout.** The vendor `struct aw365xx_flash` carries 24 bytes (three
   pointer-sized members) between `dnode[]` and `flash_dev_id[]` that no
   instruction ever touches.  On AW36518/V2 this makes
   `sizeof(*flash) = 0x308` with `dnode[0] @ +0x278`, `flash_dev_id[0] @ +0x298`,
   `cdev @ +0x2d0`.  Reproducing that gap raised byte-identical functions from
   6 → 12 in both modules; expect the same trick to matter for AW36515, whose
   arrays are `[2]` (so re-measure its `devm_kzalloc` size and field offsets
   instead of copying these numbers).
2. **Logging shim.** `printk(KERN_ERR "aw36515[%s] " fmt, __func__, …)` for the
   tagged records, plain `pr_info()`/`printk()` for the few untagged ones —
   re-derive the exact split from its own `.rodata.str1.1`.
3. **Toolchain.** All three stock modules carry the identical
   `Android (10087095, +pgo, +bolt, +lto, -mlgo, based on r487747c) clang 17.0.2`
   comment, so the residual scheduling differences seen here (Kleaf builds
   without the vendor's PGO/BOLT profile) will reappear and are expected.
4. **PT path differs.** AW36515 calls `flashlight_pt_is_low()` itself, while
   AW36518/V2 rely on the Ulefone `fl_enable()` name-match bypass in
   `flashlight.ko` (`strncmp(name, "aw36518-led0", 12)` /
   `"aw36518_v2-led0", 15`).  Check whether `fl_enable()` also names
   `aw36515-led0/1`; if not, AW36515 goes through the normal low-battery cut-off.
5. **Providers.** AW36515 imports `flashlight_pt_is_low` in addition to the two
   flashlight symbols and does **not** import `is_yft_cts_board`, so the same
   `flashlight_provider` target supplies all of its vendor CRCs; `fortify_panic`
   and `strnlen` are GKI symbols.
6. **DT.** `aw36515@63` is the only node of the three with `flash-externel` and
   with media-graph endpoints (`mtk-composite-v4l2-1` ports 0/1), and it uses
   `part = 0` with `ct = 0/1` — i.e. it is the main-camera pair while
   AW36518/V2 are the `part = 1` pair.
