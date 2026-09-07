# Phase 7 — calibration and speaker-protection contract

All statements below are derived from static analysis of the stock
`aw883xx_driver.ko` and from the reconstruction, which is byte-identical to the
stock module for every function in this document. **No calibration was executed,
no amplifier register was written, and no persistent audio data was touched.**

## Quantities the driver handles

| quantity | where it lives | units | how obtained |
|---|---|---|---|
| `cali_re` (Re25 / DC resistance) | `aw_cali_desc.cali_re` (RAM) | mOhm | measured by the on-chip DSP, read back through `dsp_re_desc` |
| `r0` (real-time resistance) | computed | mOhm | `aw_cali_svc_get_dev_r0` → `ops.aw_get_r0` (`aw_pid_2049_get_convert_r0`) |
| `te` (coil temperature delta) | `cali_desc` | raw | `aw883xx_cali_get_te`, needs `coil_alpha` from DSP |
| `f0` | `aw_cali_desc.f0` | Hz | `f0_desc.dsp_reg` (`AW_PID_2049_DSP_REG_RESULT_F0`), shifted |
| `q` | `aw_cali_desc.q` | Q×1000 | `q_desc.dsp_reg` (`AW_PID_2049_DSP_REG_RESULT_Q`) |
| `ra` | `aw_cali_desc.ra` | mOhm | `ra_desc.dsp_reg` = `AW_PID_2049_DSP_REG_CFG_ADPZ_RA`, 32-bit, `AW_DSP_RE_TO_SHOW_RE` shift |
| `vmax` | `monitor_desc.vmax_desc` | raw | monitor table; read + written during protection stepping |
| `re` bounds | `aw_dev->re_range` | mOhm | DT `re-min = 1000`, `re-max = 40000` (this device) |
| calibration status | `cali_desc.cali_result` | enum | `CALI_RESULT_NONE/NORMAL/ERROR` |

Error sentinels: `AW_ERRO_CALI_RE_VALUE = 0`, `AW_ERRO_CALI_F0_VALUE = 2600`
(the driver logs `get iv data failed, set default f0: 2600 q: 2600`).

## Interfaces that expose calibration

### 1. miscdevice `/dev/aw_smartpa` (`misc_cali`, `aw_cali_misc_fops`)

`unlocked_ioctl` / `compat_ioctl`, magic `'a'`:

| ioctl | nr | payload | classification |
|---|---|---|---|
| `AW_IOCTL_GET_F0` | 5 | `int32_t` | **READ_ONLY** (runs an f0 measurement, see below) |
| `AW_IOCTL_SET_CALI_RE` | 6 | `int32_t` | **DSP_PARAMETER_WRITE** + **HARDWARE_REGISTER_WRITE** |
| `AW_IOCTL_GET_RE` | 17 | `int32_t` | READ_ONLY |
| `AW_IOCTL_GET_CALI_F0` | 18 | `int32_t` | READ_ONLY |
| `AW_IOCTL_GET_REAL_R0` | 19 | `int32_t` | READ_ONLY |
| `AW_IOCTL_GET_TE` | 20 | `int32_t` | READ_ONLY |
| `AW_IOCTL_GET_RE_RANGE` | 21 | `struct re_data` | READ_ONLY |

`write()` accepts an ASCII command from `cali_str[]`:
`none start_cali cali_re cali_f0 store_re show_re show_r0 show_cali_f0 show_f0
show_te dev_sel get_ver get_re_range`, plus `dev_sel:dev[%u]` device selection.
`read()` returns the result of the last command.

### 2. sysfs on `/sys/bus/i2c/devices/6-0034/`

