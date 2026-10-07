# USB-CHARGER-INTEGRATION — closure (2026-10-07, static)

Workspace component `Reverse Engineer - PARTIAL/USB-CHARGER-INTEGRATION` → **DONE**.

## Scope

The charger arbitration core that joins USB, PD and the power path:
* `charger_class`: charger device ABI, including the YFT `is_otg_enabled` op;
* `mtk_chg_type_det`: BC1.2/Type-C type detection;
* `mtk_charger_framework`: `mtk-master-charger`, basic/pulse charger,
  adapter switch.

Neighbours are all DONE: MT6375-CHARGER, PD-PPS-UFCS, TCPC/USB-TYPEC,
EXTERNAL-USB and INTERNAL-THERMAL-USB.

## Result

| module | functions | whole file vs stock (stripped) |
|---|---|---|
| mtk_charger_framework | 130/130, data 84/84 | **identical except build-id** |
| charger_class | 90/90 | identical except build-id and `srcversion` |
| mtk_chg_type_det | 8/8 | identical except build-id and `srcversion` |

B1==B2 for all three (`parity/b1-b2-build.txt`). Integration 7/7
(`evidence/integration-checks.txt`).

The new fix in this pass is in **`mtk_charger_framework`**. The earlier
"130/130" claim was function-level only. The whole file differed in size
(+120 B stock), in section order, and by 1 in `__COUNTER__`. Two changes make
it identical except the build-id (KDM commit `ca8b550`):
* `yft_cam_open_flag` is defined and exported in `mtk_basic_charger.c`;
* `yft_long_charger_flag` is defined first in `mtk_charger.c`, before
  `__chg_cmdline`.

**Declared residual: `srcversion`.** It is the sumversion MD4 of the source
tokens with comments and whitespace removed. For `charger_class` it covers
`charger_class.c` + `charger_class.h`; for `mtk_chg_type_det` it also covers
`mtk_charger.h`, `adapter_class.h`, `mtk_charger_algorithm_class.h` and
`mtk_smartcharging.h`.
* `srcversion` does not affect code, data or ABI.
* The exact YFT header and `.c` token stream (where the `is_otg_enabled`
  extern goes, enum and empty-`#if` remnants) cannot be recovered from the
  binary.
* A bounded search found no match. It covered 1 376 local variants plus
  public ALPS/Nothing/Volla/Xiaomi revisions of the header and `.c`.
* There is precedent: TKCORE-DRV and USB-TYPEC/rt_pd_manager were closed
  with the same residual.

## Integration contract (static)

* `/charger` (`mediatek,charger`) and `/mtk-ctd` (`mediatek,mtk_ctd`) are in
  DT. Load order is `charger_class` → `mtk_chg_type_det` /
  `mtk_charger_framework`.
* YFT hooks exported by the framework:
  * `yft_cam_open_flag` is consumed by `imgsensor` and `charger_cooling`. It
    limits charging while a camera is open (basic charger path).
  * `yft_long_charger_flag` is consumed by `charger_cooling`.
  * All consumer CRCs are equal.
* `charger_class` exports 85 symbols, including `charger_dev_is_otg_enabled`.
  Every stock consumer import CRC equals the export.
* Live: `mtk-master-charger` advertises `SDP DCP CDP PD PD_PPS`.
* Cross-layer routing:
  * USB data/role: EXTERNAL-USB.
  * Thermal-camera USB session (`yft_usb_flag`): MT6375-CHARGER and
    INTERNAL-THERMAL-USB.
  * PD/PPS: PD-PPS-UFCS.

## Boundaries

Runtime protocol traces, current limits under load and replacement validation
are integration/physical work.
