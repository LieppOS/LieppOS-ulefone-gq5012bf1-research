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

**Conclusion:** `aw36518_v2.ko` is the *same vendor source file* built with the
name macro changed to `aw36518_v2` and the `is_yft_cts_board()` CTS skip
compiled out.  Reconstructing it from the source produced in this phase is a
mechanical rename plus removing one call — no new RE is required.  (The
LieppOS reconstruction source is written so the tag string, the compatible, the
sub-device name and the CTS hook are the only chip-identity knobs.)

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