| attribute | mode | classification |
|---|---|---|
| `cali_re` | RW | read: READ_ONLY; write: **VOLATILE_WRITE + DSP_PARAMETER_WRITE** |
| `cali_f0` | R (store triggers a measurement) | **HARDWARE_REGISTER_WRITE** (drives white noise) |
| `cali_f0_q` | R | **HARDWARE_REGISTER_WRITE** |
| `cali_time` | RW | VOLATILE_WRITE (measurement dwell, min guard `time:%d is too short, no set`) |
| `re_range` | R | READ_ONLY |
| `dsp_re` | R | READ_ONLY (`read dsp re fail`) |
| `spk_temp` | R | READ_ONLY |
| `dsp`, `dsp_rw`, `reg`, `rw`, `awrw` | RW | **HARDWARE_REGISTER_WRITE / DSP_PARAMETER_WRITE** — raw register and DSP debug windows, guarded by `aw_pid_2049_check_rd_access` / `aw_pid_2049_check_wr_access` |
| `dbg_prof` | RW | VOLATILE_WRITE (forces a profile) |
| `fade_en`, `fade_step`, `phase_sync`, `i2c_log_en`, `monitor`, `monitor_update` | RW | VOLATILE_WRITE |
| `drv_ver` | R | READ_ONLY |

### 3. class `/sys/class/smartpa/`

`cali_time` (RW), `re25_calib` (RW), `f0_calib` (R), `f0_q_calib` (R),
`re_range` (R) — the same operations, applied to all registered devices
(`AW_CALI_ALL_DEV = 0xFFFFFFFF`) rather than one.

Gated by DT: `aw-cali-check` (absent here ⇒ ` cali-check get failed ,default turn
off`) and `aw-cali-mode`. With `AW_CALI_MODE_NONE` the attribute/class/misc
front-ends are still created but the service layer logs `cali mode is NONE`.

## What a calibration run actually does

`aw_cali_svc_cali_re(aw_dev, is_single, flag)` (Re / Re25):

1. `aw_cali_svc_cali_mode_enable(..., CALI_TYPE_RE, flag)` — with
   `CALI_OPS_HMUTE` it asserts hardware mute (`mute_desc`, SYSCTRL `HMUTE`).
2. Saves the current DSP calibration config (`aw_cali_svc_get_cali_cfg`, four
   32/16-bit DSP words: `actampth`, `noiseampth`, `ustepn`, `alphan`) and writes
   the calibration variant (`aw_cali_svc_set_cali_cfg`).
3. Waits `g_cali_re_time`. **The stock default is 1000 ms, not the 3000 ms of
   the public v1.6.0 driver** — the `g_cali_re_time` initialiser at `.data+0x1e8`
   is `0x000003e8`. It is scaled by `AW_CALI_DELAY_CACL(v) = v*32/48`.
4. Reads Re `AW_CALI_READ_CNT_MAX = 8` times, discards `AW_CALI_DATA_SUM_RM = 2`
   extremes (`aw_cali_svc_del_max_min_ave_algo`, `aw_cali_svc_bubble_sort`) and
   averages (`aw_cali_svc_get_smooth_cali_re`).
5. Range-checks against `re_range` (1000…40000 mOhm here); out-of-range values
   are rejected: `out range re value: [%d]mohm`, `invalid cali re %d!`,
   `cali_re:%d out of range, no set`.
6. Restores the saved DSP cali config and un-mutes.

`aw_cali_svc_cali_f0_q(aw_dev, is_single, CALI_OPS_NOISE)` (f0 / Q):

1. `aw_cali_svc_set_white_noise(aw_dev, true)` — programs the DSP noise
   generator (`noise_desc.dsp_reg` = `AW_PID_2049_DSP_REG_CFG_MBMEC_GLBCFG`,
   `AW_PID_2049_DSP_REG_NOISE_MASK`) and runs the DSP volume ramp
   (`aw_cali_svc_cali_run_dsp_vol`); **this drives an audible test signal**.
2. Waits `AW_CALI_F0_TIME = 5000 ms`, reads f0/q up to `F0_READ_CNT_MAX = 5`.
3. Turns the noise generator off and restores volume.

`aw883xx_cali_set_cali_re()` writes the value both to the chip
(`ops.aw_set_cali_re` = `aw_pid_2049_set_cali_re_to_dsp`, DSP register
`AW_PID_2049_DSP_REG_CFG_ADPZ_RE`) and to `cali_desc.cali_re` in RAM.

## Persistence — the kernel does NOT store calibration

The public Awinic v1.6.0 driver has an `AW_CALI_STORE_EXAMPLE` block that
persists Re to `/mnt/vendor/persist/factory/audio/aw_cali.bin` with
`filp_open`/`kernel_read`/`kernel_write`. **That block is compiled out of the
stock GQ5012BF1 module.** Evidence:

