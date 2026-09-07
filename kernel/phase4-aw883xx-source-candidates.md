# Phase 4 — source-candidate search for aw883xx_driver.ko

Search order was local first, then public, exactly as required.

## 1. Local trees searched

| tree | result |
|---|---|
| `~/kernel-work/gki-12901745-workspace/common` (exact GKI 12901745) | no `aw88*` / `awinic` audio codec source |
| `~/kernel-work/vendor-reference/MiCode-MTK-kernel-device-modules-chagall-2.0.31` | no `AW883XX`, no `aw883xx_i2c_probe` |
| `~/kernel-work/vendor-reference/MiCode-bsp-klee-w-oss` | none |
| `~/kernel-work/vendor-reference/MiCode-dash-w-oss` | none |
| `kernel-research/nothing-mt6878/device_modules` (NothingOSS MT6878) | has `sound/soc/codecs/aw882xx/` (**different family**) and `sound/soc/mediatek/common/mtk-sp-spk-amp.{c,h}` — used as the reference for the MTK speaker-amp glue contract, not as a driver donor |
| `kernel-research/nothing-mt6878/kernel` | only `leds-aw2013`, `aw8738` — unrelated Awinic parts |
| GQ5012BF1 stock image | no source, only the `.ko` |

The NothingOSS `mtk-sp-spk-amp.c` was still valuable: it proves the
`mtk_spk_list[].i2c_probe` dispatch pattern and the `"speaker_amp"` /
`"mediatek,speaker_amp"` naming that the Ulefone build uses (the Ulefone build
calls `aw883xx_i2c_probe`/`aw883xx_i2c_remove` directly rather than through the
table, and adds an `.i2c_remove` hook that the Nothing revision lacks).

## 2. Local candidate that matched

```
kernel-research/aw883xx
  origin  https://github.com/awinic-driver/aw883xx
  commit  4f52a10  "ASoc: codecs: Add aw883xx amplifier driver"
  parent  dcb236b  "Initial commit"
  version AW883XX_DRIVER_VERSION "v1.6.0"   (aw883xx.c:48)
```

This is the vendor's own published driver drop. Files:

```
aw883xx.c aw883xx.h aw883xx_bin_parse.{c,h} aw883xx_calib.{c,h}
aw883xx_data_type.h aw883xx_device.{c,h} aw883xx_init.c aw883xx_log.h
aw883xx_monitor.{c,h} aw883xx_spin.{c,h}
aw883xx_pid_2049_{init.c,reg.h} aw883xx_pid_2066_{init.c,reg.h}
aw883xx_pid_2183_{init.c,reg.h}
```

### Match strength before any modification

| metric | value |
|---|---|
| stock defined `.text` functions | 236 |
| donor function names covering them | **233** by name |
| the other 3 | `aw883xx_i2c_remove` (donor has it, my extractor's regex missed the `#if`-split definition), `snd_soc_kcontrol_component` and `snd_soc_component_get_drvdata` (outlined ASoC header inlines) |
| stock `.rodata.str1.1` strings | 991 |
| strings absent from the donor source | **23**, of which 18 are `AWINIC_BIN_ERR`-macro concatenations that *are* present (my naive substring test split them), 2 are `__fortify_*`/`strnlen` compiler artifacts, leaving **3 real deltas**: `v1.7.1`, `aw_dev_parse_scene_v_1_0_0_0`, `no valid device scenario resolved` |

Classification: **`SAME_VENDOR_DIFFERENT_REVISION`** — same code base,
stock is `v1.7.1`, donor is `v1.6.0`.

## 3. Public search for the exact v1.7.1 drop

Queries run (web search + direct repo fetch):

* `AW883XX_DRIVER_VERSION "v1.7.1"` — no hit.
* `awinic-driver aw883xx v1.7.1` — only the two known Awinic repos.
* `github aw883xx_driver aw883xx.c v1.7.1 smartpa acf bin` — no hit.
* grep.app API for `AW883XX_DRIVER_VERSION` — HTTP 429 (Vercel challenge).
* searchcode API — HTTP 404 (endpoint retired).

Repos actually fetched and inspected:

| repo | version | verdict |
|---|---|---|
| `github.com/awinic-driver/aw883xx` @ `4f52a10` | v1.6.0 | **selected donor** |
| `github.com/awinic-driver/aw883xx_patch` @ `bd414f9` | v1.3.0 | older; mainline-submission patch set + `awinic,aw883xx.yaml` binding. Useless as a donor, but confirms the upstream lineage. |
| LineageOS `android_kernel_ayn_cq8725s-modules` `qcom/opensource/audio-kernel/asoc/codecs/aw883xx` | v1.5.0 | older, QCOM-flavoured |

No public `v1.7.1` drop exists. The reconstruction therefore proceeds as a
**delta reconstruction from v1.6.0**, with every v1.6.0→v1.7.1 difference
derived from the stock binary itself (see `RED.md`).

## 4. What was NOT used

* No `aw882xx` code was borrowed — different register maps, different ACF
  layout, different calibration ABI.
* No mainline `sound/soc/codecs/aw88395/` code was borrowed — mainline has a
  different structure and does not carry the v1.7.x vendor deltas.
* No CRC, register meaning, calibration constant or DSP command was invented.
  Everything not present in the donor was recovered from the stock
  disassembly and is cited in `RED.md`.
