# Recommended next independent family

Remaining uncertified groups, excluding PLATFORM-BATCH-04 (charging/USB) and this batch, measured on
the frozen baseline:

| Group | Uncertified | Notes |
|---|---:|---|
| PRESERVE:CONNECTIVITY | 17 | bluetooth, bt_drv_6878, cfg80211, connadp, connfem, conninfra, connscp, fmradio_drv_connac2x, … |
| PRESERVE:MODEM | 16 | ccci_* and c2k_*; also providers for `snd-soc-mtk-common` (2 symbols) |
| met_drv_v3 | 10 | debug-only |
| PRESERVE:DISPLAY-GLUE | 8 | |
| PRESERVE:SENSOR-HUB | 3 | **`scp.ko`**, sensorhub, hf_manager |

**Recommendation: SCP-CONNECTIVITY-BATCH-01 = SENSOR-HUB (3) + CONNECTIVITY (17) = 20 modules.**

- `scp.ko` is the largest uncertified provider behind the audio boundary (13 symbols). Its export CRCs
  and KCFI words are already reproduced from ALPS source (`PROVIDER-BOUNDARIES.tsv`), so source is
  likely complete.
- `connscp`/`conninfra` depend on SCP, and FM radio pairs with the ACCDET FM-antenna switch closed here.
- The group does not overlap charging/USB/Type-C. Reuse this repository's engine (bootstrap, scope,
  witness, verify, residual, mutation, cleancheck) with a new owned set.

Do this before MODEM: the modem stack carries more proprietary boundary and needs separate care for
CCCI/firmware.