* the stock `__versions` table contains no `filp_open`, `filp_close`,
  `kernel_read`, `kernel_write` or `skip_spaces`;
* the string `/mnt/vendor/persist/factory/audio/aw_cali.bin` does not exist in
  `.rodata.str1.1`;
* there is no `aw_cali_write_re_to_nvram` symbol;
* `aw_cali_store_cali_re()`'s "write re to nvram failed!" error path is absent
  from `aw_cali_misc_ops` and `aw_cali_svc_set_devs_re_str`.

Calibration state in the kernel is therefore **volatile**: it lives in
`aw_cali_desc` and is re-applied to the chip on every `aw883xx_device_start()`
via `aw_dev_init_re_update()`.

Persistence is owned by userspace, in MTK NVRAM:

```
/mnt/vendor/nvdata/APCFG/APRDCL/smartpa_calib
iAP_CFG_CUSTOM_FILE_SMARTPA_CALIB_LID
consumers: /vendor/bin/smartpa_nvtest, /vendor/lib64/libcustom_nvram.so,
           /vendor/lib64/libaudiosmartpamtk.so
```

The SKTune effect (`/vendor/lib64/hw/awinic.audio.effect.so`) applies its own
range guard (`set cail re out of range(%d, %d)!`) and combines the stored value
with `ra` (`Algo cali re = set cali re + ra = %d + %d = %d mOhm`).

## Safety classification summary

| operation | classification | reachable from |
|---|---|---|
| read Re/R0/F0/Q/Te/temperature/vmax/registers | `READ_ONLY` | ioctl 17–21, sysfs read, class read |
| set `cali_time`, `fade_*`, `dbg_prof`, `monitor*`, `i2c_log_en` | `VOLATILE_WRITE` | sysfs write |
| write `cali_re` / `re25_calib` / ioctl 6 | `DSP_PARAMETER_WRITE` (`CFG_ADPZ_RE`) | ioctl 6, sysfs, class |
| run Re calibration (`start_cali`, `cali_re`) | `HARDWARE_REGISTER_WRITE` + `DSP_PARAMETER_WRITE` (mute + DSP cali cfg swap) | misc `write()`, sysfs `cali_re` store, class `re25_calib` store |
| run F0/Q calibration (`cali_f0`) | `HARDWARE_REGISTER_WRITE` + `DSP_PARAMETER_WRITE` + **drives white noise into the speaker** | misc `write()`, sysfs `cali_f0`/`cali_f0_q`, class `f0_calib` |
| `reg`/`rw`/`dsp_rw`/`awrw` debug windows | `HARDWARE_REGISTER_WRITE` / `DSP_PARAMETER_WRITE` | sysfs write (`dsp` is read-only) |
| profile/firmware download at `device_start` | `HARDWARE_REGISTER_WRITE` + `DSP_PARAMETER_WRITE` — **required for normal playback**, not gated | probe / DAI startup |
| boost-voltage / IPEAK / gain / vmax stepping by the monitor | `HARDWARE_REGISTER_WRITE` — **required for protection**, not gated | monitor work |
| persistent calibration write | `PERSISTENT_CALIBRATION_WRITE` | **not present in this driver** — userspace/NVRAM only |
| OTP / eFuse write | none | the driver only *reads* `EFRH/EFRM/EFRL` for vcalb; there is no efuse write path |

## Deliberate safety gates in the LieppOS reconstruction

Two build-time gates were added. Both default to the stock behaviour being
**enabled**, i.e. they change nothing unless explicitly flipped:

* `AW_ALLOW_CALIBRATION_WRITES` (default 1) — guards the calibration *run*
  entry points (`aw_cali_svc_cali_re`, `aw_cali_svc_cali_f0_q`) and the
  `set_cali_re` path.
* `AW_ALLOW_FACTORY_MODE` (default 1) — guards the four *writable* raw
  register/DSP debug attributes (`reg_store`, `rw_store`, `dsp_rw_store`,
  `awrw_store`). The `dsp` attribute is show-only in the stock module and needs
  no gate.

Ordinary playback initialisation — profile/firmware download, PLL/SYSST/DSP
checks, mute/unmute, power sequencing and monitor protection — is **not** gated,
because the stock evidence proves it is required for normal operation.

See `RED.md` §Deviations for the exact list.
